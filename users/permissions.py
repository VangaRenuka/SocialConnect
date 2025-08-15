from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner
        return obj == request.user


class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin()


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners or admins.
    """
    
    def has_object_permission(self, request, view, obj):
        # Admin can do anything
        if request.user.is_admin():
            return True
        
        # Owner can edit their own content
        if hasattr(obj, 'author'):
            return obj.author == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False


class IsPublicProfileOrOwner(permissions.BasePermission):
    """
    Custom permission for profile visibility.
    """
    
    def has_object_permission(self, request, view, obj):
        # Owner can always view/edit
        if obj == request.user:
            return True
        
        # Check profile visibility
        return obj.can_view_profile(request.user)


