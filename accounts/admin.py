from django.contrib import admin
from .models import User, Organization, ContentType, AccessControlEntry

# Register your models here.
admin.site.register(User)
admin.site.register(Organization)
admin.site.register(ContentType)
admin.site.register(AccessControlEntry)