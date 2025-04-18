from django.db import models
from django.utils import timezone

from django.urls import reverse


class Customer(models.Model):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    company = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    receive_email_offers = models.BooleanField(default=False)
    receive_text_offers = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


class Address(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='addresses')
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default="United States")
    zip_code = models.CharField(max_length=20)
    is_default_shipping = models.BooleanField(default=False)
    is_default_billing = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.address_line1}, {self.city}, {self.state}"


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    weight = models.CharField(max_length=50, blank=True, null=True)  # E.g., "10oz"
    image_url = models.URLField(blank=True, null=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ShippingMethod(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_delivery_time = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return self.name


class PaymentMethod(models.Model):
    PAYMENT_TYPES = (
        ('credit_card', 'Credit Card'),
        ('paypal', 'PayPal'),
        ('shop_pay', 'Shop Pay'),
        ('google_pay', 'Google Pay'),
    )
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='payment_methods')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    
    # For credit cards
    card_number_last_four = models.CharField(max_length=4, blank=True, null=True)
    card_brand = models.CharField(max_length=20, blank=True, null=True)  # Visa, Mastercard, etc.
    expiration_date = models.CharField(max_length=7, blank=True, null=True)  # MM/YY format
    cardholder_name = models.CharField(max_length=255, blank=True, null=True)
    
    # Shop account info
    has_shop_account = models.BooleanField(default=False)
    mobile_number = models.CharField(max_length=20, blank=True, null=True)
    
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_payment_type_display()} - {self.customer}"


class Order(models.Model):
    ORDER_STATUS = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, related_name='orders')
    shipping_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, related_name='shipping_orders')
    billing_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, related_name='billing_orders')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True)
    shipping_method = models.ForeignKey(ShippingMethod, on_delete=models.SET_NULL, null=True)
    
    order_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    service_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount_code = models.CharField(max_length=50, blank=True, null=True)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order #{self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate an order number if one doesn't exist
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            self.order_number = f"ONX-{timestamp}"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=255)  # Store at time of purchase
    product_price = models.DecimalField(max_digits=10, decimal_places=2)  # Store at time of purchase
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity} x {self.product_name} in {self.order}"
    
    def save(self, *args, **kwargs):
        self.total_price = self.product_price * self.quantity
        super().save(*args, **kwargs)

 

class GiftCardType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.CharField(max_length=200)  # Changed to ImageFiel
    price = models.DecimalField(max_digits=6, decimal_places=2)
    is_active = models.BooleanField(default=True)
 
    
    def __str__(self):
        return self.name

class GiftCard(models.Model):
    gift_card_type = models.ForeignKey(GiftCardType, on_delete=models.CASCADE)
    recipient_name = models.CharField(max_length=100)
    recipient_email = models.EmailField()
    recipient_phone = models.CharField(max_length=15, blank=True, null=True)  # Optional phone number
    sender_name = models.CharField(max_length=100)
    message = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    password = models.CharField(max_length=16)
    code = models.CharField(max_length=16, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_redeemed = models.BooleanField(default=False)
    delivery_date = models.DateField(blank=True, null=True)  # Optional delivery date
    
    def __str__(self):
        return f"Gift Card #{self.id} - {self.recipient_name}"

 