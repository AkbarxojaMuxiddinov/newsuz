from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from django.contrib.admin.models import LogEntry

admin.site.register(User, UserAdmin)

@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display =  (
        "action_time",
        "user",
        "content_type",
        "object_repr",
        "action_flag",
    )
    list_filter = ("action_flag", "content_type")
    search_fields = ("user__username", "object_repr")
    ordering = ("-action_time",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
