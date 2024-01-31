from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

# Create your models here.
class Expense(models.Model):
    # Amount
    amount = models.FloatField()
    # Date field. Default set to now
    date = models.DateField(default=now)
    # Description
    description = models.TextField()
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    category = models.CharField(max_length=266)

    def __str__(self):
        return self.category

    class Meta:
        ordering: ['-date']

class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'


