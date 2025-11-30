from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class Organization(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'organizations'
        ordering = ['name']
    
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

class AccessControlEntry(models.Model):
    # Generic foreign key to any entity
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    entity = GenericForeignKey('content_type', 'object_id')
    
    # Either user OR organization, not both
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='permissions')
    organization = models.ForeignKey(Organization, null=True, blank=True, on_delete=models.CASCADE, related_name='permissions')
    
    # Permissions
    can_read = models.BooleanField(default=False)
    can_write = models.BooleanField(default=False)
    can_execute = models.BooleanField(default=False)
    
    # Metadata
    granted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='granted_permissions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'access_control_entries'
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['user', 'content_type']),
            models.Index(fields=['organization', 'content_type']),
            models.Index(fields=['expires_at']),
        ]
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(user__isnull=False, organization__isnull=True) |
                    models.Q(user__isnull=True, organization__isnull=False)
                ),
                name='user_or_organization_not_both'
            ),
            models.UniqueConstraint(
                fields=['content_type', 'object_id', 'user'],
                name='unique_user_entity_permission'
            ),
            models.UniqueConstraint(
                fields=['content_type', 'object_id', 'organization'],
                name='unique_org_entity_permission'
            ),
        ]
    
    def __str__(self):
        subject = self.user or self.organization
        return f"{subject} -> {self.entity}"

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