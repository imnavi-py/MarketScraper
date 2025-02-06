from django.db import models

class MarketData(models.Model):
    title = models.CharField(max_length=255)
    title_link = models.URLField()
    text = models.TextField()
    image_url = models.URLField()
    paragraphs = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title