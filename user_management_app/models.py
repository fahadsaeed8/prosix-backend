from django.db import models
from user_management_app.constants import ROLE_CHOICES, USER_STATUS_CHOICES
# Create your models here.


class UserProfile(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=255, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=25, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    user_status = models.CharField(max_length=255,  choices=USER_STATUS_CHOICES, default='pending')
    permission = models.JSONField(blank=True, null=True)
    logo = models.ImageField(upload_to='profile_logos/', blank=True, null=True)
    

    def __str__(self):
        return f"{self.user.username}'s Profile"

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'