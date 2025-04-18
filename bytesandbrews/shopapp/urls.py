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

    



    
    # Add other shop app URLs here 
]