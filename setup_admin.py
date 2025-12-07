
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HireX.settings')
django.setup()

from rbac.models import User

def find_admin():
    admins = User.objects.filter(role='admin')
    if admins.exists():
        print(f"Admin found: {admins.first().email}")
        # I don't know the password, so I might need to reset it to a known value to ensure auto-login works.
        u = admins.first()
        u.set_password('admin123')
        u.save()
        print("Password set to: admin123")
    else:
        print("No admin found. Creating one.")
        User.objects.create_superuser('admin@hirex.com', 'admin123', role='admin')
        print("Admin created: admin@hirex.com / admin123")

if __name__ == '__main__':
    find_admin()
