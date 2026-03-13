# views.py
from functools import wraps
from datetime import date, datetime, timedelta
import calendar

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404

from django.db.models import Sum

from .models import (
    Trainer, TrainerSalary,
    Equipment, Plan,
    Member, MemberFees,
    Attendance
)


# ================= ACCESS HELPERS =================

def is_admin(user):
    """Checks if the user is staff or belongs to the 'Admin' group."""
    return user.is_staff or user.groups.filter(name="Admin").exists()


def is_trainer(user):
    """Checks if the user belongs to the 'Trainer' group."""
    return user.groups.filter(name="Trainer").exists()


def is_staff_or_trainer(user):
    """Checks if the user is Admin or Trainer."""
    return is_admin(user) or is_trainer(user)


# ================= CUSTOM DECORATORS =================

def admin_required(view_func):
    """
    Decorator: Requires login and 'Admin' role.
    Redirects Trainers to their home for better UX instead of a 403 page.
    """

    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if is_admin(request.user):
            return view_func(request, *args, **kwargs)
        elif is_trainer(request.user):
            # Trainer is logged in but trying to access admin page
            messages.error(request, "Access Denied: You cannot view Admin pages.")
            return redirect('trainer_home')
        else:
            # Logged in but no role assigned
            return HttpResponseForbidden("Access Denied: Unauthorized role.")

    return _wrapped


def staff_or_trainer_required(view_func):
    """Requires login and either 'Admin' or 'Trainer' role."""
    # Uses Django's built-in decorator for concise check
    decorator = user_passes_test(is_staff_or_trainer, login_url='login')
    return decorator(view_func)


# ================= BASIC PAGES =================

def About(request):
    return render(request, 'about.html')


def Contact(request):
    return render(request, 'contact.html')


@staff_or_trainer_required
def Index(request):

    today = date.today()

    # Determine which attendance date to show: prefer today if records exist, otherwise use latest recorded date
    latest_date = Attendance.objects.order_by('-date').values_list('date', flat=True).first()
    if Attendance.objects.filter(date=today).exists():
        attendance_date = today
    else:
        attendance_date = latest_date or today

    # Attendance count for the selected attendance_date (normalize to 'Present')
    attendance_count = Attendance.objects.filter(date=attendance_date, status='Present').count()

    # Fees collected this month
    fees_collected = MemberFees.objects.filter(paid_on__year=today.year, paid_on__month=today.month).aggregate(total=Sum('amount'))['total'] or 0

    # New purchases in the last 30 days (using Equipment as purchases)
    thirty_days_ago = today - timedelta(days=30)
    new_purchases_count = Equipment.objects.filter(date__gte=thirty_days_ago).count()

    # Recent purchases list (latest 10)
    purchases_qs = Equipment.objects.order_by('-date')[:10]
    purchases_list = [
        {
            'item': e.name,
            'amount': e.price,
            'date': e.date.strftime('%Y-%m-%d')
        }
        for e in purchases_qs
    ]

    # Financial overview for last 6 months (labels + fees + salaries)
    revenue_labels = []
    revenue_fees = []
    revenue_salaries = []
    for months_ago in range(5, -1, -1):
        # compute year and month for the target month
        year = today.year
        month = today.month - months_ago
        while month <= 0:
            month += 12
            year -= 1

        label = f"{calendar.month_abbr[month]} {year}"
        revenue_labels.append(label)

        month_fees = MemberFees.objects.filter(paid_on__year=year, paid_on__month=month).aggregate(total=Sum('amount'))['total'] or 0
        month_salaries = TrainerSalary.objects.filter(paid_on__year=year, paid_on__month=month).aggregate(total=Sum('amount'))['total'] or 0

        revenue_fees.append(month_fees)
        revenue_salaries.append(month_salaries)

    total_members = Member.objects.count()

    context = {
        'attendance_count': attendance_count,
        'attendance_date': attendance_date.strftime('%Y-%m-%d') if attendance_date else '',
        'total_members': total_members,
        'fees_collected': fees_collected,
        'new_purchases_count': new_purchases_count,
        'purchases_list': purchases_list,
        # pass Python lists and let the template use json_script for safe injection
        'revenue_labels': revenue_labels,
        'revenue_fees': revenue_fees,
        'revenue_salaries': revenue_salaries,
    }

    return render(request, 'Index.html', context)



def Login(request):
    error = ""

    if request.method == "POST":
        u = request.POST.get('uname')
        p = request.POST.get('password')

        user = authenticate(request, username=u, password=p)

        if user:
            login(request, user)

            # ================= SESSION DATA =================
            request.session['user_id'] = user.id
            request.session['username'] = user.username
            request.session['email'] = user.email
            request.session['is_admin'] = False
            request.session['is_trainer'] = False


            if user.get_username() == "admin":
                request.session['is_admin'] = True
                return redirect("home")
            elif user.get_username() == "trainer":
                request.session['is_trainer'] = False
                return redirect("home")

            else:
                logout(request)
                request.session.flush()
                error = "unauthorized"
        else:
            error = "invalid"

    return render(request, 'Login.html', {"error": error})

def Logout_admin(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('login')


@staff_or_trainer_required
def Trainer_Home(request):
    return render(request, "trainer_home.html")


# ================= TRAINER (ADMIN ONLY) =================

@admin_required
def Add_Trainer(request):
    if request.session['is_admin']:
        error = ""
        if request.method == "POST":
            try:
                Trainer.objects.create(
                name=request.POST.get('name'),
                contact=request.POST.get('contact'),
                age=request.POST.get('age'),
                gender=request.POST.get('gender'),
                salary=request.POST.get('salary')
                )
                messages.success(request, "Trainer added successfully.")
                error = "no"
            except Exception as e:
                messages.error(request, f"Error adding trainer: {e}")
                error = "yes"

        return render(request, 'add_trainer.html', {'error': error})
    else:
        return render(request, 'access_denied.html')


@admin_required
def View_Trainer(request):

    if request.session['is_admin']:
        trainer = Trainer.objects.all()
        return render(request, 'view_trainer.html', {'trainer': trainer})
    else:
        return render(request, "access_denied.html")


@admin_required
def Delete_Trainer(request, pid):
    trainer = get_object_or_404(Trainer, id=pid)
    trainer.delete()
    messages.success(request, "Trainer deleted successfully.")
    return redirect('view_trainer')


@admin_required
def Add_Trainer_Salary(request, pid):
    if not request.session['is_trainer']:
        trainer = get_object_or_404(Trainer, id=pid)
        error = ""

        if request.method == "POST":
            try:
                TrainerSalary.objects.create(
                trainer=trainer,
                month=request.POST.get('month'),
                amount=request.POST.get('amount'),
                paid_on=request.POST.get('paid_on'),
                note=request.POST.get('note')
                )
                messages.success(request, "Salary payment recorded successfully.")
                error = "no"
            except Exception as e:
                messages.error(request, f"Error recording salary: {e}")
                error = "yes"

        return render(request, 'add_trainer_salary.html', {'trainer': trainer, 'error': error})
    else :
        return render(request, "access_denied.html")

@admin_required
def Trainer_Salary_History(request, pid):
    trainer = get_object_or_404(Trainer, id=pid)
    salary = TrainerSalary.objects.filter(trainer=trainer).order_by('-paid_on')

    return render(request, 'trainer_salary_history.html', {
        'trainer': trainer,
        'salary': salary
    })


# ================= EQUIPMENT (ADMIN OR TRAINER) =================

@staff_or_trainer_required
def Add_Equipment(request):
    error = ""
    if request.method == "POST":
        try:
            Equipment.objects.create(
                name=request.POST.get('name'),
                price=request.POST.get('price'),
                unit=request.POST.get('unit'),
                date=request.POST.get('date'),
                condition=request.POST.get('condition')
            )
            messages.success(request, "Equipment added successfully.")
            error = "no"
        except Exception as e:
            messages.error(request, f"Error adding equipment: {e}")
            error = "yes"

    return render(request, 'add_equipment.html', {'error': error})


@staff_or_trainer_required
def View_Equipment(request):
    equipment = Equipment.objects.all()
    return render(request, 'view_equipment.html', {'equipment': equipment})


@staff_or_trainer_required
def Delete_Equipment(request, pid):
    equipment = get_object_or_404(Equipment, id=pid)
    equipment.delete()
    messages.success(request, "Equipment deleted successfully.")
    return redirect('view_equipment')


# ================= PLANS =================

@admin_required
def Add_Plan(request):
    if request.session['is_admin']:
        trainer = Trainer.objects.all()
        error = ""
        if request.method == "POST":
            try:
                Plan.objects.create(
                name=request.POST.get('name'),
                amount=request.POST.get('amount'),
                duration=request.POST.get('duration')
                )
                messages.success(request, "Plan added successfully.")
                error = "no"
            except Exception as e:
                messages.error(request, f"Error adding plan: {e}")
                error = "yes"

        return render(request, 'add_plan.html', {'error': error})
    else :
        return render(request, "access_denied.html")

@staff_or_trainer_required
def View_Plan(request):
    plan = Plan.objects.all()
    return render(request, 'view_plan.html', {'plan': plan})


@admin_required
def Delete_Plan(request, pid):
    if request.session['is_admin']:

        try:
            plan = get_object_or_404(Plan, id=pid)
            plan.delete()
            messages.success(request, "Plan deleted successfully")
        except Exception:
            messages.error(request, "Plan not found or deletion failed.")

        return redirect('view_plan')
    else:
        return render(request, "access_denied.html")

# ================= MEMBERS (ADMIN OR TRAINER) =================

@staff_or_trainer_required
def Add_Member(request):
    plan = Plan.objects.all()
    error = ""

    if request.method == "POST":
        try:
            plan_id = request.POST.get('plan')
            plan_obj = get_object_or_404(Plan, id=plan_id)

            Member.objects.create(
                name=request.POST.get('name'),
                contact=request.POST.get('contact'),
                age=request.POST.get('age'),
                gender=request.POST.get('gender'),
                plan=plan_obj,
                join_date=request.POST.get('join_date'),
                renewal=request.POST.get('renewal'),
                amount=request.POST.get('amount'),
                duration=request.POST.get('duration'),
                pending_amount=request.POST.get('pending_amount'),
            )
            messages.success(request, "Member added successfully.")
            error = "no"
        except Exception as e:
            messages.error(request, f"Error adding member: {e}")
            error = "yes"

    return render(request, "add_member.html", {'plan': plan, 'error': error})


@staff_or_trainer_required
def View_Member(request):
    member = Member.objects.all()
    return render(request, 'view_member.html', {'member': member})


@staff_or_trainer_required
def Delete_Member(request, pid):
    member = get_object_or_404(Member, id=pid)
    member.delete()
    messages.success(request, "Member deleted successfully.")
    return redirect('view_member')


# ================= FEES (ADMIN OR TRAINER) =================

@staff_or_trainer_required
def Add_Fees(request, pid):
    member = get_object_or_404(Member, id=pid)
    error = ""

    if request.method == "POST":
        try:
            MemberFees.objects.create(
                member=member,
                month=request.POST.get('month'),
                amount=request.POST.get('amount'),
                paid_on=request.POST.get('paid_on'),
                note=request.POST.get('note')
            )
            messages.success(request, "Fees recorded successfully.")
            error = "no"
        except Exception as e:
            messages.error(request, f"Error adding fees: {e}")
            error = "yes"

    return render(request, 'add_fees.html', {'member': member, 'error': error})


@staff_or_trainer_required
def Member_Fees_History(request, pid):
    member = get_object_or_404(Member, id=pid)
    fees = MemberFees.objects.filter(member=member).order_by('-paid_on')

    return render(request, 'member_fees_history.html', {'member': member, 'fees': fees})


# ================= ATTENDANCE (ADMIN OR TRAINER) =================

@staff_or_trainer_required
def Mark_Attendance(request):
    members = Member.objects.all()
    today = date.today()
    error = ""

    if request.method == "POST":
        try:
            for m in members:
                status = request.POST.get(f"status_{m.id}")
                if not status:
                    # no selection for this member
                    continue
                # normalize possible values ('P'/'A' or 'Present'/'Absent')
                if status == 'P':
                    normalized = 'Present'
                elif status == 'A':
                    normalized = 'Absent'
                elif status in ['Present', 'Absent']:
                    normalized = status
                else:
                    # unexpected value — skip
                    continue

                # Create or update attendance for member on this date to avoid duplicates
                Attendance.objects.update_or_create(
                    member=m,
                    date=today,
                    defaults={'status': normalized}
                )
            messages.success(request, "Attendance marked successfully.")
            error = "no"
        except Exception as e:
            messages.error(request, f"ATTENDANCE ERROR: {e}")
            error = "yes"

    return render(request, "mark_attendance.html", {
        "members": members,
        "today": today,
        "error": error,
    })


@staff_or_trainer_required
def View_Attendance(request):
    selected_date_str = request.GET.get("date")
    # If a date is provided, parse it. Otherwise default to the most recent attendance date (if any), or today.
    if selected_date_str:
        try:
            selected_date_obj = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
        except Exception:
            selected_date_obj = None
    else:
        # Use the latest attendance date if records exist so users see data immediately
        latest_date = Attendance.objects.order_by('-date').values_list('date', flat=True).first()
        selected_date_obj = latest_date or date.today()

    # Query attendance for the selected date (if valid)
    attendance = Attendance.objects.filter(date=selected_date_obj).select_related('member') if selected_date_obj else None

    return render(request, "view_attendance.html", {
        "attendance": attendance,
        # pass a string for form value (YYYY-MM-DD) or empty string
        "selected_date": selected_date_obj.strftime('%Y-%m-%d') if selected_date_obj else ''
    })