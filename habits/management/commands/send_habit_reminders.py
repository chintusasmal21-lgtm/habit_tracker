
from datetime import date

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.core.mail import send_mail

from habits.models import Habit


class Command(BaseCommand):

    help = "Send users an email containing their habits scheduled for today."

    def handle(self, *args, **kwargs):

        # Get today's date
        today = date.today()

        # Monday = 0
        # Tuesday = 1
        # Wednesday = 2
        # Thursday = 3
        # Friday = 4
        # Saturday = 5
        # Sunday = 6
        today_weekday = today.weekday()

        self.stdout.write(
            f"Checking today's habits for {today}"
        )

        # Get users who have an email address
        users = User.objects.exclude(
            email__isnull=True
        ).exclude(
            email=""
        )

        total_emails = 0

        # Check each user
        for user in users:

            # Get habits that are active today
            habits = Habit.objects.filter(
                user=user,
                start_date__lte=today,
                end_date__gte=today,
            )

            today_habits = []

            # Check each habit
            for habit in habits:

                scheduled_today = False

                # Daily habit
                if habit.frequency == "Daily":
                    scheduled_today = True

                # Monday to Friday
                elif habit.frequency == "Weekdays":
                    if today_weekday < 5:
                        scheduled_today = True

                # Saturday and Sunday
                elif habit.frequency == "Weekends":
                    if today_weekday >= 5:
                        scheduled_today = True

                # Weekly habit
                # Runs on the same weekday as the start date
                elif habit.frequency == "Weekly":
                    if today_weekday == habit.start_date.weekday():
                        scheduled_today = True

                # Skip this habit if it is not scheduled today
                if not scheduled_today:
                    continue

                # Add habit to today's list
                today_habits.append(habit)

            # If the user has no habits today, don't send an email
            if not today_habits:
                continue

            # Create the habit list for the email
            habit_list = "\n".join(
                f"🔹 {habit.name} - Reminder: {habit.reminder_time}"
                for habit in today_habits
            )

            # Email message
            message = f"""
Good Morning {user.username}! 🌅

Here are your habits scheduled for today.

Date: {today}

Today's Habits:

{habit_list}

Please complete your habits today and keep building a healthy routine.

Stay consistent and stay healthy! 💪

Habit Tracker Team
"""

            try:

                # Send email
                send_mail(
                    subject="🌅 Good Morning! Your Habits for Today",

                    message=message,

                    from_email=settings.DEFAULT_FROM_EMAIL,

                    recipient_list=[
                        user.email
                    ],

                    fail_silently=False,
                )

                total_emails += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Morning habit email sent to {user.email}"
                    )
                )

            except Exception as e:

                self.stdout.write(
                    self.style.ERROR(
                        f"Email failed for {user.email}: {e}"
                    )
                )

        # Final result
        self.stdout.write(
            self.style.SUCCESS(
                f"Completed. "
                f"Total emails sent: {total_emails}"
            )
        )
