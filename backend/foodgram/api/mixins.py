from rest_framework import mixins, permissions, viewsets


class ListRetrieveViewSet(mixins.RetrieveModelMixin,
                          mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    permission_classes = [permissions.AllowAny]
