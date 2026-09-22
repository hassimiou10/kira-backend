from django.http import HttpResponse

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from . import services
from .models import CV
from .serializers import CVSerializer


ALLOWED_TEMPLATES = [
    "classic",
    "modern",
    "minimal",
    "elegant",
    "tech",
    "student",
]


class CVViewSet(viewsets.ModelViewSet):

    queryset = CV.objects.all()
    serializer_class = CVSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated:
            return CV.objects.filter(owner=user)

        return CV.objects.none()

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(owner=self.request.user)
        else:
            serializer.save()

    @action(
        detail=True,
        methods=["get"],
        permission_classes=[IsAuthenticatedOrReadOnly],
    )
    def pdf(self, request, pk=None):
        """
        Affiche le PDF du CV.

        URL :
        /api/cv/<id>/pdf/
        """

        cv = self.get_object()

        
        pdf_bytes = services.generate_pdf(cv)

        if not pdf_bytes:
            return Response(
                {
                    "status": "error",
                    "message": "Impossible de générer le PDF.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        cv.pdf = pdf_bytes
        cv.save(
            update_fields=[
                "pdf",
                "updated_at",
            ]
        )

        response = HttpResponse(
            pdf_bytes,
            content_type="application/pdf",
        )

        return response

    @action(
        detail=True,
        methods=["get"],
        permission_classes=[IsAuthenticatedOrReadOnly],
    )
    def download_pdf(self, request, pk=None):
        """
        Télécharge le PDF du CV.

        URL :
        /api/cv/<id>/download_pdf/
        """

        cv = self.get_object()

   
        pdf_bytes = services.generate_pdf(cv)

        if not pdf_bytes:
            return Response(
                {
                    "status": "error",
                    "message": "Impossible de générer le PDF.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        cv.pdf = pdf_bytes
        cv.save(
            update_fields=[
                "pdf",
                "updated_at",
            ]
        )

        filename = (
            f"{cv.full_name.replace(' ', '_')}_{cv.pk}.pdf"
            if cv.full_name
            else f"cv_{cv.pk}.pdf"
        )

        response = HttpResponse(
            pdf_bytes,
            content_type="application/pdf",
        )

        response["Content-Disposition"] = (
            f'attachment; filename="{filename}"'
        )

        return response

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[IsAuthenticated],
        url_path="generate/full",
    )
    def generate_full(self, request):
        """
        Génère un CV complet à partir d'une description.

        URL :
        POST /api/cv/generate/full/
        """

        description = (
            request.data.get("description")
            or request.data.get("prompt")
            or request.data.get("text")
            or ""
        )

        if not description.strip():
            return Response(
                {
                    "status": "error",
                    "message": "Description requise.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        template = request.data.get(
            "template",
            "modern",
        )

        if template not in ALLOWED_TEMPLATES:
            template = "modern"

        cv_data = services.generate_full_cv_from_description(
            description
        )

        full_name = (
            cv_data.get("full_name")
            or request.user.get_full_name()
            or request.user.username
        )

        serializer = self.get_serializer(
            data={
                "full_name": full_name,
                "email": request.user.email,
                "phone": cv_data.get("phone", ""),
                "summary": cv_data.get("summary", ""),
                "template": template,
                "data": cv_data,
            }
        )

        serializer.is_valid(raise_exception=True)

        cv = serializer.save(
            owner=request.user
        )

        return Response(
            {
                "status": "success",
                "message": "CV généré avec succès.",
                "template": template,
                "data": self.get_serializer(cv).data,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated],
        url_path="generate-summary",
    )
    def generate_summary(self, request, pk=None):
        """
        Génère un résumé professionnel pour un CV.

        URL :
        POST /api/cv/<id>/generate-summary/
        """

        cv = self.get_object()

        summary = services.generate_professional_summary(cv)

        cv.summary = summary
        cv.pdf = None

        cv.save(
            update_fields=[
                "summary",
                "pdf",
                "updated_at",
            ]
        )

        return Response(
            {
                "status": "success",
                "message": "Résumé professionnel généré.",
                "summary": summary,
                "data": self.get_serializer(cv).data,
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated],
        url_path="improve",
    )
    def improve(self, request, pk=None):
        """
        Améliore un CV existant avec l'IA.

        URL :
        POST /api/cv/<id>/improve/
        """

        cv = self.get_object()

        improved_data = services.improve_cv(cv)

        if isinstance(improved_data, dict):
            cv.data = improved_data

            if improved_data.get("full_name"):
                cv.full_name = improved_data["full_name"]

            if improved_data.get("email"):
                cv.email = improved_data["email"]

            if improved_data.get("phone"):
                cv.phone = improved_data["phone"]

            if improved_data.get("summary"):
                cv.summary = improved_data["summary"]

        cv.pdf = None

        cv.save(
            update_fields=[
                "data",
                "full_name",
                "email",
                "phone",
                "summary",
                "pdf",
                "updated_at",
            ]
        )

        return Response(
            {
                "status": "success",
                "message": "CV amélioré avec succès.",
                "data": self.get_serializer(cv).data,
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["patch"],
        permission_classes=[IsAuthenticated],
        parser_classes=[MultiPartParser, FormParser],
        url_path="photo",
    )
    def upload_photo(self, request, pk=None):
        """
        Upload ou remplace la photo de profil du CV.

        URL :
        PATCH /api/cv/<id>/photo/
        """

        cv = self.get_object()

        photo = request.FILES.get("photo")

        if not photo:
            return Response(
                {
                    "status": "error",
                    "message": "Aucune photo envoyée.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        cv.photo = photo
        cv.pdf = None

        cv.save(
            update_fields=[
                "photo",
                "pdf",
                "updated_at",
            ]
        )

        return Response(
            {
                "status": "success",
                "message": "Photo ajoutée avec succès.",
                "data": self.get_serializer(cv).data,
            },
            status=status.HTTP_200_OK,
        )

    def perform_update(self, serializer):
        """
        Lorsqu'un CV est modifié, on supprime l'ancien PDF
        afin qu'il soit régénéré avec les nouvelles données/template.
        """

        updated_cv = serializer.save()

        # Invalider l'ancien PDF.
        updated_cv.pdf = None

        updated_cv.save(
            update_fields=[
                "pdf",
                "updated_at",
            ]
        )
