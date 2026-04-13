from django.contrib import admin
from .models import User, UserProfile

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'username', 'balance', 'total_earned', 'total_withdrawn', 'is_verified', 'date_joined']
    list_filter = ['is_verified', 'date_joined']
    search_fields = ['email', 'username']
    readonly_fields = ['balance', 'total_earned', 'total_withdrawn', 'referral_code']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'country', 'city', 'completed_surveys', 'referral_earnings', 'created_at']
    list_filter = ['country', 'created_at']
    search_fields = ['user__email']
