
from rest_framework import viewsets
from rest_framework.permissions import (
    AllowAny,
    IsAdminUser,
    IsAuthenticated
)

from .models import Product, Order

from .serializers import (
    ProductSerializer,
    OrderSerializer,
    OrderCreateSerializer
)


# PRODUCT API
class ProductViewSet(viewsets.ModelViewSet):

    queryset = Product.objects.all().order_by('-id')

    serializer_class = ProductSerializer

    def get_permissions(self):

        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]

        return [permission() for permission in permission_classes]


# ORDER API
class OrderViewSet(viewsets.ModelViewSet):

    serializer_class = OrderSerializer

    def get_queryset(self):

        if self.request.user.is_staff:
            return Order.objects.all().order_by('-id')

        return Order.objects.filter(
            user=self.request.user
        ).order_by('-id')

    def get_permissions(self):

        if self.action in ['list', 'retrieve', 'create']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]

        return [permission() for permission in permission_classes]

    def get_serializer_class(self):

        if self.action == 'create':
            return OrderCreateSerializer

        return OrderSerializer
