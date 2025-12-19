from django.db import models

class Game(models.Model):
    app_id = models.CharField(max_length=50, unique=True, help_text="Steam AppID")

    title = models.CharField(max_length=255)

    publisher = models.CharField(max_length=255, blank=True, default="")

    release_date = models.DateField(null=True, blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    description = models.TextField(null=True, blank=True)

    header_image = models.URLField(max_length=500, null=True, blank=True)
    genres = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title