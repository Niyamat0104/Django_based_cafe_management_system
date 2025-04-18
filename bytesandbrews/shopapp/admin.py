from django.contrib import admin
from .models import (
    Customer, 
    Address, 
    Product, 
    ShippingMethod,
    PaymentMethod, 
    Order, 
    OrderItem
)

class AddressInline(admin.TabularInline):
    model = Address
    extra = 0

class PaymentMethodInline(admin.TabularInline):
    model = PaymentMethod
    extra = 0

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'phone', 'created_at')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    list_filter = ('receive_email_offers', 'receive_text_offers', 'created_at')
    inlines = [AddressInline, PaymentMethodInline]
    fieldsets = (
        ('Personal Information', {
            'fields': ('email', 'first_name', 'last_name', 'company', 'phone')
        }),
        ('Preferences', {
            'fields': ('receive_email_offers', 'receive_text_offers')
        }),
    )

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('customer', 'address_line1', 'city', 'state', 'zip_code', 'is_default_shipping', 'is_default_billing')
    search_fields = ('customer__email', 'customer__last_name', 'address_line1', 'city', 'state', 'zip_code')
    list_filter = ('state', 'country', 'is_default_shipping', 'is_default_billing')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'weight', 'stock_quantity', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Product Information', {
            'fields': ('name', 'description', 'price', 'weight', 'image_url')
        }),
        ('Inventory', {
            'fields': ('stock_quantity',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'estimated_delivery_time')
    search_fields = ('name',)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('total_price',)

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('customer', 'payment_type', 'card_brand', 'card_number_last_four', 'is_default')
    list_filter = ('payment_type', 'card_brand', 'is_default', 'created_at')
    search_fields = ('customer__email', 'customer__last_name', 'cardholder_name')
    
    def get_fieldsets(self, request, obj=None):
        if obj and obj.payment_type == 'credit_card':
            return (
                ('Customer', {
                    'fields': ('customer', 'payment_type', 'is_default')
                }),
                ('Credit Card Information', {
                    'fields': ('card_brand', 'card_number_last_four', 'expiration_date', 'cardholder_name')
                }),
            )
        else:
            return (
                ('Customer', {
                    'fields': ('customer', 'payment_type', 'is_default')
                }),
                ('Shop Account Information', {
                    'fields': ('has_shop_account', 'mobile_number'),
                    'classes': ('collapse',) if obj and obj.payment_type != 'shop_pay' else tuple()
                }),
            )

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer', 'status', 'subtotal', 'total', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'customer__email', 'customer__last_name')
    readonly_fields = ('order_number', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'customer', 'status')
        }),
        ('Addresses', {
            'fields': ('shipping_address', 'billing_address')
        }),
        ('Shipping & Payment', {
            'fields': ('shipping_method', 'payment_method')
        }),
        ('Financial Details', {
            'fields': ('subtotal', 'shipping_cost', 'service_fee', 'discount_amount', 
                       'discount_code', 'tax_amount', 'total')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_name', 'product_price', 'quantity', 'total_price')
    search_fields = ('order__order_number', 'product_name')
    readonly_fields = ('total_price',)

from django.contrib import admin
from .models import GiftCardType, GiftCard

@admin.register(GiftCardType)
class GiftCardTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')

@admin.register(GiftCard)
class GiftCardAdmin(admin.ModelAdmin):
    list_display = ('id', 'gift_card_type', 'recipient_name', 'recipient_email', 'recipient_phone', 'sender_name', 'message', 'password', 'code',
                   'amount', 'created_at', 'is_redeemed')
    list_filter = ('is_redeemed', 'gift_card_type')
    search_fields = ('recipient_name', 'recipient_email', 'sender_name', 'code')
    readonly_fields = ('code', 'created_at')