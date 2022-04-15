from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Доступ на чтение для всех.
    Изменение и удаление - только авторам рецепта.
    """

    message = 'У вас недостаточно прав для выполнения данной операции!'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user
