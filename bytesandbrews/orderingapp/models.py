from django.db import models

from django.contrib.auth.models import BaseUserManager,AbstractUser
from django.conf import settings
  
 



class AppUserManager(BaseUserManager):
    def create_user(self, email, name,phone, address, gender,password=None, cafe_name=None, location=None, year_established=None, **extra_fields):
        if not email:
            raise ValueError('The Email field is mandatory')       
        # converting email with lower case
        email= self.normalize_email(email)
        user = self.model(
            email=email,
            name=name,
            phone=phone,
            address= address,
            gender= gender,
            cafe_name=cafe_name,
            location=location,
            year_established=year_established,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
   
    def create_superuser(self, email, name, phone, address, gender, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)


        if not password:
            raise ValueError("Superusers must have a password.")
        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, name, phone, address, gender, password,**extra_fields)


class AppUser(AbstractUser):


    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )
    # redefine the email to be unique
    email = models.EmailField(unique=True)


    # Adding extra field  inside the custom user class
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    cafe_name=models.CharField(max_length=200)
    location=models.CharField(max_length=200)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    # removing the username field
    username= None
    objects = AppUserManager()
    year_established=models.IntegerField()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'phone', 'address', 'gender','cafe_name','location','year_established']


    def __str__(self):
        return self.email


def get_default_user():
    return 1




 

class Menu(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,default=get_default_user)
    category = models.CharField(max_length=100)
    subcategory = models.CharField(max_length=100)
    subsubcategory = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    image_path = models.CharField(max_length=200, blank=True, null=True)

    price = models.DecimalField(max_digits=6, decimal_places=2)

class InventoryItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,default=get_default_user)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    quantity = models.FloatField(default=0)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    last_updated = models.DateTimeField(auto_now=True)

class Feedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,default=get_default_user)
    custname = models.CharField(max_length=100)
    email = models.EmailField()
    rating = models.IntegerField()
    comment = models.TextField()

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,default=get_default_user)
    items = models.TextField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    gst = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

 
    
class UserSubscription(models.Model):
    PLAN_CHOICES = [
        ('FREE', 'Free'),
        ('STANDARD', 'Standard'),
        ('PRO', 'Pro'),
        ('PREMIUM', 'Premium'),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES)
    start_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.plan}"
