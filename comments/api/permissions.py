from rest_framework.permissions import BasePermission


class IsObjectOwner(BasePermission):
    """
    This Permission is responsible for checking if obj.user == request.user
    Permission will be executed one by one
     - If it is an action with detail=False, only check has_permission
     - If it is an action with detail=True, check both has_permission and
       has_object_permission
    If there is an error, the default error message will display the content of
    IsObjectOwner.message
    """
    message = "You do not have permission to access this object."

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user

