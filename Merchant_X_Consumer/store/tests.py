from django.test import TestCase
from store.models import User, Order
from django.urls import reverse
from rest_framework import status

# Create your tests here.
class UserOrderTestCase(TestCase):
    def setUp(self):
        user1 = User.objects.create_user(username='user1', password='pass')
        user2 = User.objects.create_user(username='user2', password='pass')
        order1 = Order.objects.create(user=user1)
        order3 = Order.objects.create(user=user1)
        order2 = Order.objects.create(user=user2)
        order4 = Order.objects.create(user=user2)
    def test_user_order_endpoint_retrieves_only_authenticated_user_orders(self):
        user = User.objects.get(username='user2')
        self.client.force_login(user) # 模擬用戶登入
        response = self.client.get(reverse('user-orders')) 

        assert response.status_code == status.HTTP_200_OK 
        data = response.json() 
        self.assertTrue(all(order['user'] == user.id for order in data)) # 確保所有返回的訂單都屬於該用戶

    def test_user_order_list_unauthenticated(self):
        response = self.client.get(reverse('user-orders')) # 未登入狀態下訪問
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  # 應該返回403禁止訪問