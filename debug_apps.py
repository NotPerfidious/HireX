import os
import django
import sys

# Add the project root to sys.path
sys.path.append(r'f:\5th Semester\SDA\HireX Project Gemini - Copy - Copy\HireX')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HireX.settings')
django.setup()

from jobs.models import Application
from jobs.serializers import ApplicationSerializer

apps = Application.objects.all()
print(f"Total applications: {apps.count()}")
for app in apps:
    print(f"ID: {app.id}, By: {app.applied_by}, Job: {app.applied_for}, Resume: {app.resume}")
    output = ApplicationSerializer(app).data
    print("Serialized:", output)
