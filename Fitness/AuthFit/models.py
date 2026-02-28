from django.db import models

# Create your models here.
class Contact(models.Model):
    name = models.CharField(max_length=25)
    email = models.EmailField()
    phonenumber = models.CharField(max_length=10)
    description = models.TextField()

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
    ]
    Trainer = [
        ('Y','Yes'),
        ('N','No')
    ]
    fullname = models.CharField(max_length=25)
    email = models.EmailField(null=True ,blank=True)
    gender = models.CharField(max_length=1,choices=GENDER_CHOICES,default='M')
    phonenumber = models.CharField(max_length=10)
    dob = models.DateField()
    doj = models.DateTimeField()
    plan = models.CharField(max_length=1,choices=MembershipPlan,default='B')
    trainer = models.CharField(max_length=1,choices=Trainer ,default='N')
    Reference = models.CharField(max_length=30,null=True,blank=True)
    address = models.TextField()

    def __str__(self):
        return f"{self.fullname}"
