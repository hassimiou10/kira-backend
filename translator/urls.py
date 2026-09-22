from django.urls import path
from .views import TranslationHistoryView, TranslateView

urlpatterns = [
    path('', TranslateView.as_view(), name='translate'),
    path('history/', TranslationHistoryView.as_view(), name='translation-history'),
]

