import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", ".settings")
from django.contrib.auth.models import User
User.objects.get(username="pi", is_superuser=True).delete()
