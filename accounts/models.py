from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

class Organization(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    manager = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_organizations'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'organizations'
        ordering = ['name']

    def clean(self):
        """
        Ensures: If a manager is assigned, that manager must belong
        to this organization.
        This works across ALL database backends.
        """
        if self.manager:
            if self.manager.organization_id != self.id:
                raise ValidationError("Manager must be a member of this organization.")

    def save(self, *args, **kwargs):
        # Always run clean() before saving
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class User(AbstractUser):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='members'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'name']
    
    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['organization', 'email']),
        ]
    
    def __str__(self):
        return self.email


class File(models.Model):
    name = models.CharField(max_length=255)
    path = models.CharField(max_length=1024)
    folder = models.ForeignKey('Folder', on_delete=models.CASCADE, null=True, blank=True, related_name='files')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_files')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='files')
    size = models.BigIntegerField(default=0)
    mime_type = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'files'
        indexes = [
            models.Index(fields=['folder', 'name']),
            models.Index(fields=['organization', 'created_at']),
            models.Index(fields=['owner']),
        ]
    
    def __str__(self):
        return self.name

class Folder(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_folders')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='folders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'folders'
        indexes = [
            models.Index(fields=['parent', 'name']),
            models.Index(fields=['organization', 'created_at']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['parent', 'name', 'organization'],
                name='unique_folder_name_per_parent'
            ),
        ]
    
    def __str__(self):
        return self.name