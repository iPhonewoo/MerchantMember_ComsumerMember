import factory
from store.models import Product
from store.models import Store

class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Sequence(lambda n: f"商品{n}")
    description = "測試商品描述"
    price = 99.99
    stock = 10
    store = factory.SubFactory("tests.factories.store_factory.StoreFactory")
