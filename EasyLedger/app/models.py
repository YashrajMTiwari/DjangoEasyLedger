from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField()
    shop_owner = models.ForeignKey(User, related_name='customers', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    shop_owner = models.ForeignKey(User, related_name='products', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Purchase(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    purchase_date = models.DateField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.BooleanField(default=False)

    def clean(self):
        if not self.product:
            raise ValidationError('Product is required.')

        if self.product.shop_owner != self.customer.shop_owner:
            raise ValidationError("Product and customer do not belong to the same shop owner.")

        if self.quantity <= 0:
            raise ValidationError("Quantity must be greater than 0.")

        self.total_amount = self.product.price * self.quantity  # Calculate total amount

    def save(self, *args, **kwargs):
        self.clean()  # Ensure validation
        super().save(*args, **kwargs)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    whatsapp_number = models.CharField(max_length=15, blank=True, null=True)  # Added WhatsApp number

    def __str__(self):
        return self.user.username
