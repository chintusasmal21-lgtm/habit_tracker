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

Message:
{message}
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

    Habit.objects.filter(
        user=request.user,
        end_date__lte=date.today(),
        status='Pending'
    ).update(
        status='Completed'
    )

    total_habits = Habit.objects.filter(
        user=request.user
    ).count()

    pending_habits = Habit.objects.filter(
        user=request.user,
        status='Pending'
    )

    completed_habits = Habit.objects.filter(
        user=request.user,
        status='Completed'
    )
    today = date.today()

    habits_completed_today = HabitLog.objects.filter(
        habit__user=request.user,
        completed=True,
        log_date=today
    ).count()

    
    habits_completed_this_week = Habit.objects.filter(
        user=request.user,
        status='Completed',
        end_date__gte=today - timedelta(days=7)
    ).count()
    context = {

        'total_habits': total_habits,

        'pending_habits': pending_habits,

        'completed_habits': completed_habits,

        'completed_count': completed_habits.count(),

        'habits_completed_today': habits_completed_today,

        'habits_completed_this_week': habits_completed_this_week,

    }

    return render(
        request,
        'habits/dashboard.html',
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

        # Check email
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, 'habits/register.html')

        # Check phone
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
        send_mail(

            'Registration Successful',

            f'Hello {username}, Your registration completed successfully in Habit Tracker.',

            'yourgmail@gmail.com',

            [email],

            fail_silently=False,
        )
        messages.success(request, "Registration successful.")
        return redirect('/login/')

    return render(request, 'habits/register.html')

from datetime import datetime, timedelta
from .models import Habit, HabitLog

@login_required
def add_habit(request):

    if request.method == "POST":

        start_date = datetime.strptime(
            request.POST.get('start_date'),
            '%Y-%m-%d'
        ).date()

        end_date = datetime.strptime(
            request.POST.get('end_date'),
            '%Y-%m-%d'
        ).date()

        habit = Habit.objects.create(
            user=request.user,
            name=request.POST.get('habit_name'),
            description=request.POST.get('description'),
            habit_time=request.POST.get('habit_time'),
            start_date=start_date,
            end_date=end_date,
            status='Pending'
        )
        messages.success(request, "Habit successfully added!")

        current_date = start_date

        while current_date <= end_date:

            print("Creating:", current_date)

            HabitLog.objects.create(
                habit=habit,
                log_date=current_date,
                completed=False
            )

            current_date += timedelta(days=1)
        send_mail(
          'Habit Created',
           f'Your habit "{habit.name}" has been created successfully.\n\n'
           f'Start Date: {habit.start_date}\n'
           f'End Date: {habit.end_date}',
           'yourgmail@gmail.com',
           [request.user.email],
           fail_silently=False,
        )
    
        

        return redirect('/dashboard/')

    return render(request, 'habits/add_habit.html')

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

    if request.method == 'POST':

        habit.name = request.POST.get(
            'habit_name'
        )

        habit.description = request.POST.get(
            'description'
        )
        habit.habit_time = request.POST.get(
        'habit_time'
    )
        
        new_end_date = datetime.strptime(
            request.POST.get('end_date'),
            '%Y-%m-%d'
        ).date()

        habit.end_date = new_end_date

        if new_end_date > date.today():
         habit.status = 'Pending'

        habit.save()

        send_mail(
           'Habit Updated',
           f'Your habit "{habit.name}" has been updated.\n\n'
           f'Your description "{habit.description}" has been updated\n'
           f'Start Date: {habit.start_date}\n'
           f'New End Date: {habit.end_date}',
           'yourgmail@gmail.com',

           [request.user.email],
           fail_silently=False,
        ) 
        current_date = habit.start_date

        while current_date <= habit.end_date:

            HabitLog.objects.get_or_create(
                habit=habit,
                log_date=current_date
            )

            current_date =current_date+ timedelta(days=1)
    

        return redirect('edit_habit')
   

    return render(
        request,
        'habits/habit_edits.html',
        {'habit': habit}
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


# Create your views here.
