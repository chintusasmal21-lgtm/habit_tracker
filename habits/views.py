from django.shortcuts import render, redirect,get_object_or_404,redirect
from .models import Register
from django.core.mail import send_mail
from .models import Habit,HabitLog
from datetime import date, datetime,timedelta

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count
from habits.models import Profile
from django.shortcuts import render
import random
from django.conf import settings

   


def home(request):
    return render(request, 'habits/home.html')
def about(request):
    return render(request, 'habits/about.html')
def contact(request):

    if request.method == "POST":

        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        send_mail(
            subject,
            f"""
               Name: {name}

               Email: {email}

               Message:{message}
            """,
            email,
            ['yourgmail@gmail.com'],
            fail_silently=False,
        )

        messages.success(
            request,
            "Message sent successfully!"
        )

    return render(
        request,
        'habits/contact.html'
    )
@login_required
def dashboard(request):

    today = date.today()

    # Total Habits
    total_habits = Habit.objects.filter(
        user=request.user
    ).count()

    # Pending Habits
    pending_habits = Habit.objects.filter(
        user=request.user,
        status="Pending"
    )

    # Completed Habits
    completed_habits = Habit.objects.filter(
        user=request.user,
        status="Completed"
    )

    # Habits completed today
    completed_today = HabitLog.objects.filter(
        habit__user=request.user,
        log_date=today,
        completed=True
    ).count()
    

    # Habits completed this week
    completed_week = 0

    habits = Habit.objects.filter(user=request.user)

    for habit in habits:
       total_logs = HabitLog.objects.filter(habit=habit).count()
       completed_logs = HabitLog.objects.filter(
        habit=habit,
        completed=True
        ).count()
       if total_logs > 0 and total_logs == completed_logs:
        completed_week += 1

    active_days = HabitLog.objects.filter(
    habit__user=request.user,
    completed=True
    ).values('log_date').distinct().count()

    current_streak = 0
    check_date = date.today()

    while HabitLog.objects.filter(
        habit__user=request.user,
        log_date=check_date,
        completed=True
    ).exists():

       current_streak += 1
       check_date -= timedelta(days=1)

    context = {

        "total_habits": total_habits,

        "pending_habits": pending_habits,

        "completed_habits": completed_habits,

        "completed_today": completed_today,

        "completed_week": completed_week,
        "active_days": active_days,

        "current_streak": current_streak,
       

    }

    return render(
        request,
        "habits/dashboard.html",
        context
    )


def user_login(request):
    error = ""
    if request.method == "POST":

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect('/dashboard/')

    return render(request, 'habits/login.html', {'error': error})
    
    
def register(request):
    if request.method == "POST":

        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        gender = request.POST.get('gender')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'habits/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, 'habits/register.html')

        if Profile.objects.filter(phone=phone).exists():
            messages.error(request, "Phone number already exists.")
            return render(request, 'habits/register.html')

        Register.objects.create(
            username=username,
            email=email,
            phone=phone,
            gender=gender,
            password=password
        )

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Email temporarily disabled

        messages.success(request, "Registration successful.")
        return redirect('/login/')

    return render(request, 'habits/register.html')

import logging
from datetime import datetime, timedelta
from .models import Habit, HabitLog
logger = logging.getLogger(__name__)

@login_required
def add_habit(request):

    if request.method == "POST":

        start_date = datetime.strptime(
            request.POST.get("start_date"),
            "%Y-%m-%d"
        ).date()

        end_date = datetime.strptime(
            request.POST.get("end_date"),
            "%Y-%m-%d"
        ).date()

        habit = Habit.objects.create(
            user=request.user,
            name=request.POST.get("habit_name"),
            description=request.POST.get("description"),
            category=request.POST.get("category"),
            frequency=request.POST.get("frequency"),
            reminder_time=request.POST.get("reminder_time"),
            start_date=start_date,
            end_date=end_date,
            status="Pending"
        )

        current_date = start_date

        while current_date <= end_date:

            if habit.frequency == "Daily":

                HabitLog.objects.get_or_create(
                    habit=habit,
                    log_date=current_date,
                    defaults={
                        "completed": False,
                        "missed": False
                    }
                )

                current_date += timedelta(days=1)

            elif habit.frequency == "Weekdays":

                if current_date.weekday() < 5:

                    HabitLog.objects.get_or_create(
                        habit=habit,
                        log_date=current_date,
                        defaults={
                            "completed": False,
                            "missed": False
                        }
                    )

                current_date += timedelta(days=1)

            elif habit.frequency == "Weekends":

                if current_date.weekday() >= 5:

                    HabitLog.objects.get_or_create(
                        habit=habit,
                        log_date=current_date,
                        defaults={
                            "completed": False,
                            "missed": False
                        }
                    )

                current_date += timedelta(days=1)

            elif habit.frequency == "Weekly":

                HabitLog.objects.get_or_create(
                    habit=habit,
                    log_date=current_date,
                    defaults={
                        "completed": False,
                        "missed": False
                    }
                )

                current_date += timedelta(days=7)

        # Send email (optional)
        try:
            if request.user.email:
                send_mail(
                    subject="Habit Created Successfully",
                    message=f"""
Your habit has been created successfully.

Habit Name : {habit.name}
Category   : {habit.category}
Frequency  : {habit.frequency}
Reminder   : {habit.reminder_time}

Start Date : {habit.start_date}
End Date   : {habit.end_date}

Stay consistent and achieve your goals!
""",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[request.user.email],
                    fail_silently=True,
                )

        except Exception as e:
            logger.error(f"Email Error: {e}")

        messages.success(request, "Habit added successfully!")
        return redirect("dashboard")

    return render(request, "habits/add_habit.html")


def profile(request):
    return render(request, 'habits/profile.html')

def logout_view(request):
    logout(request)
    return redirect('/admin-login/')

def admin_login(request):

    error = ""

    if request.method == "POST":

        username = request.POST.get('username')

        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None and user.is_superuser:

            login(request, user)

            return redirect('/admin-dashboard/')

        else:

            error = "Invalid Admin Username or Password"

    return render( request, 'habits/admin_login.html', {'error': error})

@login_required(login_url='/admin-login/')

def admin_dashboard(request):

    total_users = Register.objects.count()

    total_habits = Habit.objects.count()

    habits = Habit.objects.all()

    users = Register.objects.all()

    context = {

        'total_users': total_users,

        'total_habits': total_habits,

        'habits': habits,

        'users': users,

    }

    return render(
        request,
        'habits/admin_dashboard.html',
        context
    )
@login_required
def delete_habit(request, id):

    habit = get_object_or_404(
        Habit,
        id=id,
        user=request.user
    )

    habit.delete()

    return redirect('/habit-list/')
def logout_view(request):

    logout(request)

    return redirect('/')

@login_required
def delete_user(request, id):
    habit = Habit.objects.get(
        id=id,
        user=request.user
    )

    return redirect('/admin-dashboard/')
@login_required(login_url='/admin-login/')
def admin_delete_habit(request, id):
    habit = get_object_or_404(Habit, id=id)
    habit.delete()

    messages.success(request, "Habit deleted successfully.")

    return redirect('admin_dashboard')



@login_required

def habit_list(request):

    habits = Habit.objects.filter(
        
    user=request.user
)

    context = {

        'habits': habits

    }

    return render(
        request,
        'habits/habit_list.html',
        context
    )
@login_required
def edit_habit(request):

    habits = Habit.objects.filter(
        user=request.user
    )

    return render(
        request,
        'habits/edit_habit.html',
        {
            'habits': habits
        }
    )


@login_required
def habit_edits(request, id):

    habit = get_object_or_404(
        Habit,
        id=id,
        user=request.user
    )

    old_frequency = habit.frequency
    old_start_date = habit.start_date
    old_end_date = habit.end_date

    if request.method == "POST":

        habit.description = request.POST.get("description")
        habit.category = request.POST.get("category")
        habit.frequency = request.POST.get("frequency")
        habit.reminder_time = request.POST.get("reminder_time")

        habit.end_date = datetime.strptime(
            request.POST.get("end_date"),
            "%Y-%m-%d"
        ).date()

        if habit.end_date >= date.today():
            habit.status = "Pending"
        else:
            habit.status = "Completed"

        habit.save()

        # Recreate logs only if schedule changed
        if (
            old_frequency != habit.frequency or
            old_start_date != habit.start_date or
            old_end_date != habit.end_date
        ):

            HabitLog.objects.filter(habit=habit).delete()

            current_date = habit.start_date

            while current_date <= habit.end_date:

                if habit.frequency == "Daily":

                    HabitLog.objects.get_or_create(
                        habit=habit,
                        log_date=current_date,
                        defaults={
                            "completed": False,
                            "missed": False
                        }
                    )

                    current_date += timedelta(days=1)

                elif habit.frequency == "Weekdays":

                    if current_date.weekday() < 5:

                        HabitLog.objects.get_or_create(
                            habit=habit,
                            log_date=current_date,
                            defaults={
                                "completed": False,
                                "missed": False
                            }
                        )

                    current_date += timedelta(days=1)

                elif habit.frequency == "Weekends":

                    if current_date.weekday() >= 5:

                        HabitLog.objects.get_or_create(
                            habit=habit,
                            log_date=current_date,
                            defaults={
                                "completed": False,
                                "missed": False
                            }
                        )

                    current_date += timedelta(days=1)

                elif habit.frequency == "Weekly":

                    HabitLog.objects.get_or_create(
                        habit=habit,
                        log_date=current_date,
                        defaults={
                            "completed": False,
                            "missed": False
                        }
                    )

                    current_date += timedelta(days=7)

        try:
            send_mail(
                "Habit Updated",
                f"""
Your habit "{habit.name}" has been updated.

Description : {habit.description}
Category    : {habit.category}
Frequency   : {habit.frequency}
Reminder    : {habit.reminder_time}
Start Date  : {habit.start_date}
End Date    : {habit.end_date}
Status      : {habit.status}
""",
                settings.EMAIL_HOST_USER,
                [request.user.email],
                fail_silently=False,
            )

        except Exception as e:
            print("Email Error:", e)

        messages.success(request, "Habit updated successfully!")

        return redirect("edit_habit")

    return render(
        request,
        "habits/habit_edits.html",
        {
            "habit": habit
        }
    )
def complete_habit(request, id):

    habit = get_object_or_404(
    Habit,
    id=id,
    user=request.user
)

    habit.status = "Completed"

    habit.save()

    return redirect('/dashboard/')
@login_required
def habit_detail(request, id):

    habit = get_object_or_404(
        Habit,
        id=id,
        user=request.user
    )

    today = date.today()

    HabitLog.objects.filter(
        habit=habit,
        log_date__lt=today,
        completed=False
    ).update(
        missed=True
    )

    logs = HabitLog.objects.filter(
        habit=habit
    ).order_by('log_date')

    return render(
        request,
        'habits/habit_detail.html',
        {
            'habit': habit,
            'logs': logs,
            'today': today
        }
    )
@login_required
def mark_complete(request, log_id):

    log = get_object_or_404(
        HabitLog,
        id=log_id
    )

    log.completed = True
    log.save()

    return redirect(
        'habit_detail',
        id=log.habit.id
    )

@login_required
def analytics(request):

    habits = Habit.objects.filter(
        user=request.user
    )

    return render(
        request,
        'habits/analytics.html',
        {
            'habits': habits
        }
    )
@login_required
def habit_analytics(request, id):

    habit = get_object_or_404(
        Habit,
        id=id,
        user=request.user
    )

    logs = HabitLog.objects.filter(
        habit=habit
    )

    total_days = logs.count()

    completed_days = logs.filter(
        completed=True
    ).count()

    missed_days = logs.filter(
        missed=True
    ).count()

    remaining_days = total_days - completed_days - missed_days

    success_rate = 0

    if total_days > 0:
        success_rate = round(
            (completed_days / total_days) * 100,
            
        )
    date_data = logs.filter(
        completed=True
    ).values(
        'log_date'
    ).annotate(
        total=Count('id')
    ).order_by('log_date')

    date_labels = []    
    date_counts = []

    for item in date_data:

        date_labels.append(
            item['log_date'].strftime('%d-%m')
        )

        date_counts.append(
            item['total']
        )    

    return render(
        request,
        'habits/habit_analytics.html',
        {
            'habit': habit,
            'total_days': total_days,
            'completed_days': completed_days,
            'missed_days': missed_days,
            'remaining_days': remaining_days,
            'success_rate': success_rate,
            'date_labels': date_labels,
            'date_counts': date_counts,
        }
    )
@login_required
def analysis(request):

    total = Habit.objects.filter(
        user=request.user
    ).count()

    completed = Habit.objects.filter(
        user=request.user,
        status='Completed'
    ).count()

    pending = Habit.objects.filter(
        user=request.user,
        status='Pending'
    ).count()

    missed = Habit.objects.filter(
        user=request.user,
        status='Missed'
    ).count()

    success_rate = 0

    if total > 0:
        success_rate = round(
            (completed / total) * 100
        )
    date_data = HabitLog.objects.filter(
        habit__user=request.user,
        completed=True
      
    ).values(
        'log_date'
    ).annotate(
        total=Count('id')
    ).order_by('log_date')
   


    date_labels = []
    date_counts = []

    for item in date_data:

        date_labels.append(
            item['log_date'].strftime('%d-%m')
        )

        date_counts.append(
            item['total']
        )
    weekly_counts = [5, 8, 12, 15]

    context = {

        'total': total,
        'completed': completed,
        'pending': pending,
        'missed': missed,
        'success_rate': success_rate,

        'date_labels': date_labels,
        'date_counts': date_counts,
        'weekly_counts': weekly_counts,
       

    }    

   

    return render(
        request,
        'habits/analysis.html',
        context
    )
@login_required
def profile(request):

    profile = Profile.objects.get(
        user=request.user
    )

    total_habits = Habit.objects.filter(
        user=request.user
    ).count()

    completed_habits = Habit.objects.filter(
        user=request.user,
        status='Completed'
    ).count()

    return render(
        request,
        'habits/profile.html',
        {
            'profile': profile,
            'total_habits': total_habits,
            'completed_habits': completed_habits
        }
    )
@login_required
def achievements(request):

    completed = HabitLog.objects.filter(
        habit__user=request.user,
        completed=True
    ).count()

    achievements = []

    if completed >= 1:
        achievements.append("🎯 First Step")

    elif completed >= 5:
        achievements.append("⭐ Habit Explorer")

    elif completed >= 10:
        achievements.append("🌟 Habit Champion")

    elif completed >= 20:
        achievements.append("🏆 Habit Master")

    return render(
        request,
        'habits/achievements.html',
        {
            'achievements': achievements
        }
    )
    
@login_required
def edit_profile(request):

    profile = Profile.objects.get(
        user=request.user
    )

    if request.method == "POST":

        request.user.username = request.POST.get(
            'username'
        )

        request.user.email = request.POST.get(
            'email'
        )

        request.user.save()

        if 'profile_pic' in request.FILES:

            profile.profile_pic = request.FILES[
                'profile_pic'
            ]

            profile.save()

        return redirect('profile')

    return render(
        request,
        'habits/edit_profile.html',
        {
            'profile': profile
        }
    )
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages

@login_required
def change_password(request):

    if request.method == "POST":

        old_password = request.POST.get(
            'old_password'
        )

        new_password = request.POST.get(
            'new_password'
        )

        confirm_password = request.POST.get(
            'confirm_password'
        )

        if not request.user.check_password(
            old_password
        ):

            messages.error(
                request,
                "Current password is incorrect."
            )

        elif new_password != confirm_password:

            messages.error(
                request,
                "Passwords do not match."
            )

        else:

            request.user.set_password(
                new_password
            )

            request.user.save()

            update_session_auth_hash(
                request,
                request.user
            )

            messages.success(
                request,
                "Password changed successfully."
            )

    return render(
        request,
        'habits/change_password.html'
    )
@login_required
def delete_account(request):

    if request.method == 'POST':

        user = request.user

        logout(request)

        user.delete()

        return redirect('home')

    return render(
        request,
        'habits/delete_account.html'
    )
def forgot_password(request):

    if request.method == "POST":

        email = request.POST.get('email')

        try:

            user = User.objects.get(
                email=email
            )

            otp = str(
                random.randint(
                    100000,
                    999999
                )
            )

            PasswordOTP.objects.create(
                user=user,
                otp=otp
            )

            send_mail(
                'Password Reset OTP',
                f'Your OTP is {otp}',
                'admin@gmail.com',
                [email],
                fail_silently=False
            )

            request.session['reset_user'] = user.id

            return redirect(
                'verify_otp'
            )

        except User.DoesNotExist:

            return render(
                request,
                'habits/forgot_password.html',
                {
                    'error':
                    'Email not found'
                }
            )

    return render(
        request,
        'habits/forgot_password.html'
    )
from .models import PasswordOTP
def verify_otp(request):

    if request.method == "POST":

        entered_otp = request.POST.get(
            'otp'
        )

        user_id = request.session.get(
            'reset_user'
        )

        otp_obj = PasswordOTP.objects.filter(
            user_id=user_id,
            otp=entered_otp
        ).last()

        if otp_obj:

            request.session[
                'otp_verified'
            ] = True

            return redirect(
                'reset_password'
            )

        else:

            return render(
                request,
                'habits/verify_otp.html',
                {
                    'error':
                    'Invalid OTP'
                }
            )

    return render(
        request,
        'habits/verify_otp.html'
    )
def reset_password(request):

    if not request.session.get(
        'otp_verified'
    ):

        return redirect(
            'forgot_password'
        )

    if request.method == "POST":

        password = request.POST.get(
            'password'
        )

        confirm_password = request.POST.get(
            'confirm_password'
        )

        if password == confirm_password:

            user = User.objects.get(
                id=request.session[
                    'reset_user'
                ]
            )

            user.set_password(
                password
            )

            user.save()

            request.session.flush()

            return redirect(
                'login'
            )

    return render(
        request,
        'habits/reset_password.html'
    )



from django.shortcuts import render

def health(request):
    return render(request, "habits/health.html")
from django.shortcuts import render




def bmi_calculator(request):

    bmi = None
    status = None
    tips = []

    if request.method == "POST":

        age = int(request.POST["age"])
        gender = request.POST["gender"]
        height = float(request.POST["height"])
        weight = float(request.POST["weight"])

        bmi = round(weight / ((height / 100) ** 2), 1)

        if bmi < 18.5:
            status = "🔵 Underweight"
            tips = [
                "🍗 Eat protein-rich foods",
                "🥛 Drink milk daily",
                "💪 Do strength training",
                "🍌 Increase healthy calories"
            ]

        elif bmi < 25:
            status = "🟢 Healthy"
            tips = [
                "🥗 Maintain a balanced diet",
                "🏃 Exercise daily",
                "💧 Drink enough water",
                "😴 Sleep 7-8 hours"
            ]

        elif bmi < 30:
            status = "🟠 Overweight"
            tips = [
                "🚶 Walk 8000 steps daily",
                "🥦 Eat more vegetables",
                "🍩 Reduce sugar",
                "🚫 Avoid junk food"
            ]

        else:
            status = "🔴 Obese"
            tips = [
                "👨‍⚕️ Consult a doctor",
                "🏃 Cardio exercise",
                "🥗 Follow a calorie deficit",
                "🚫 Avoid sugary drinks"
            ]

        if gender == "Male":
            tips.append("🥩 Increase protein for muscle growth")
            tips.append("🏋️ Include strength workouts")

        else:
            tips.append("🥛 Eat calcium-rich foods")
            tips.append("🥬 Include iron-rich foods")

        return render(request, "habits/bmi.html", {
            "age": age,
            "gender": gender,
            "height": height,
            "weight": weight,
            "bmi": bmi,
            "status": status,
            "tips": tips,
        })

    return render(request, "habits/bmi.html")


from django.shortcuts import render

def calorie_calculator(request):

    calories = None
    goal = None

    if request.method == "POST":

        age = int(request.POST.get("age"))
        gender = request.POST.get("gender")
        weight = float(request.POST.get("weight"))
        height = float(request.POST.get("height"))
        activity = float(request.POST.get("activity"))
        goal = request.POST.get("goal")

        # Calculate BMR (Mifflin-St Jeor Equation)
        if gender == "Male":
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        else:
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161

        # Daily calories
        calories = bmr * activity

        # Adjust based on goal
        if goal == "Weight Loss":
            calories -= 500
        elif goal == "Weight Gain":
            calories += 500

        calories = round(calories)

    return render(
        request,
        "habits/calories_calculator.html",
        {
            "calories": calories,
            "goal": goal,
        }
    )

from .models import Food
@login_required(login_url='/admin-login/')
def food_list(request):

    foods = Food.objects.all().order_by("name")

    return render(
        request,
        "habits/food_list.html",
        {
            "foods": foods
        }
    )
@login_required(login_url='/admin-login/')
def add_food(request):

    if request.method == "POST":

        Food.objects.create(

            name=request.POST.get("name"),

            food_type=request.POST.get("food_type"),

            meal_type=request.POST.get("meal_type"),

            diet_type=request.POST.get("diet_type"),

            goal=request.POST.get("goal"),

            serving_size=request.POST.get("serving_size"),

            calories=request.POST.get("calories"),
            health_score=request.POST.get("health_score"),
           

            
        )

        return redirect("food_list")

    return render(request, "habits/add_food.html")
@login_required(login_url='/admin-login/')
def edit_food(request, id):

    food = get_object_or_404(
        Food,
        id=id
    )

    if request.method == "POST":

        food.name = request.POST.get("name")
        food.food_type = request.POST.get("food_type")
        food.meal_type = request.POST.get("meal_type")
        food.diet_type = request.POST.get("diet_type")
        food.goal = request.POST.get("goal")
        food.serving_size = request.POST.get("serving_size")
        food.calories = request.POST.get("calories")
        food.health_score = request.POST.get("health_score")
       
        

        food.save()

        return redirect("food_list")

    return render(
        request,
        "habits/edit_food.html",
        {
            "food": food
        }
    )
@login_required(login_url='/admin-login/')
def delete_food(request, id):

    food = get_object_or_404(
        Food,
        id=id
    )

    food.delete()

    return redirect("food_list")


@login_required
def food_recommendations(request):

    foods = []

    current = None
    target_calories = None
    total_calories = 0

    if request.GET.get("target_calories"):

        current = int(request.GET.get("target"))

        target_calories = int(request.GET.get("target_calories"))

        all_foods = Food.objects.order_by("-health_score", "-calories")

        for food in all_foods:

            if total_calories >= target_calories:
                break

            foods.append(food)
            total_calories += food.calories

    return render(
        request,
        "habits/food_recommendations.html",
        {
            "foods": foods,
            "current": current,
            "target_calories": target_calories,
            "total_calories": total_calories,
        }
    )
from django.db.models import Q
from .models import Medicine


def medicine_search(request):

    medicines = []

    query = request.GET.get("q")

    if query:

        medicines = Medicine.objects.filter(
            Q(problem__icontains=query) |
            Q(medicine_name__icontains=query) |
            Q(symptoms__icontains=query)
        )

    return render(
        request,
        "habits/medicine_search.html",
        {
            "medicines": medicines,
            "query": query,
        },
    )
# Create your views here.
