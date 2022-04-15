from rest_framework import mixins, permissions, viewsets


class ListRetrieveCreateViewSet(mixins.CreateModelMixin,
                                mixins.RetrieveModelMixin,
                                mixins.ListModelMixin,
                                viewsets.GenericViewSet):
    """Набор представлений для модели User."""

    permission_classes = [permissions.AllowAny]


class ListRetrieveViewSet(mixins.RetrieveModelMixin,
                          mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    permission_classes = [permissions.AllowAny]
