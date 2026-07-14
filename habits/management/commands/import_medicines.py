from django.core.management.base import BaseCommand
from habits.models import Medicine
import openpyxl
import os


class Command(BaseCommand):
    help = "Import medicines from Excel"

    def handle(self, *args, **kwargs):

        file_path = os.path.join(
            "data",
            "Health_Medicine_Database_100.xlsx"
        )

        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active

        # Optional: Remove old records
        Medicine.objects.all().delete()

        for row in sheet.iter_rows(min_row=2, values_only=True):

            Medicine.objects.create(
                problem=row[0],
                medicine_name=row[1],
                dosage=row[2],
                precautions=row[3],
                symptoms=row[4],
                home_remedy=row[5],
                foods_to_eat=row[6],
                foods_to_avoid=row[7],
                consult_doctor=row[8],
            )

        self.stdout.write(
            self.style.SUCCESS("Medicines imported successfully!")
        )