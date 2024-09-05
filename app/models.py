from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal


class SKU(models.Model):
    code = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.code

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    sku = models.ForeignKey(SKU, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    supplier = models.CharField(max_length=100)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_in_stock = models.PositiveIntegerField()
    expiry_date = models.DateField()

    def __str__(self):
        return self.name



class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    sale_date = models.DateTimeField(auto_now_add=True)

    @property
    def total_price(self):
        return self.product.selling_price * Decimal(self.quantity)

    @property
    def tax(self):
        return self.total_price * Decimal('0.18')

    @property
    def total_with_tax(self):
        return self.total_price + self.tax

    @property
    def profit(self):
        cost_price = self.product.purchase_price * Decimal(self.quantity)
        return self.total_price - cost_price

    def __str__(self):
        return f'Sale of {self.product.name} on {self.sale_date}'

class InventoryLog(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    change_in_quantity = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.change_in_quantity} units of {self.product.name} on {self.timestamp}'

