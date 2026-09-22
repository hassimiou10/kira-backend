from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    EducationRecordViewSet,
    SummarizeCourseView,
    GenerateQuizView,
    GenerateFlashcardsView,
    ExplainConceptView,
    FlashcardListView,
    MasterFlashcardView,
)

router = DefaultRouter()
router.register(r"", EducationRecordViewSet, basename="educationrecord")

urlpatterns = [
    path('summarize/', SummarizeCourseView.as_view(), name='education-summarize'),
    path('quiz/', GenerateQuizView.as_view(), name='education-quiz'),
    path('flashcards/', GenerateFlashcardsView.as_view(), name='education-flashcards'),
    path('flashcards/list/', FlashcardListView.as_view(), name='education-flashcards-list'),
    path('flashcards/<uuid:pk>/master/', MasterFlashcardView.as_view(), name='education-flashcard-master'),
    path('explain/', ExplainConceptView.as_view(), name='education-explain'),
    path('', include(router.urls)),
]
