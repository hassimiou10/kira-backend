from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/chat/', include('ai_chat.urls')),
    path('api/translate/', include('translator.urls')),
    path('api/documents/', include('documents.urls')),
    path('api/cv/', include('cv_generator.urls')),
    path('api/education/', include('education.urls')),
    path('api/dev/', include('developer_assistant.urls')),
    path('api/payments/', include('payments.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)