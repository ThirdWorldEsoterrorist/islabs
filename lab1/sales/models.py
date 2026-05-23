from django.db import models
from decimal import Decimal

CREDIT_DANGER = Decimal(0.9)

class Client(models.Model):
    name = models.CharField(max_length=24, unique=True)
    a_total = models.DecimalField(max_digits = 8, decimal_places = 2)
    a_current = models.DecimalField(max_digits = 8, decimal_places = 2)
    c_limit = models.DecimalField(max_digits = 8, decimal_places = 2)
    c_current = models.DecimalField(max_digits = 8, decimal_places = 2)
    @property
    def credit_remain(self):
        return self.c_limit - self.c_current
    comm = models.TextField(blank=True)

    def __str__(self):
        return self.name

    def credit_danger(self):
        if self.c_current >= (CREDIT_DANGER * self.c_limit):
            return True
        return False


# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=128)#check
    price = models.DecimalField(max_digits=8, decimal_places=2) #check
    stock = models.SmallIntegerField()

    def __str__(self):
        return self.name

class Order(models.Model):
    PAYMENT_CHOICES = [
        ('cash', 'Наличный'),
        ('card', 'Безналичный'),
        ('credit', 'Кредитный'),
        ('barter', 'Бартер'),
        ('return', 'Взаимозачёт')
    ]
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    payment = models.CharField(max_length=16, choices=PAYMENT_CHOICES, default='cash')
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def get_items(self):
        # Возвращает все позиции этого заказа
        return OrderItem.objects.filter(order=self)

    @property
    def get_total_cost(self):
        # Считает общую сумму всех товаров в заказе
        items = self.get_items
        return sum(item.product.price * item.quantity for item in items)

    def process_payment(self, total_sum, barter_items_in=None):
        client = self.client

        if (self.payment == 'cash'):
            client.a_total += total_sum
            # Товары уменьшаются в цикле OrderItem (см. views.py)

        elif (self.payment == 'card'):
            client.a_total += total_sum
            client.a_current -= total_sum

        elif (self.payment == 'credit'):
            client.c_current += total_sum

        # бартер реализуется в html-скрипте в силу более простой реализации
        elif (self.payment == 'return'):
            client.c_current -= total_sum

        client.save()

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
