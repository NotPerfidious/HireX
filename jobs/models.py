from django.db import models
from rbac.models import Candidate, Interviewer # Assuming these models are correct
from django.utils import timezone # Import for setting default times
from django.core.validators import MinValueValidator, MaxValueValidator # Import for better validation

APPLICATION_STATUS_CHOICES = (
    ('pending', 'Pending Review'),
    ('shortlisted', 'Shortlisted'),
    ('rejected', 'Rejected'),
    ('interview', 'Scheduled for Interview'),
    ('hired', 'Hired'),
)

class Skill(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name'] 

class JobPost(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    skills = models.ManyToManyField(Skill, related_name='job_posts')
    posted_date = models.DateTimeField(default=timezone.now) 
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class Application(models.Model):
    description = models.TextField(blank=True, null=True) 
    applied_by = models.ForeignKey(
        Candidate, 
        on_delete=models.CASCADE,
        related_name='applications'
    )
    applied_for = models.ForeignKey(
        JobPost, 
        on_delete=models.CASCADE,
        related_name='applications'
    )
    status = models.CharField(
        max_length=20, 
        choices=APPLICATION_STATUS_CHOICES,
        default='pending',
        db_index=True 
    )
    applied_date = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('applied_by', 'applied_for')
        ordering = ['-applied_date']
    def __str__(self):
        return f"{self.applied_by.full_name} applied for {self.applied_for.title}"

class Feedback(models.Model):
    feedback = models.TextField()
    
    rating = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)] # Ensure rating is 0-5
    ) 
    reviewer = models.ForeignKey(
        Interviewer, 
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
        related_name='given_feedback'
    )
    
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Rating: {self.rating}/5"


class Interview(models.Model):
    application = models.ForeignKey(
        Application, 
        on_delete=models.CASCADE,
        related_name='interviews'
    )
    interviewer = models.ForeignKey(
        Interviewer,
        on_delete=models.SET_NULL, 
        null=True,
        related_name='interviews_assigned'
    )

    date = models.DateField()
    start_time = models.DateTimeField(default=timezone.now)
    duration = models.IntegerField(help_text="Duration in minutes")
    feedback = models.OneToOneField(
        Feedback, 
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
        related_name='interview_result'
    )
    
    def __str__(self):
        return f"Interview for {self.application.applied_for.title} on {self.date}"