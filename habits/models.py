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
    habit_time = models.TimeField()

    status = models.CharField(
        max_length=20,
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