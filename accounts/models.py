from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    organization = models.ForeignKey('Organization', on_delete = models.CASCADE, null = True, blank = True)

    def __str__(self):
        return self.name

class Organization(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    manager = models.ForeignKey('User', on_delete = models.CASCADE, null = True, blank = True)

    def __str__(self):
        return self.name

class AccessControlEntry(models.Model):
    entity_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    entity_id = models.PositiveIntegerField()
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, null=True, on_delete=models.CASCADE)

    can_read = models.BooleanField(default=False)
    can_write = models.BooleanField(default=False)
    can_execute = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["entity_type", "entity_id"]),
            models.Index(fields=["user"]),
            models.Index(fields=["organization"]),
        ]
