from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom User model with role-based access."""

    ROLE_CHOICES = (
        ('citizen', 'Citizen'),
        ('worker', 'Worker'),
        ('admin', 'Admin'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='citizen')
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_citizen(self):
        return self.role == 'citizen'

    @property
    def is_worker(self):
        return self.role == 'worker'

    @property
    def is_admin_user(self):
        return self.role == 'admin'


class Notification(models.Model):
    """System notifications for users."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"To {self.user.username} - {self.message}"
