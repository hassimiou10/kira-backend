from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    DeveloperAssistantPromptViewSet,
    GenerateCodeView,
    FixBugView,
    ExplainCodeView,
    ReviewCodeView,
)

router = DefaultRouter()
router.register(r"prompts", DeveloperAssistantPromptViewSet, basename="developerassistantprompt")

urlpatterns = [
    path("generate/", GenerateCodeView.as_view(), name="dev-generate-code"),
    path("fix-bug/", FixBugView.as_view(), name="dev-fix-bug"),
    path("explain/", ExplainCodeView.as_view(), name="dev-explain-code"),
    path("review/", ReviewCodeView.as_view(), name="dev-review-code"),
    path("", include(router.urls)),
]