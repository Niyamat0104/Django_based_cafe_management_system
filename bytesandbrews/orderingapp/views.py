from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from orderingapp.models import Order
import json 

from django.contrib import messages
from .models import *
 
from collections import defaultdict
from .models import Menu
from . models import Feedback
from collections import defaultdict
from django.contrib.auth import get_user_model
User = get_user_model()

from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
from shopapp.models import GiftCard
import json

from twilio.rest import Client
import decimal

from django.db.models import Count, Sum
import requests

# Twilio credentials (from your console)
account_sid = 'AC4056bdd967749c0e84df8ee374e2db7c'
auth_token = 'd4ea0c4b2b9b5052f3f3b8a80f3456cb'
client = Client(account_sid, auth_token)

# Your Twilio WhatsApp-enabled number
twilio_whatsapp_number = 'whatsapp:+14155238886'

flask_api='http://Niyamat.pythonanywhere.com'

# List of recipients (they must have joined sandbox or be approved in production)
@login_required
def order_history(request):
    response=requests.get(f'{flask_api}/orderresource').json()
    return render(request,'order_history.html',{"orders":response})

@csrf_exempt
def redeem_gift_card(request):
    if request.method == 'POST':
        try:
            # Get form data
            email = request.POST.get('email')
            code = request.POST.get('code')
            password = request.POST.get('password')
            phone = request.POST.get('phone')
            
            # Get order details
            cart_data = request.POST.get('cart_data', '[]')
            subtotal = request.POST.get('subtotal', '₹0')
            gst = request.POST.get('gst', '₹0')
            total = request.POST.get('total', '₹0')
            
            # Clean the price strings to get numerical values
            subtotal_clean = subtotal.replace('₹', '').replace(',', '').strip()
            gst_clean = gst.replace('₹', '').replace(',', '').strip()
            total_clean = total.replace('₹', '').replace(',', '').strip()
            
            try:
                subtotal_value = Decimal(subtotal_clean)
                gst_value = Decimal(gst_clean)  
                total_value = Decimal(total_clean)
            except Exception as e:
                messages.error(request, f'Invalid price format: {str(e)}. Please try again.')
                return redirect('order_app:payment')
            
            # Query for the gift card
            try:
                gift_card = GiftCard.objects.get(
                    recipient_email=email,
                    code=code,
                    password=password,
                    recipient_phone=phone,
                    is_redeemed=False
                )
                
                # Check if the gift card has enough balance
                if gift_card.amount >= total_value:
                    # Update the gift card
                    gift_card.amount = gift_card.amount - total_value
                    
                    # If balance becomes zero, mark as redeemed
                    if gift_card.amount <= 0:
                        gift_card.is_redeemed = True
                    
                    # Save the gift card changes
                    gift_card.save()
                    
                    # Process the order (you might want to store order details here)
                    cart_items = json.loads(cart_data)
                    # Here you would typically create an Order object
                    # and save it to the database
                    
                    messages.success(request, 'Payment successful! Your gift card was redeemed.')
                    
                    # Send WhatsApp notification if Twilio is configured
                    try:
                        # Make sure gift_card.phone has the proper format for Twilio
                        recipient = f'whatsapp:{gift_card.recipient_phone}'
                        message_body = f'Hello! {gift_card.recipient_name}, your gift card with code: {gift_card.code} has recently been used for the purchase of items worth ₹{total_value}. Amount left on the gift card is ₹{gift_card.amount}'
                        
                        # Send the message using Twilio
                        client.messages.create(
                            body=message_body,
                            from_=twilio_whatsapp_number,
                            to=recipient
                        )
                    except Exception as twilio_error:
                        # Log Twilio error but don't stop the checkout process
                        print(f"WhatsApp notification error: {str(twilio_error)}")
                    
                    return redirect('order_app:payment_successfull')
                else:
                    # Not enough balance
                    messages.error(request, f'Insufficient gift card balance. Your gift card has ₹{gift_card.amount} but your order total is ₹{total_value}')
                    return redirect('order_app:payment')
                    
            except GiftCard.DoesNotExist:
                # Gift card not found or already redeemed
                messages.error(request, 'Invalid gift card details. Please check your information and try again.')
                return redirect('order_app:payment')
                
        except Exception as e:
            # Handle any other errors
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('order_app:payment')
    
    # If not POST request, redirect to payment page
    return redirect('order_app:payment')


def menu_view(request):
    response = requests.get(f'{flask_api}/all_items_in_menu_resource')
    data = response.json()

    # 'ALL MENU ITEMS' is a list of dictionaries
    menu_items = data.get("ALL MENU ITEMS", [])
    menu_data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    # Fix: use dictionary key access instead of dot access
    for item in menu_items:
        menu_data[item['category']][item['subcategory']][item['subsubcategory']].append(item)

    
         

    # Convert to regular dict to make it template-safe
    def recursive_dict(d):
        if isinstance(d, defaultdict):
            d = {k: recursive_dict(v) for k, v in d.items()}
        return d

    context = {
        'menu_data': recursive_dict(menu_data),
        'user': request.user,
    }

    return render(request, 'menu1.html', context)
def home(request):
     return render(request,"index.html")

def order_now(request):
     return render(request,"order_now.html")

def learn(request):
     return render(request,"learn.html")

def order_selection(request,id):
    response=requests.get(f'{flask_api}/product/{id}')
    item=response.json()

    return render(request,"order_selection.html",{"item":item})

def drinks(request):
    return render(request,"drinks.html")

def bestsellers(request):
    return render(request,"bestsellers.html")
 
def chocolate(request):
    return render(request,"chocolates.html")

def desserts(request):
    return render(request,"desserts.html")
def cookies(request):
    return render(request,"cookies.html")

def food(request):
    return render(request,"food.html")

def cart(request):
    return render(request,"cart.html")
def payment(request):
    if request.method == 'POST':
        # Get cart data from form submission
        cart_data = request.POST.get('cart_data', '[]')
        subtotal = request.POST.get('subtotal', '0.00')
        gst = request.POST.get('gst', '0.00')
        total = request.POST.get('total', '0.00')
        
        # Parse the cart data to extract just the names
        try:
            cart_items = json.loads(cart_data)
            item_names = [item['name'] for item in cart_items]
            items_string = ', '.join(item_names)
        except:
            items_string = "Your order"
        
        # Store order in Flask API immediately
        new_order = {
            "items": items_string,
            "subtotal": subtotal,
            "gst": gst,
            "total": total
        }
        
        try:
            response = requests.post(f'{flask_api}/orderresource', json=new_order)
            response.raise_for_status()  # Raise an exception for 4XX/5XX responses
            print("Order saved successfully:", new_order)
            
            # Redirect to success page after API call succeeds
            return redirect('order_app:payment_successfull')
        except Exception as e:
            print(f"Error saving order to API: {str(e)}")
            # Still store in session as fallback
            request.session['order_items'] = items_string
            request.session['subtotal'] = subtotal
            request.session['gst'] = gst
            request.session['total'] = total
            
        context = {
            "order_items": items_string,
            "subtotal": subtotal,
            "gst": gst,
            "total": total
        }
        return render(request, "payment.html", context)
        
    else:  # GET request
        # Check if we have data in session (fallback)
        if 'order_items' not in request.session:
            return redirect('cart')
        
        items_string = request.session.get('order_items', "Your order")
        subtotal = request.session.get('subtotal', '0.00')
        gst = request.session.get('gst', '0.00')
        total = request.session.get('total', '0.00')

        # Try to store the order from session data
        new_order = {
            "items": items_string,
            "subtotal": subtotal,
            "gst": gst,
            "total": total
        }
        
        try:
            response = requests.post(f'{flask_api}/orderresource', json=new_order)
            response.raise_for_status()
            print("Order saved successfully from session:", new_order)
            
            # Clear session data
            del request.session['order_items']
            del request.session['subtotal']
            del request.session['gst']
            del request.session['total']
            
            return redirect('order_app:payment_successfull')
        except Exception as e:
            print(f"Error saving order to API: {str(e)}")
        
        context = {
            "order_items": items_string,
            "subtotal": subtotal,
            "gst": gst,
            "total": total
        }
        return render(request, "payment.html", context)

def payment_successfull(request):
    return render(request, "payment_successfull.html")

def admin(request):
    return render(request,'admin.html')

def feedback(request):
     
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")
        new_comment={
            "username" : username,
            "email" : email,
            "rating" :rating,
            "comment" :comment
        }
         
        response=requests.post(f'{flask_api}/feedbacks',json=new_comment)
        
        if response.status_code == 201:
            created_post = response.json()
            print(f"Created Post is: {created_post}")
        else:
            print(
            f"Failed to create a new post Status code: {response.status_code}")

        messages.success(request,"Feedback submitted successfully!")
         
        
         
        return redirect('order_app:ordernow')

    
    return render(request,"feedback.html")
 
@login_required
def dashboard(request,id):
     target_user = get_object_or_404(User, id=id)
     response3 = requests.get(f'{flask_api}/all_items_in_menu_resource')
     data = response3.json()

    # 'ALL MENU ITEMS' is a list of dictionaries
     menu_items = data.get("ALL MENU ITEMS", [])
     response=requests.get(f'{flask_api}/feedbacks')
     feedbacks=response.json()
     response2=requests.get(f'{flask_api}/orderresource')
     orders_history=response2.json()
    
     has_menu = bool(menu_items)
     has_reviews = bool(feedbacks)
     has_orders=bool(order_history)
    
     context = {
        'has_menu': has_menu,
        'has_reviews': has_reviews,
        'has_orders':has_orders,
        'menu_items': menu_items if has_menu else None,
        'feedbacks': feedbacks if has_reviews else None,
        'orders':orders_history if has_orders else None,
        'cafe_name': target_user.cafe_name,
        'user_name': target_user.name,
        'gender':target_user.gender,
        'id':id
    }
    
     return render(request, 'dashboard.html', context)

def contact_view(request):
    return render(request,"contact_us.html")
def about_view(request):
    return render(request,"about_us.html")



def login_signup_page(request):
    """View that renders the login/signup page and handles both forms"""
    if request.method == 'POST':
        # Determine if this is a login or signup request based on the form data
        if 'cafe_name' in request.POST:
            # This is a signup request
            return handle_signup(request)
        else:
            # This is a login request
            return handle_login(request)
    
    # For GET requests, just render the form
    return render(request, 'login.html')   

def handle_signup(request):
    """Process the signup form data"""
    try:
        # Extract all fields from the form
        email = request.POST.get('email')
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        gender = request.POST.get('gender')
        cafe_name = request.POST.get('cafe_name')
        location = request.POST.get('location')
        year_established = request.POST.get('year_establishment')
        
        # You mentioned an address field in your model but it's not in the form
        # Setting a default value for now
        address = request.POST.get('location', '')  # Using location as address for now
        
        # Validate data
        if not email or not name or not phone or not password:
            messages.error(request, "Please fill all required fields")
            return redirect('order_app:loginadmin')
            
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('order_app:loginadmin')
            
        # Check if user with this email already exists
        if AppUser.objects.filter(email=email).exists():
            messages.error(request, "User with this email already exists")
            return redirect('order_app:loginadmin')
            
        # Create the user
        user = AppUser.objects.create_user(
            email=email,
            name=name,
            phone=phone,
            address=address,
            gender=gender,
            cafe_name=cafe_name,
            location=location,
            year_established=int(year_established),
            password=password
        )
        
        # Log the user in
        login(request, user)
        messages.success(request, "Account created successfully!")
        return redirect('order_app:admin')  # Redirect to dashboard or home page
        
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('order_app:loginadmin')

def handle_login(request):
    """Process the login form data"""
    try:
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember', False)
        
        # Authenticate user
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            login(request, user)
            
            # Handle remember me
            if not remember_me:
                request.session.set_expiry(0)  # Session expires when browser closes
                
            messages.success(request, "Logged in successfully!")
            return redirect('order_app:admin')  # Redirect to dashboard or home page
        else:
            messages.error(request, "Invalid email or password")
            return redirect('order_app:loginadmin')
            
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('order_app:loginadmin')

         
        
@login_required
def logout_view(request):
    logout(request)
    messages.success(request,"Logout Successfull !")
    return redirect('order_app:order-home')


@login_required
def update_staff_status(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            plan = data.get('plan')
            
            # Update user's staff status
            user = request.user
            user.is_staff = True
            user.save()
            
            # Create or update subscription record
            # update_or_create returns a tuple (object, created)
            subscription, created = UserSubscription.objects.update_or_create(
                user=user,
                defaults={
                    'plan': plan,
                    'expiry_date': timezone.now() + timedelta(days=365),  # 1 year for annual billing
                    'is_active': True
                }
            )
            
            # No need to call save() again
            
            return JsonResponse({'status': 'success', 'message': 'Subscription updated successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
        
@login_required
def profile(request,id):
    currentuser=User.objects.get(id=id)
    return render(request,"profile.html",{"currentuser":currentuser})

@login_required
def reviews_view(request):
    response = requests.get(f'{flask_api}/feedbacks')
    json_data = response.json()

    all_feedbacks = json_data.get("All Feedbacks", [])  # Extract only the list
    return render(request, "reviews.html", context={"reviews": all_feedbacks})

@login_required
def delete_menu_item_view(request, id):
    # Check if the user has permission to delete (you can customize this check)
    
    
    # For API interaction, we need to get or generate a token
    # Option 1: If you have a token-based system but store tokens elsewhere
    # token = get_user_token(request.user)  # Implement this function based on your auth system
    
    # Option 2: If you don't have tokens yet, use basic authentication for API calls
    # Here's a simpler approach that doesn't require tokens:
    try:
        response = requests.delete(f"http://127.0.0.1:5000/product/{id}")
        
        # Handle the response
        if response.status_code == 200:
            messages.success(request, "Menu item deleted successfully")
        elif response.status_code == 403:
            messages.error(request, "API rejected the delete request")
        elif response.status_code == 404:
            messages.error(request, "Menu item not found")
        else:
            messages.error(request, f"Error: {response.status_code}")
    except requests.RequestException as e:
        messages.error(request, f"Connection error: {str(e)}")
    
    return redirect('order_app:order-menu')

@login_required
def update_menu_item_view(request, id):
    # First, get the menu item to check permissions and display in the form
    try:
        # For GET, fetch the existing item data
        get_response = requests.get(f"http://127.0.0.1:5000/product/{id}")
        if get_response.status_code != 200:
            messages.error(request, "Menu item not found")
            return redirect('order_app:order-menu')
        
        item = get_response.json()
        
        # Check permissions (adjust as needed for your application)
        if not request.user.is_staff and not request.user.is_superuser:
            messages.error(request, "You are not allowed to update this menu item.")
            return redirect('order_app:order-home')
        
        if request.method == 'POST':
            # Prepare data for the API request
            data = {
                "subcategory": request.POST.get('subcategory', '').strip().title(),
                "subsubcategory": request.POST.get('subsubcategory', '').strip().title(),
                "name": request.POST.get('name', '').strip(),
                "price": request.POST.get('price')
            }
            
            # Make a PUT request to the API endpoint
            # Note: Using a simpler approach without tokens for now
            put_response = requests.put(f"http://127.0.0.1:5000/product/{id}", json=data)
            
            if put_response.status_code == 200:
                messages.success(request, "Menu item updated successfully")
                return redirect('order_app:order-menu')
            else:
                messages.error(request, f"Error updating menu item: {put_response.status_code}")
                
        return render(request, 'edit_menu.html', {"item": item})
        
    except requests.RequestException as e:
        messages.error(request, f"Connection error: {str(e)}")
        return redirect('order_app:order-menu')
@login_required
def superadmin_view(request):
    users=User.objects.exclude(is_superuser="True")
    return render(request,"superadmin.html",{"users":users})

@login_required
def delete_order_view(request,id):
    response=requests.delete(f'{flask_api}/orderresource/{id}')
    messages.success(request,"order has been deleted successfully!!")
    return redirect('order_app:order_history')

     
     
 