from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from habits.models import Habit
from datetime import date

class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        today = date.today()

        habits = Habit.objects.filter(
            start_date__lte=today,
            end_date__gte=today,
            status='Pending'
        )

        for habit in habits:

            send_mail(
                'Daily Habit Reminder',
                f'''
Hello {habit.user.username},

Reminder for your habit:

Habit: {habit.name}

Description:
{habit.description}

Today is your scheduled habit day.
Please complete it.

Start Date: {habit.start_date}
End Date: {habit.end_date}

Good Luck!
                ''',
                'yourgmail@gmail.com',
                [habit.user.email],
                fail_silently=False,
            )

        self.stdout.write("Daily reminders sent")