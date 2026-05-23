from django.db import models

class Parameter(models.Model):
    value = models.FloatField() #f(x)
    timestamp = models.DateTimeField(auto_now_add=True) #x
    class Meta:
        ordering = ['-timestamp']
