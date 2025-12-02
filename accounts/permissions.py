from rest_framework import permissions

class IsOrganizationMember(permissions.BasePermission):
    """
    Allows access only if the requesting user belongs to the organization.
    """

    def has_object_permission(self, request, view, obj):
        # obj is an Organization
        return request.user.organization_id == obj.id


class IsOrganizationManager(permissions.BasePermission):
    """
    Allows access only to the manager of the organization.
    """

    def has_object_permission(self, request, view, obj):
        # obj is an Organization
        return obj.manager_id == request.user.id
