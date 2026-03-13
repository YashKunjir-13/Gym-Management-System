from django.db import models
from datetime import date


# ======================= TRAINER =======================

class Trainer(models.Model):
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=10)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    salary = models.IntegerField()


    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class TrainerSalary(models.Model):
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE)
    month = models.CharField(max_length=20)
    amount = models.IntegerField()
    paid_on = models.DateField()
    note = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.trainer.name} ({self.month})"

    class Meta:
        ordering = ["-paid_on"]


# ======================= EQUIPMENT =======================

class Equipment(models.Model):
    name = models.CharField(max_length=100)
    price = models.IntegerField()
    unit = models.IntegerField()
    date = models.DateField()
    condition = models.CharField(max_length=50, default="Working")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


# ======================= PLAN =======================

class Plan(models.Model):
    name = models.CharField(max_length=50, unique=True)
    amount = models.IntegerField()
    duration = models.IntegerField()   # in months

    def __str__(self):
        return f"{self.name} ({self.duration} months)"

    class Meta:
        ordering = ["duration"]


# ======================= MEMBER =======================

class Member(models.Model):
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=10)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)

    plan = models.CharField(max_length=30)

    join_date = models.DateField()
    renewal = models.DateField()

    amount = models.IntegerField()
    duration = models.IntegerField()
    pending_amount = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


# ======================= MEMBER FEES =======================

class MemberFees(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    month = models.CharField(max_length=20)
    amount = models.IntegerField()
    paid_on = models.DateField()
    note = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.member.name} - {self.month}"

    class Meta:
        ordering = ["-paid_on"]


# ======================= ATTENDANCE =======================

class Attendance(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    date = models.DateField(default=date.today)
    status = models.CharField(max_length=10)  # Present / Absent

    def __str__(self):
        return f"{self.member.name} - {self.date} - {self.status}"

    class Meta:
        ordering = ["-date"]
