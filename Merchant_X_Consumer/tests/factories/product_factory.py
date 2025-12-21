import factory
from store.models import Product
from .store_factory import StoreFactory


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    store = factory.SubFactory(StoreFactory)
    name = factory.Sequence(lambda n: f"測試商品{n}")
    description = "這是一個測試商品"
    price = 99.99
    stock = 10

