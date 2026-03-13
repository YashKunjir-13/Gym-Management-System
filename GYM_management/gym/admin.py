from django.contrib import admin
from .models import (
    Trainer, TrainerSalary,
    Plan, Member, MemberFees,
    Equipment, Attendance
)

# ================= TRAINER =================

@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "contact", "age", "gender", "salary")
    search_fields = ("name", "contact")
    list_filter = ("gender",)


@admin.register(TrainerSalary)
class TrainerSalaryAdmin(admin.ModelAdmin):
    list_display = ("id", "trainer", "month", "amount", "paid_on")
    list_filter = ("trainer", "month")
    search_fields = ("trainer__name", "month")
    ordering = ("-paid_on",)


# ================= PLAN =================

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "amount", "duration")
    search_fields = ("name",)
    ordering = ("duration",)


# ================= MEMBER =================

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "contact", "plan", "join_date", "renewal", "pending_amount")
    list_filter = ("plan", "gender")
    search_fields = ("name", "contact")
    ordering = ("name",)


@admin.register(MemberFees)
class MemberFeesAdmin(admin.ModelAdmin):
    list_display = ("id", "member", "month", "amount", "paid_on")
    search_fields = ("member__name", "month")
    list_filter = ("month",)
    ordering = ("-paid_on",)


# ================= EQUIPMENT =================

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "unit", "date", "condition")
    search_fields = ("name",)
    list_filter = ("condition",)
    ordering = ("name",)


# ================= ATTENDANCE =================

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("id", "member", "date", "status")
    list_filter = ("date", "status")
    search_fields = ("member__name", "status")
    ordering = ("-date",)
