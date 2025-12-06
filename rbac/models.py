from django.contrib.auth.models import AbstractUser
from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class User(AbstractUser):
    full_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Django hashes this
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('hr', 'HR'),
        ('interviewer', 'Interviewer'),
        ('candidate', 'Candidate'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]  # Django still requires username internally

    def __str__(self):
        return f"{self.email} ({self.role})"


class Hr(User):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)


class Candidate(User):
    job_role = models.CharField(max_length=50)


class Interviewer(User):
    no_of_interviews_taken = models.IntegerField(default=0)


class SoftwareAdmin(User):
    pass
