import factory
from decimal import Decimal
from store.models import Order, OrderItem
from .user_factory import MemberFactory
from .product_factory import ProductFactory


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    member = factory.SubFactory(MemberFactory)
    receiver_name = factory.LazyAttribute(lambda o: o.member.name)
    receiver_phone = "0912345678"
    address = "高雄市測試區測試路 1 號"
    note = ""
    status = Order.StatusChoices.PENDING
    total_amount = Decimal("0.00")


class OrderItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrderItem

    order = factory.SubFactory(OrderFactory)
    product = factory.SubFactory(ProductFactory)
    quantity = 1
    price_at_purchase = factory.LazyAttribute(lambda o: o.product.price)
