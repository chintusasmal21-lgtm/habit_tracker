from django.core.management.base import BaseCommand
from habits.models import Food
import openpyxl
import os


class Command(BaseCommand):
    help = "Import foods from Excel"

    def handle(self, *args, **kwargs):

        file_path = os.path.join(
            "data",
            "Food_Database_400.xlsx"
        )

        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active

        # Delete old records
        Food.objects.all().delete()

        # Convert text to numbers
        score_map = {
            "High": 5,
            "Medium": 3,
            "Low": 1,
            "Excellent": 5,
            "Good": 4,
            "Average": 3,
            "Poor": 2,
            "Avoid": 1,
        }

        for row in sheet.iter_rows(min_row=2, values_only=True):

            Food.objects.create(
                name=row[0],
                food_type=row[1],
                meal_type=row[2],
                diet_type=row[3],
                goal=row[4],
                serving_size=row[5],
                calories=int(row[6]),
                health_score=score_map.get(str(row[7]).strip(), 3),
            )

        self.stdout.write(
            self.style.SUCCESS("Foods imported successfully!")
        )
