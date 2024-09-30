from rest_framework.permissions import BasePermission

class IsInGroup(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        #obtener nombre del grupo de usuario
        user_groups = request.user.groups.values_list('name', flat=True)

        #grupos permitidos
        allowed_groups = view.allowed_groups if hasattr(view, 'allowed_groups') else []

        return any(group in user_groups for group in allowed_groups)
