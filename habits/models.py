from django.db import models
from django.contrib.auth.models import User



class Register(models.Model):

    username = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    gender = models.CharField(max_length=10)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.username


class Habit(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    name = models.CharField(
        max_length=200
    )

    description = models.TextField(
        blank=True
    )
    category = models.CharField(
    max_length=50,
    default="Health"
    )

    frequency = models.CharField(
    max_length=20,
    default="Daily"
    )

    reminder_time = models.TimeField(
    null=True,
    blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('Completed', 'Completed'),
        ],
        default='Pending'
    )

    start_date = models.DateField()

    end_date = models.DateField( null=True,
    blank=True)
    

    def __str__(self):
        return self.name
    
class HabitLog(models.Model):

    habit = models.ForeignKey(
        Habit,
        on_delete=models.CASCADE
    )

    log_date = models.DateField()

    completed = models.BooleanField(
        default=False
    )

    missed = models.BooleanField(
        default=False
    ) 
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["habit", "log_date"],
                name="unique_habit_log"
            )
        ]  
class Profile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    profile_pic = models.ImageField(
        upload_to='profile_pics/',
        default='default.png'
    )
    phone = models.CharField(
        max_length=10,
        unique=True,
        null=True,
        blank=True
    )

    gender = models.CharField(
        max_length=10,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.user.username    
class PasswordOTP(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    otp = models.CharField(
        max_length=6
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )  

from django.db import models

class Food(models.Model):

    FOOD_TYPES = [
        ("Fruit", "Fruit"),
        ("Vegetable", "Vegetable"),
        ("Grain", "Grain"),
        ("Protein", "Protein"),
        ("Dairy", "Dairy"),
        ("Nut", "Nut & Seeds"),
        ("Beverage", "Beverage"),
        ("Snack", "Snack"),
        ("Fast Food", "Fast Food"),
        ("Dessert", "Dessert"),
    ]

    MEAL_TYPES = [
        ("Breakfast", "Breakfast"),
        ("Lunch", "Lunch"),
        ("Dinner", "Dinner"),
        ("Snack", "Snack"),
        ("Any", "Any Time"),
    ]

    DIET_TYPES = [
        ("Veg", "Vegetarian"),
        ("Non-Veg", "Non Vegetarian"),
        ("Vegan", "Vegan"),
    ]

    GOALS = [
        ("Weight Gain", "Weight Gain"),
        ("Weight Loss", "Weight Loss"),
        ("Maintain", "Maintain"),
    ]
    HEALTH_SCORES = [
        (5, "⭐⭐⭐⭐⭐ Excellent"),
        (4, "⭐⭐⭐⭐ Good"),
        (3, "⭐⭐⭐ Average"),
        (2, "⭐⭐ Poor"),
        (1, "⭐ Avoid"),
    ]

    name = models.CharField(max_length=100)

    food_type = models.CharField(max_length=30, choices=FOOD_TYPES)

    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES)

    diet_type = models.CharField(max_length=20, choices=DIET_TYPES)

    goal = models.CharField(max_length=20, choices=GOALS)

    serving_size = models.CharField(max_length=50)

    calories = models.IntegerField()
    health_score = models.IntegerField(
        choices=HEALTH_SCORES,
        default=3
    )


    def __str__(self):
        return self.name

from django.db import models

class Medicine(models.Model):
    problem = models.CharField(max_length=200)
    medicine_name = models.TextField()
    dosage = models.CharField(max_length=200)
    precautions = models.TextField()
    symptoms = models.TextField()
    home_remedy = models.TextField()
    foods_to_eat = models.TextField()
    foods_to_avoid = models.TextField()
    consult_doctor = models.TextField()

    def __str__(self):
        return self.problem    

