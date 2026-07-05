from django.http import JsonResponse
from .models import Habit

print("API FILE LOADED")

def test(request):
    print("TEST FUNCTION CALLED")
    return JsonResponse({
        "message": "API Working"
    })
def habit_list(request):

    habits = Habit.objects.all()

    data = []

    for habit in habits:
        data.append({
            "id": habit.id,
            "name": habit.name,
            "description": habit.description,
        })

    return JsonResponse(data, safe=False)