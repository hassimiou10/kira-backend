from django.urls import path

from .views import DocumentListView, DocumentUploadView, DocumentQuestionView

urlpatterns = [
    path("", DocumentListView.as_view(), name="document-list"),
    path("upload/", DocumentUploadView.as_view(), name="document-upload"),
    path("<int:pk>/question/", DocumentQuestionView.as_view(), name="document-question"),
]