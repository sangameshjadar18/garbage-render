from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class GarbageBin(models.Model):
    """Physical garbage bin location and status."""

    STATUS_CHOICES = (
        ('empty', 'Empty'),
        ('half', 'Half Full'),
        ('full', 'Full'),
        ('overflow', 'Overflow'),
    )

    WASTE_TYPE_CHOICES = (
        ('e_waste', 'E-Waste'),
        ('eco_friendly', 'Eco-Friendly Waste'),
        ('mixed', 'Mixed Waste'),
    )

    location = models.CharField(max_length=300)
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
    waste_type = models.CharField(
        max_length=20,
        choices=WASTE_TYPE_CHOICES,
        default='mixed',
        help_text='Type of waste accepted by this bin'
    )
    capacity = models.PositiveIntegerField(
        default=1, 
        validators=[MinValueValidator(1)], 
        help_text='Fill level percentage (1-100)'
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='empty')
    assigned_worker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_bins',
        limit_choices_to={'role': 'worker'},
    )
    last_collected = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.get_waste_type_display()} bin at {self.location} ({self.get_status_display()})"

    @property
    def status_color(self):
        colors = {
            'empty': 'success',
            'half': 'info',
            'full': 'warning',
            'overflow': 'danger',
        }
        return colors.get(self.status, 'secondary')

    @property
    def waste_type_color(self):
        colors = {
            'e_waste': 'danger',
            'eco_friendly': 'success',
            'mixed': 'primary',
        }
        return colors.get(self.waste_type, 'secondary')
