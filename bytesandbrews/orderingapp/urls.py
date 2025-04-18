from django.urls import path
from . import views
app_name = 'order_app'
urlpatterns = [
    path('', views.home, name='order-home'),
    path('menu/', views.menu_view, name='order-menu'),
    path('ordernow/', views.order_now, name='ordernow'),
    path('learnmore/', views.learn, name='learn'),
    path('order_selection/<int:id>/', views.order_selection, name='order_selection'),
    path("drinks/",views.drinks,name="drinks"),
    path("bestsellers/",views.bestsellers,name="bestsellers"),
    path("chocolate/",views.chocolate,name="chocolate"),
    path("desserts/",views.desserts,name="desserts"),
    path("cookies/",views.cookies,name="cookies"),
    path("food/",views.food,name="food"),
    path("cart/",views.cart,name="cart"),
    path("payment/",views.payment,name="payment"),
    path("paymentsuccessfull/",views.payment_successfull,name="payment_successfull"),
    path("admin/",views.admin,name="admin"),
    path("feedback/",views.feedback,name="feedback"),
    path("loginadmin/",views.login_signup_page,name="loginadmin"),
    path("dashboard/<int:id>",views.dashboard,name="dashboard"),
    path("conatct_us/",views.contact_view,name="contact"),
    path("about_us/",views.about_view,name="about"),
    path("logout/",views.logout_view,name="logout"),
    path('update-staff-status/', views.update_staff_status, name='update_staff_status'),
    path("profile/<int:id>/",views.profile,name="profile"),
    path("reviews/",views.reviews_view,name="reviews"),
    path("deletemenuitem/<int:id>/",views.delete_menu_item_view,name="deletemenuitem"),
    path("updatemenuitem/<int:id>/",views.upadte_menu_item_view,name="updatemenuitem"),
    path("superadmindashboard/",views.superadmin_view,name="superadmin"),
     path("redeem_gift_card/",views.redeem_gift_card,name="redeem_gift_card"),
     path("order_history/",views.order_history,name="order_history")



    


   
]
