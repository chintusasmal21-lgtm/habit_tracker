from django.core.management.base import BaseCommand
from habits.models import Food
import openpyxl
import os


class Command(BaseCommand):
    help = "Import foods from Excel"

    def handle(self, *args, **kwargs):

        file_path = os.path.join(
            "data",
            "food_dataset_240_real_foods.xlsx"
        )

        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active

        # Delete existing data
        Food.objects.all().delete()

        # Convert health score text to number
        score_map = {
            "Excellent": 5,
            "Very Good": 4,
            "Good": 3,
            "Average": 2,
            "Poor": 1,
            "High": 5,
            "Medium": 3,
            "Low": 1,
            "Avoid": 1,
        }

        for row in sheet.iter_rows(min_row=2, values_only=True):

            # Skip empty rows
            if not row[0]:
                continue

            Food.objects.create(
                name=str(row[0]).strip(),
                food_type=str(row[1]).strip(),
                meal_type=str(row[2]).strip(),
                diet_type=str(row[3]).strip(),
                goal=str(row[4]).strip(),
                serving_size=str(row[5]).strip(),
                calories=int(row[6]),
                health_score=score_map.get(str(row[7]).strip(), 3),
            )

        self.stdout.write(
            self.style.SUCCESS("✅ Foods imported successfully!")
        )
