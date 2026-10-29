from rest_framework.permissions import BasePermission

class IsCameraAdminOrManager(BasePermission):
    message = "Only authenticated admins and managers may manage cameras."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and getattr(user, "role", None) in {"admin", "manager"})
