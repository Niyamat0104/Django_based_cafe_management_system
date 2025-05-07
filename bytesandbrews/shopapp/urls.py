from django.urls import path
from . import views

app_name = 'shop_app'

urlpatterns = [
    path('', views.shopapp_main_view, name="merch-home"),
    path('merchandiseapp/',views.merchandise_view,name="merchandise"),
    path('deluxe/',views.deluxe_view,name="deluxe"),
    path('conisseur/',views.conisseur_view,name="conisseur"),
    path('starterpack/',views.starter_pack,name="starter_pack"),
    path('about/',views.about_view,name="about"),
    path("coffeepack",views.coffee_pack,name="coffee_pack"),
   

 
    path('gift-card-home', views.gift_cards_view, name='gift_cards'),
    path('gift-cards/create/', views.create_gift_card, name='create_gift_card'),
    path('gift-cards/success/<int:order_id>/', views.order_success, name='order_success'),
    path('checkoutcoffee/', views.checkout, name='checkoutcoffee'),
    path('process_payment/',views.process_payment,name="process-payment"),
    path('order-confirmation/<str:order_number>/', views.order_confirmation, name='order_confirmation'),
    path('gift-cards/', views.gift_card_history, name='gift_card_history'),
    path('gift-cards/<int:id>/delete/', views.delete_gift_card, name='delete_gift_card'),
    path('gift_card/edit/<int:id>/', views.edit_gift_card, name='edit_gift_card'),
    path('orders/', views.order_history, name='order_history'),
    path('orders/<str:order_number>/', views.order_detail, name='order_detail'),
    path('order/cancel/', views.cancel_order, name='cancel_order'),
    path('/customhampers/',views.custom_hampers_view,name="custom_hampers")
   

    



    
    # Add other shop app URLs here 
]