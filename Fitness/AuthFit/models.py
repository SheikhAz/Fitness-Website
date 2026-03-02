from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Contact(models.Model):
    name = models.CharField(max_length=25)
    email = models.EmailField()
    phonenumber = models.CharField(max_length=10)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.name
    
class Enrollment(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    MembershipPlan = [
        ('B' ,'Basic'),
        ('P' ,'Popular'),
        ('A' ,'Annual'),
        ('T' ,'TRIAL'),
    ]
    Trainer = [
        ('Y','Yes'),
        ('N','No')
    ]
    PAYMENT = [
        ("D",'Done'),
        ("P",'Pending'),
    ]
    AMOUNT =[
        ('1','500'),
        ('3','1300'),
        ('6','7999')
    ]
    METHOD = [
        ('C','CASH'),
        ('U','UPI'),
        ('B','UPI + CASH'),
    ]
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    fullname = models.CharField(max_length=25)
    email = models.EmailField()
    gender = models.CharField(max_length=1,choices=GENDER_CHOICES)
    phone = models.CharField(max_length=10)
    dob = models.DateField()
    plan = models.CharField(max_length=1,choices=MembershipPlan)
    trainer = models.CharField(max_length=1, choices=Trainer)
    Reference = models.CharField(max_length=30,null=True,blank=True)
    address = models.TextField()
    paymentStatus = models.CharField(max_length=1,choices=PAYMENT,blank=True,null=True)
    Amount = models.CharField(max_length=1,choices=AMOUNT,blank=True,null=True)
    paymentMethod = models.CharField(max_length=1,choices=METHOD,blank=True,null=True)
    doj = models.DateTimeField(null=True,blank=True)
    DueDate = models.DateTimeField(blank=True,null=True)


    def __str__(self):
        return f"{self.fullname}"


class Trainer(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    name = models.CharField(max_length=30)
    gender = models.CharField(max_length=1,choices=GENDER_CHOICES,default='M')
    address = models.TextField()
    phone = models.CharField(max_length=10)
    salary = models.IntegerField()

    def __str__(self):
        return self.name
