from django.contrib import admin
from .models import Register,Food

admin.site.register(Register)
@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "food_type",
        "meal_type",
        "diet_type",
        "goal",
        "serving_size",
        "calories",
       
    )

    search_fields = (
        "name",
    )

    list_filter = (
        "food_type",
        "meal_type",
        "diet_type",
        "goal",
    )

    ordering = (
        "name",
    )

    list_per_page = 25