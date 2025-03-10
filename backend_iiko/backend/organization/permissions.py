from rest_framework.permissions import BasePermission, SAFE_METHODS

from .models import Chain, Organization, Restaurant


class IsAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj: Organization):
        if request.method in SAFE_METHODS:
            return True

        return bool(obj.authors.filter(id=request.user.id).exists())


class IsAuthorInChainOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj: Chain):
        if request.method in SAFE_METHODS:
            return True

        return bool(obj.organization.authors.filter(id=request.user.id).exists())


class IsAuthorInRestaurantOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj: Restaurant):
        if request.method in SAFE_METHODS:
            return True

        return bool(obj.chain.organization.authors.filter(id=request.user.id).exists())
