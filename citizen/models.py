from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Report(models.Model):
    """Garbage complaint report submitted by citizens."""

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
    )

    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )

    citizen = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submitted_reports',
    )
    assigned_worker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_reports',
    )
    worker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_reports',
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=300, help_text='Address or landmark')
    latitude = models.FloatField(
        validators=[
            MinValueValidator(-90),
            MaxValueValidator(90)
        ],
        null=True, blank=True
    )
    longitude = models.FloatField(
        validators=[
            MinValueValidator(-180),
            MaxValueValidator(180)
        ],
        null=True, blank=True
    )
    map_link = models.URLField(blank=True, null=True)
    image = models.ImageField(upload_to='report_images/', blank=True, null=True)
    completion_image = models.ImageField(upload_to='completed_reports/', blank=True, null=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    worker_notes = models.TextField(blank=True, null=True, help_text='Notes from the worker')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_status_display()}] {self.title} — {self.citizen.username}"

    @property
    def status_color(self):
        """Return Bootstrap color class based on status."""
        colors = {
            'pending': 'warning',
            'assigned': 'info',
            'in_progress': 'primary',
            'resolved': 'success',
            'rejected': 'danger',
        }
        return colors.get(self.status, 'secondary')

    @property
    def priority_color(self):
        """Return Bootstrap color class based on priority."""
        colors = {
            'low': 'success',
            'medium': 'info',
            'high': 'warning',
            'critical': 'danger',
        }
        return colors.get(self.priority, 'secondary')


class Feedback(models.Model):
    """Feedback submitted by citizens for completed reports."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    message = models.TextField()
    rating = models.IntegerField()  # 1 to 5 stars
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for {self.report.title} ({self.rating} stars) by {self.user.username}"
