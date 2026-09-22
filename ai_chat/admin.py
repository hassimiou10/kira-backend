from django.contrib import admin
from .models import Conversation, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('role', 'content', 'created_at')
    can_delete = False


class ConversationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('title', 'user__username')
    inlines = [MessageInline]


class MessageAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'role', 'short_content', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('content',)

    def short_content(self, obj):
        return obj.content[:50]
    short_content.short_description = 'Contenu'


admin.site.register(Conversation, ConversationAdmin)
admin.site.register(Message, MessageAdmin)