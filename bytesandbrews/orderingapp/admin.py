from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Menu, InventoryItem, Feedback, Order ,UserSubscription

from .models import AppUser

 
class AppUserAdmin(UserAdmin):
    model = AppUser


    list_display = ('email', 'name', 'is_staff', 'is_superuser', 'gender', 'address', 'phone','cafe_name','location','year_established')
    ordering = ('email',)


    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name', 'phone', 'address', 'gender','cafe_name','location','year_established')}),
        ('Permissions', {'fields': ('is_active', 'is_staff',
         'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),


    )


    # Fields visible when creating a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'phone', 'address', 'gender','cafe_name','location','year_established', 'password1', 'password2'),
        }),
    )


admin.site.register(AppUser, AppUserAdmin)


 
class MenuAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'subcategory', 'subsubcategory', 'price')
    search_fields = ('name', 'category', 'subcategory')

 
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'quantity', 'price', 'last_updated')
    list_filter = ('category',)
    search_fields = ('name',)

 
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('custname', 'email', 'rating')
    search_fields = ('custname', 'email')
    list_filter = ('rating',)

 
class OrderAdmin(admin.ModelAdmin):
    list_display = ('date', 'subtotal', 'gst', 'total')
    readonly_fields = ('date',)
    search_fields = ('items',)
    date_hierarchy = 'date'

 
 
     
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display=["user","plan","start_date","expiry_date","is_active"]

admin.site.register(Menu,MenuAdmin)
admin.site.register(InventoryItem,InventoryItemAdmin)
admin.site.register(Feedback,FeedbackAdmin)
admin.site.register(Order,OrderAdmin)
admin.site.register(UserSubscription,UserSubscriptionAdmin)
 