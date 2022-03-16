from rest_framework import permissions


class AuthorPermission(permissions.BasePermission):
    """ Check the author of the photo
    """

    def has_object_permission(self, request, view, obj):
        if request.method == 'post':
            return True

        return request.user == obj.author
