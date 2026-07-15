from django.urls import path
from . import views
from .api_views import test, habit_list
urlpatterns = [
     path('api/test/', test),
     path('api/habits/', habit_list),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('register/', views.register, name='register'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('add_habit/', views.add_habit, name='add_habit'),
    path('profile/', views.profile, name='profile'),

    path('logout/', views.logout_view, name='logout'),
    path('login/', views.user_login, name='login'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    path('delete-habit/<int:id>/', views.delete_habit, name='delete_habit'), 
    path('delete-user/<int:id>/', views.delete_user, name='delete_user'),
    path(
    'habit-list/',
    views.habit_list,
    name='habit_list'
),
    path(
    'complete-habit/<int:id>/',
    views.complete_habit,
    name='complete_habit'

),
path(
    'edit_habit/<int:id>/',
    views.edit_habit,
    name='edit_habit'
),

 path('edit_habit/', views.edit_habit, name='edit_habit'),
 
 path(
    'habit_edits/<int:id>/',
    views.habit_edits,
    name='habit_edits'
),
 path(
    'habit/<int:id>/',
    views.habit_detail,
    name='habit_detail'
),

path(
    'mark-complete/<int:log_id>/',
    views.mark_complete,
    name='mark_complete'
),
path(
    'analytics/',
    views.analytics,
    name='analytics'
),


path(
    'habit-analytics/<int:id>/',
    views.habit_analytics,
    name='habit_analytics'
),
path(
    'analysis/',
    views.analysis,
    name='analysis'
),
path(
    'achievements/',
    views.achievements,
    name='achievements'
),
path(
    'edit-profile/',
    views.edit_profile,
    name='edit_profile'
),
path(
    'change-password/',
    views.change_password,
    name='change_password'
),
path(
    'delete-account/',
    views.delete_account,
    name='delete_account'
),
path(
    'forgot-password/',
    views.forgot_password,
    name='forgot_password'
),
path(
    'verify-otp/',
    views.verify_otp,
    name='verify_otp'
),

path(
    'reset-password/',
    views.reset_password,
    name='reset_password'
),
 path("health/", 
      views.health,
     name="health"
),
path("bmi/", views.bmi_calculator, name="bmi_calculator"),
path(
    "calories_calculator/",
    views.calorie_calculator,
    name="calorie_calculator"
),
path(
    'admin-delete-habit/<int:id>/',
    views.admin_delete_habit,
    name='admin_delete_habit'
),
path(
    "food-list/",
    views.food_list,
    name="food_list"
),

path(
    "add-food/",
    views.add_food,
    name="add_food"
),

path(
    "edit-food/<int:id>/",
    views.edit_food,
    name="edit_food"
),

path(
    "delete-food/<int:id>/",
    views.delete_food,
    name="delete_food"
),
path(
    "food-recommendations/",
    views.food_recommendations,
    name="food_recommendations"
),
path(
    "medicine-search/",
    views.medicine_search,
    name="medicine_search",
),
path(
    "profile/",
    views.profile,
    name="profile"
),




]




