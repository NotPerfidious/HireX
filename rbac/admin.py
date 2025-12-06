from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin 
from .models import User, Hr, Candidate, Interviewer, SoftwareAdmin, Company # Import all models

# Register your models here.



admin.site.register(Company) 
admin.site.register(User)
admin.site.register(Hr)
admin.site.register(Candidate)
admin.site.register(Interviewer)
admin.site.register(SoftwareAdmin)