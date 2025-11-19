# from django.contrib import admin

# from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# from .models import User, Conversation, Message


# @admin.register(User)
# class UserAdmin(BaseUserAdmin):
#     """
#     Custom admin for User model.
#     """
#     list_display = ['email', 'first_name', 'last_name', 'role', 'phone_number', 'created_at', 'is_active']
#     list_filter = ['role', 'is_active', 'created_at']
#     search_fields = ['email', 'first_name', 'last_name', 'phone_number']
#     ordering = ['-created_at']
    
#     fieldsets = (
#         (None, {'fields': ('email', 'password')}),
#         ('Personal Info', {'fields': ('first_name', 'last_name', 'phone_number')}),
#         ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
#         ('Important Dates', {'fields': ('last_login', 'created_at')}),
#     )
    
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('email', 'first_name', 'last_name', 'phone_number', 'role', 'password1', 'password2'),
#         }),
#     )
    
#     readonly_fields = ['created_at', 'last_login']


# @admin.register(Conversation)
# class ConversationAdmin(admin.ModelAdmin):
#     """
#     Admin interface for Conversation model.
#     """
#     list_display = ['conversation_id', 'get_participants_display', 'created_at', 'get_message_count']
#     list_filter = ['created_at']
#     search_fields = ['conversation_id', 'participants__email']
#     filter_horizontal = ['participants']
#     readonly_fields = ['conversation_id', 'created_at']
#     ordering = ['-created_at']
    
#     def get_participants_display(self, obj):
#         """Display first 3 participants."""
#         participants = obj.participants.all()[:3]
#         emails = [p.email for p in participants]
#         return ', '.join(emails)
#     get_participants_display.short_description = 'Participants'
    
#     def get_message_count(self, obj):
#         """Display message count."""
#         return obj.messages.count()
#     get_message_count.short_description = 'Messages'


# @admin.register(Message)
# class MessageAdmin(admin.ModelAdmin):
#     """
#     Admin interface for Message model.
#     """
#     list_display = ['message_id', 'sender', 'conversation', 'get_message_preview', 'sent_at']
#     list_filter = ['sent_at']
#     search_fields = ['message_id', 'sender__email', 'message_body']
#     readonly_fields = ['message_id', 'sent_at']
#     ordering = ['-sent_at']
    
#     def get_message_preview(self, obj):
#         """Display message preview."""
#         return obj.get_preview(50)
#     get_message_preview.short_description = 'Message Preview'
    
#     fieldsets = (
#         (None, {
#             'fields': ('message_id', 'conversation', 'sender')
#         }),
#         ('Content', {
#             'fields': ('message_body',)
#         }),
#         ('Metadata', {
#             'fields': ('sent_at',)
#         }),
#     )