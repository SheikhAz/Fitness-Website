import random
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# Create your models here.


class Contact(models.Model):
    name = models.CharField(max_length=25)
    email = models.EmailField()
    phonenumber = models.CharField(max_length=10)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.name


class Trainer(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    name = models.CharField(max_length=30)
    gender = models.CharField(
        max_length=1, choices=GENDER_CHOICES, default='M')
    address = models.TextField()
    phone = models.CharField(max_length=10)
    salary = models.IntegerField()

    def __str__(self):
        return self.name


class MembershipPlan(models.Model):
    plan = models.CharField(max_length=100)
    price = models.IntegerField()

    def __str__(self):
        return f"{self.plan} - ₹{self.price}"


class Enrollment(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    PAYMENT = [
        ("Done", 'Done'),
        ("Pending", 'Pending'),
    ]
    METHOD = [
        ('C', 'CASH'),
        ('U', 'UPI'),
        ('B', 'UPI + CASH'),
    ]
    unique_id = models.CharField(max_length=4 , unique=True,editable=False ,db_index=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=25)
    email = models.EmailField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    phone = models.CharField(max_length=10,db_index=True)
    dob = models.DateField()
    selectPlan = models.ForeignKey(
        MembershipPlan, on_delete=models.CASCADE, related_name="enrollments")
    trainer = models.ForeignKey(
        Trainer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="enrollments"
    )
    Reference = models.CharField(max_length=30, null=True, blank=True)
    address = models.TextField()
    paymentStatus = models.CharField(
        max_length=10, choices=PAYMENT, blank=True, null=True)
    Amount = models.CharField(max_length=10)
    paymentMethod = models.CharField(
        max_length=1, choices=METHOD, blank=True, null=True)
    doj = models.DateField(auto_now_add=True,null=True, blank=True)
    DueDate = models.DateField(blank=True, null=True)

    def generate_unique_id(self):
        while True:
            random_id = str(random.randint(1000,9999))
            if not Enrollment.objects.filter(unique_id = random_id).exists():
                return random_id


    @property
    def is_expired(self):
        if self.DueDate:
            return timezone.now().date() >= self.DueDate
        return False


    @property
    def days_remaining(self):
        if self.DueDate:
            remaining = (self.DueDate - timezone.now().date()).days
            return remaining
        return None

    def save(self,*args, **kwargs):
        from django.utils import timezone

        if not self.unique_id:
            self.unique_id = self.generate_unique_id()

        if self.DueDate and timezone.now().date() > self.DueDate:
            self.paymentStatus = "Pending"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.unique_id} - {self.fullname}"


class Gallery(models.Model):
    title = models.CharField(max_length=100)
    images = models.ImageField(upload_to='gallery')
    timestamp = models.DateTimeField(auto_now_add=True ,blank=True)

    def __str__(self):
        return self.title
    

class Attendence(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.localdate)
    timestamp = models.TimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user','date')

    def __str__(self):
        if hasattr(self.user, "enrollment"):
            return f"{self.user.enrollment.unique_id}"
        return f"{self.user.username} - {self.date}"
