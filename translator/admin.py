from django.contrib import admin
from .models import Translation


class TranslationAdmin(admin.ModelAdmin):
    list_display = ('user', 'source_language', 'target_language', 'short_source', 'created_at')
    list_filter = ('source_language', 'target_language', 'created_at')
    search_fields = ('source_text', 'translated_text', 'user__username')

    def short_source(self, obj):
        return obj.source_text[:50]
    short_source.short_description = 'Texte source'


admin.site.register(Translation, TranslationAdmin)