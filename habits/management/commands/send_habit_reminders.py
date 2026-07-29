from datetime import date

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User

from habits.models import Habit, HabitLog


class Command(BaseCommand):

    help = "Send email reminders for today's pending habits"

    def handle(self, *args, **kwargs):

        # Get today's date automatically
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
            f"Checking pending habits for {today}"
        )

        # Get all users who have an email
        users = User.objects.exclude(
            email__isnull=True
        ).exclude(
            email=""
        )

        total_emails = 0

        for user in users:

            # Get habits active today
            habits = Habit.objects.filter(
                user=user,
                start_date__lte=today,
                end_date__gte=today,
            )

            pending_habits = []

            for habit in habits:

                # Check whether this habit is scheduled for today
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
                # Repeats on the same weekday as start_date
                elif habit.frequency == "Weekly":
                    if today_weekday == habit.start_date.weekday():
                        scheduled_today = True

                # If not scheduled today, skip it
                if not scheduled_today:
                    continue

                # Check whether the user completed this habit TODAY
                completed_today = HabitLog.objects.filter(
                    habit=habit,
                    log_date=today,
                    completed=True
                ).exists()

                # Only add incomplete habits
                if not completed_today:

                    pending_habits.append(
                        habit.name
                    )

            # Send email only if pending habits exist
            if pending_habits:

                habit_list = "\n".join(
                    f"❌ {habit_name}"
                    for habit_name in pending_habits
                )

                message = f"""
Hello {user.username},

You have pending habits for today.

Date: {today}

Today's Pending Habits:

{habit_list}

Please complete your habits today and keep building a healthy routine.

Stay consistent and stay healthy!

Habit Tracker Team
"""

                try:

                    send_mail(

                        subject="🔔 Your Pending Habits for Today",

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
                            f"Reminder sent to {user.email}"
                        )
                    )

                except Exception as e:

                    self.stdout.write(
                        self.style.ERROR(
                            f"Email failed for "
                            f"{user.email}: {e}"
                        )
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"Completed. "
                f"Total emails sent: {total_emails}"
            )
        )