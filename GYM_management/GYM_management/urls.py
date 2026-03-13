from django.contrib import admin
from django.urls import path
from gym import views

urlpatterns = [
    # ================= Django Admin =================
    path('admin/', admin.site.urls),

    # ================= LOGIN / LOGOUT =================
    # Root path redirects to login
    path('', views.Login, name='login'),
    path('logout/', views.Logout_admin, name='logout'),

    # ================= DASHBOARDS =================
    # 'home' used for Admin redirect, Index view is protected by staff_or_trainer_required
    path('admin-home/', views.Index, name='home'),
    path('trainer-home/', views.Trainer_Home, name='trainer_home'),

    # ================= BASIC PAGES =================
    path('about/', views.About, name='about'),
    path('contact/', views.Contact, name='contact'),

    # ================= TRAINER (ADMIN ONLY) =================
    path('add_trainer/', views.Add_Trainer, name='add_trainer'),
    path('view_trainer/', views.View_Trainer, name='view_trainer'),
    path('delete_trainer/<int:pid>/', views.Delete_Trainer, name='delete_trainer'),
    path('add_salary/<int:pid>/', views.Add_Trainer_Salary, name='add_salary'),
    path('salary_history/<int:pid>/', views.Trainer_Salary_History, name='salary_history'),

    # ================= EQUIPMENT (ADMIN OR TRAINER) =================
    path('add_equipment/', views.Add_Equipment, name='add_equipment'),
    path('view_equipment/', views.View_Equipment, name='view_equipment'),
    path('delete_equipment/<int:pid>/', views.Delete_Equipment, name='delete_equipment'),

    # ================= PLANS =================
    path('add_plan/', views.Add_Plan, name='add_plan'),
    path('view_plan/', views.View_Plan, name='view_plan'),
    path('delete_plan/<int:pid>/', views.Delete_Plan, name='delete_plan'),

    # ================= MEMBERS (ADMIN OR TRAINER) =================
    path('add_member/', views.Add_Member, name='add_member'),
    path('view_member/', views.View_Member, name='view_member'),
    path('delete_member/<int:pid>/', views.Delete_Member, name='delete_member'),

    # ================= FEES (ADMIN OR TRAINER) =================
    path('add_fees/<int:pid>/', views.Add_Fees, name='add_fees'),

    # ISSUE FIXED: Renamed URL pattern for consistency and clarity
    path('member_fees_history/<int:pid>/', views.Member_Fees_History, name='member_fees_history'),

    # ================= ATTENDANCE (ADMIN OR TRAINER) =================
    path('mark_attendance/', views.Mark_Attendance, name='mark_attendance'),
    path('view_attendance/', views.View_Attendance, name='view_attendance'),
]