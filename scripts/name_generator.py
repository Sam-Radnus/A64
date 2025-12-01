import django
import os
import json
import sys

# Add project base dir to Python path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
print(PROJECT_ROOT)

sys.path.insert(0, PROJECT_ROOT)

# Set Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

django.setup()

import random
from django.contrib.auth import get_user_model

User = get_user_model()

with open("names.json", "r") as f:
    names = json.load(f)

first_names = names["first_names"]
last_names = names["last_names"]

def create_users(n):
    for i in range(1, n + 1):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        
        username = f"{first_name.lower()}.{last_name.lower()}"
        email = f"{username}@example.com"
        
        name = f"{first_name} {last_name}"
        
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": username,
                "name": name,
                "organization": None,
            }
        )

        if created:
            user.set_password("password123")
            user.save()
            print(f"Created {email}")
        else:
            print(f"Already exists {email}")

if __name__ == "__main__":
    create_users(int(sys.argv[1]))
