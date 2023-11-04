from django.db import models
import random
import string
from django.utils.text import slugify
from django.contrib.auth.models import User


class DietPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, help_text='Name of the diet plan')
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            unique_slug = base_slug
            while DietPlan.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{generate_random_string()}"
            self.slug = unique_slug
        super().save(*args, **kwargs)

class Day(models.Model):
    diet_plan = models.ForeignKey(DietPlan, on_delete=models.CASCADE)
    day_number = models.PositiveIntegerField(help_text='Day number (1-7)')

class Meal(models.Model):
    day = models.ForeignKey(Day, on_delete=models.CASCADE)
    meal_type = models.CharField(max_length=10, choices=[
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner')
    ])
    description = models.TextField(help_text='Description of the meal')

def generate_random_string(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

