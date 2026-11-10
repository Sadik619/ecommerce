
from rest_framework import serializers
from django.db import transaction

from .models import Product, Order, OrderItem


# PRODUCT SERIALIZER
class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


# ORDER ITEM SERIALIZER (FOR DISPLAYING ORDERS)
class OrderItemSerializer(serializers.ModelSerializer):

    product_name = serializers.CharField(
        source='product.name',
        read_only=True
    )

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'product',
            'product_name',
            'quantity',
            'price'
        ]


# ORDER SERIALIZER (FOR GET REQUESTS)
class OrderSerializer(serializers.ModelSerializer):

    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'total_amount',
            'status',
            'created_at',
            'items'
        ]
    

        read_only_fields = [
            'user',
            'total_amount',
            'created_at'
        ]


# ORDER ITEM INPUT SERIALIZER (FOR POST REQUESTS)
class OrderItemCreateSerializer(serializers.Serializer):

    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all()
    )

    quantity = serializers.IntegerField(min_value=1)


# ORDER CREATE SERIALIZER
class OrderCreateSerializer(serializers.ModelSerializer):

    items = OrderItemCreateSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'items']
        read_only_fields = ['id']

    def create(self, validated_data):

        items_data = validated_data.pop('items')

        with transaction.atomic():

            total_amount = 0
            products = []

            # Check stock and calculate total
            for item in items_data:

                product = Product.objects.select_for_update().get(
                    id=item['product'].id
                )

                quantity = item['quantity']

                if product.stock < quantity:
                    raise serializers.ValidationError({
                        'stock': f'Insufficient stock for {product.name}'
                    })

                total_amount += product.price * quantity

                products.append((product, quantity))

            # Create order
            order = Order.objects.create(
                user=self.context['request'].user,
                total_amount=total_amount
            )

            # Create order items and update stock
            for product, quantity in products:

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price
                )

                product.stock -= quantity

                product.save(update_fields=['stock'])

        return order
    
    def to_representation(self, instance):
        return OrderSerializer(
            instance,
            context=self.context
        ).data
