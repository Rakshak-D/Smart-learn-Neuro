"""
Custom permissions for the AI app.
"""
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj.user == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admin users to edit objects.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to admin users.
        return request.user and request.user.is_staff


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to view or edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Only the owner can view or edit the object.
        return obj.user == request.user


class IsAdminOrOwner(permissions.BasePermission):
    """
    Custom permission to only allow admin users or the owner to view or edit an object.
    """
    def has_object_permission(self, request, view, obj):
        # Admin users can do anything
        if request.user and request.user.is_staff:
            return True
            
        # Object owner can view or edit
        return obj.user == request.user


class HasLearningCondition(permissions.BasePermission):
    """
    Custom permission to only allow users with a specific learning condition.
    """
    def __init__(self, learning_condition):
        self.learning_condition = learning_condition

    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            hasattr(request.user, 'learning_condition') and
            request.user.learning_condition == self.learning_condition
        )


class IsContentCreator(permissions.BasePermission):
    """
    Custom permission to only allow content creators to create or modify content.
    """
    def has_permission(self, request, view):
        # Check if the user is authenticated and has the content_creator role
        return (
            request.user and 
            request.user.is_authenticated and 
            hasattr(request.user, 'role') and 
            request.user.role == 'content_creator'
        )


class CanAccessAdaptiveContent(permissions.BasePermission):
    """
    Custom permission to check if the user can access adaptive content.
    Users must have a valid subscription and not have exceeded their usage limits.
    """
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
            
        # Check subscription status
        if hasattr(user, 'subscription'):
            subscription = user.subscription
            if not subscription.is_active:
                return False
                
            # Check usage limits if applicable
            if hasattr(subscription, 'usage_limit'):
                return user.usage_count < subscription.usage_limit
                
        return True
