from django.shortcuts import render,redirect
from django.utils import timezone
from django.http import HttpResponse
from django.contrib import messages
import datetime
from django.core.paginator import Paginator
import uuid
import random
from django.db.models import Q
import string
from django.http import JsonResponse
from .models import GiftCardType, GiftCard,ShippingMethod,OrderItem,Address,Customer,Product,PaymentMethod,Order
import json
from twilio.rest import Client
from django.shortcuts import get_object_or_404

# Twilio credentials (from your console)
account_sid = 'AC4056bdd967749c0e84df8ee374e2db7c'
auth_token = 'd4ea0c4b2b9b5052f3f3b8a80f3456cb'
client = Client(account_sid, auth_token)

# Your Twilio WhatsApp-enabled number
twilio_whatsapp_number = 'whatsapp:+14155238886'

 
def send_order_whatsapp(order):
    """
    Send WhatsApp notification to customer about their order
    """
    # Make sure we have a valid phone number
    if not order.customer.phone:
        print("No phone number available to send WhatsApp notification")
        return
    
    # Format the phone number for Twilio (add 'whatsapp:' prefix)
    # Note: Make sure the phone number includes the country code
    recipient = f'whatsapp:{order.customer.phone}'
    
    # Create a list of ordered items
    items_list = []
    for item in order.orderitem_set.all():
        items_list.append(f"• {item.quantity}x {item.product_name} - ₹{item.total_price}")
    
    items_text = "\n".join(items_list)
    
    # Create message body
    message_body = f"""
Hello {order.customer.first_name},

Thank you for your order! Your order #{order.order_number} has been confirmed.

Order summary:
{items_text}

Subtotal: ₹{order.subtotal}
Shipping: ₹{order.shipping_cost}
Service Fee: ₹{order.service_fee}
Discount: ₹{order.discount_amount}
Total: ₹{order.total}

We'll update you when your order ships.
    """
    
    try:
        # Send WhatsApp message using Twilio
        message = client.messages.create(
            body=message_body,
            from_=twilio_whatsapp_number,
            to=recipient
        )
        print(f'Order confirmation sent to {recipient}. SID: {message.sid}')
        return True
    except Exception as e:
        print(f"Error sending WhatsApp notification: {str(e)}")
        return False
 
 

def gift_cards_view(request):
    """
    View to display all gift card types
    """
    # Get all active gift card types
    gift_card_types = GiftCardType.objects.filter(is_active=True)
    
    # Add category information for filtering
    for gift_type in gift_card_types:
        # This is where you'd add logic to determine categories
        # For simplicity, let's assign categories based on the name
        categories = []
        name_lower = gift_type.name.lower()
        
        if "featured" in name_lower or len(categories) == 0:
            categories.append("featured")
        if "birthday" in name_lower:
            categories.append("birthday")
        if "thank" in name_lower or "gratitude" in name_lower or "appreciation" in name_lower:
            categories.append("thank-you")
        if "congratulation" in name_lower or "graduation" in name_lower or "wedding" in name_lower:
            categories.append("congratulations")
        if "holiday" in name_lower or "christmas" in name_lower or "seasonal" in name_lower:
            categories.append("holidays")
            
        gift_type.get_categories = " ".join(categories)
    
    # Get min and max price for price range
    price_range = {
        'min': 25,
        'max': 100
    }
    
    context = {
        'gift_card_types': gift_card_types,
        'price_range': price_range,
        'today': datetime.date.today()
    }
    
    return render(request,'gift_cards.html', context)

def create_gift_card(request):
    """
    View to handle the gift card form submission
    """
    if request.method == 'POST':
        # Get form data
        gift_card_type_id = request.POST.get('gift_card_type_id')
        amount = request.POST.get('amount')
        recipient_name = request.POST.get('recipient_name')
        recipient_email = request.POST.get('recipient_email')
        recipient_phone = request.POST.get('recipient_phone', None)
        sender_name = request.POST.get('sender_name')
        message = request.POST.get('message', '')
        delivery_date_str = request.POST.get('delivery_date', None)
        
        # Get gift card type
        try:
            gift_card_type = GiftCardType.objects.get(id=gift_card_type_id)
        except GiftCardType.DoesNotExist:
            messages.error(request, "Invalid gift card type selected.")
            return redirect('shop_app:gift_cards')
        
        # Validate delivery date
        delivery_date = None
        if delivery_date_str:
            try:
                delivery_date = datetime.datetime.strptime(delivery_date_str, '%Y-%m-%d').date()
                if delivery_date < datetime.date.today():
                    messages.error(request, "Delivery date cannot be in the past.")
                    return redirect('shop_app:gift_cards')
            except ValueError:
                messages.error(request, "Invalid delivery date format.")
                return redirect('shop_app:gift_cards')
        
        # Create a unique code for the gift card
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
        
        # Create a password for redemption
        password = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        # Create the gift card
        gift_card = GiftCard.objects.create(
            gift_card_type=gift_card_type,
            recipient_name=recipient_name,
            recipient_email=recipient_email,
            recipient_phone=recipient_phone,
            sender_name=sender_name,
            message=message,
            amount=amount,
            code=code,
            password=password,
            delivery_date=delivery_date
        )
        recipients = [ 
        f'whatsapp:{recipient_phone}',  # Replace with actual recipient numbers

    # Add more numbers here
        ]
        message_body = f'Hello {recipient_name}, you have received a gift card of ₹{amount} from {sender_name}. Code: {code}. Message: {message} to use this e-gift card on our website use password {password}. Thank you!'
        
        for recipient in recipients:
            message = client.messages.create(
            body=message_body,
            from_=twilio_whatsapp_number,
            to=recipient
        )
        print(f'Message sent to {recipient}. SID: {message.sid}')

        
        # Here you would normally handle payment processing
        # For this example, we'll just show a success message
        
        messages.success(request, f"Gift card created successfully! It will be sent to {recipient_email}")
        
        # In a real application, you might send an email here
        
        return redirect('shop_app:order_success', order_id=gift_card.id)
    
    # If not POST, redirect to the gift cards page
    return redirect('gift_cards')

def order_success(request, order_id):
    """
    View to display order success page
    """
    try:
        gift_card = GiftCard.objects.get(id=order_id)
    except GiftCard.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect('shop_app:gift_cards')
    
    context = {
        'gift_card': gift_card
    }
    
    return render(request, 'order_success.html', context)

# Create your views here.

def shopapp_main_view(request):
    return render(request,"shopmain.html")

def merchandise_view(request):
    return render(request,"merchandise.html")

def deluxe_view(request):
    return render(request,"deluxe.html")

def conisseur_view(request):
    return render(request,"conisseur.html")

def about_view(request):
    return render(request,"about.html")

def starter_pack(request):
    return render(request,"starter_pack.html")

def coffee_pack(request):
    return render(request,"coffee_pack.html")

def checkout(request):
    """
    Render the checkout page
    """
    # You can define available shipping methods here
    shipping_methods = ShippingMethod.objects.all()
    
    return render(request, 'checkout.html', {
        'shipping_methods': shipping_methods
    })

 
def process_payment(request):
    """
    Process the checkout form and create an order
    """
    try:
        # Parse form data
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')
        country = request.POST.get('country')
        payment_method = request.POST.get('payment_method')
        
        # Get phone number for WhatsApp notification
        phone_number = request.POST.get('phone_number', '')
        
        # Parse cart data - Fix for potential format issues
        try:
            cart_data_raw = request.POST.get('cart_data', '[]')
            cart_items = json.loads(cart_data_raw)
            
            # Handle different possible formats
            if isinstance(cart_items, dict) and 'items' in cart_items:
                cart_items = cart_items['items']
            
            # Ensure cart_items is a list
            if not isinstance(cart_items, list):
                cart_items = []
                
        except json.JSONDecodeError:
            cart_items = []
        
        # Calculate the totals directly from cart items
        subtotal = 0
        for item in cart_items:
            try:
                # Extract price from the item
                price_str = item.get('price', '₹0')
                if isinstance(price_str, str):
                    # Remove currency symbol and commas
                    price_str = price_str.replace('₹', '').replace(',', '').strip()
                    price = float(price_str)
                else:
                    price = float(item.get('price', 0))
                
                # Get quantity (default to 1 if not specified)
                quantity = int(item.get('quantity', 1))
                
                # Add to subtotal
                subtotal += price * quantity
            except (ValueError, TypeError):
                # Skip items with invalid price
                continue
        
        # Fixed costs from the HTML
        shipping_cost = 40.00
        service_fee = 20.00
        
        # Calculate total
        total = subtotal + shipping_cost + service_fee
        
        # Check for discount code
        discount_code = request.POST.get('discount_code', '')
        discount_amount = 0
        
        # Apply discount if code is valid
        if discount_code == 'COFFEE25':
            discount_amount = round(subtotal * 0.25)
            total -= discount_amount
        
        # Find or create customer
        customer, created = Customer.objects.get_or_create(
            email=email,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'phone': phone_number
            }
        )
        
        # If customer exists but names differ, update the names
        if not created:
            if customer.first_name != first_name or customer.last_name != last_name:
                customer.first_name = first_name
                customer.last_name = last_name
                # Update phone if provided
                if phone_number:
                    customer.phone = phone_number
                customer.save()
        
        # Create or update address
        address_obj, _ = Address.objects.get_or_create(
            customer=customer,
            address_line1=address,
            city=city,
            state=state,
            zip_code=zip_code,
            country=country,
            defaults={
                'is_default_shipping': True,
                'is_default_billing': True
            }
        )
        
        # Get or create payment method
        payment_obj = None
        if payment_method == 'credit_card':
            card_number = request.POST.get('card_number', '')
            # Only store last 4 digits for security
            if card_number:
                last_four = card_number[-4:] if len(card_number) >= 4 else card_number
                
                payment_obj, _ = PaymentMethod.objects.get_or_create(
                    customer=customer,
                    payment_type=payment_method,
                    card_number_last_four=last_four,
                    defaults={
                        'expiration_date': request.POST.get('expiration_date', ''),
                        'cardholder_name': request.POST.get('name_on_card', ''),
                        'is_default': True
                    }
                )
        
        # Get default shipping method (or create one if none exists)
        shipping_method, _ = ShippingMethod.objects.get_or_create(
            name="Standard Shipping",
            defaults={
                'price': shipping_cost,
                'estimated_delivery_time': "3-5 business days"
            }
        )
        
        # Create order with calculated values
        order = Order.objects.create(
            customer=customer,
            shipping_address=address_obj,
            billing_address=address_obj,
            payment_method=payment_obj,
            shipping_method=shipping_method,
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            service_fee=service_fee,
            discount_amount=discount_amount,
            discount_code=discount_code,
            total=total,
            status='pending'
        )
        
        # Create order items
        for item in cart_items:
            try:
                # Get product price
                price_str = item.get('price', '₹0')
                if isinstance(price_str, str):
                    price_str = price_str.replace('₹', '').replace(',', '').strip()
                    price = float(price_str)
                else:
                    price = float(item.get('price', 0))
                
                # Get quantity
                quantity = int(item.get('quantity', 1))
                
                # Try to find product in database
                product_title = item.get('title', '')
                try:
                    product = Product.objects.get(name=product_title)
                except Product.DoesNotExist:
                    # Create a placeholder product if it doesn't exist
                    product = Product.objects.create(
                        name=product_title,
                        price=price,
                        stock_quantity=100,  # Default stock
                        image_url=item.get('image', '')
                    )
                
                # Create order item
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product_title,
                    product_price=price,
                    quantity=quantity,
                    total_price=price * quantity
                )
            except Exception as item_error:
                print(f"Error processing item: {str(item_error)}")
                # Continue processing other items
                continue
        
        # Send WhatsApp notification to customer
        if customer.phone:
            try:
                send_order_whatsapp(order)
            except Exception as whatsapp_error:
                print(f"Error sending WhatsApp notification: {str(whatsapp_error)}")
                # Continue processing even if WhatsApp notification fails
            
        # Return success response with order number and clear storage flag
        response_data = {
            'success': True,
            'order_number': order.order_number,
            'clear_storage': True,  # Flag to indicate localStorage should be cleared
            'redirect_url': f'/shop/order-confirmation/{order.order_number}/'  # Fixed URL with leading slash
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        # Log the error
        import traceback
        print(f"Error processing payment: {str(e)}")
        print(traceback.format_exc())
        
        # Return error response
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while processing your payment.'
        })
    

def order_confirmation(request, order_number):
    """
    Display order confirmation page with complete order details and clear local storage
    """
    # Get the order with all related data using select_related
    print(order_number)
    order = get_object_or_404(
        Order.objects.select_related(
            'customer', 
            'shipping_address', 
            'payment_method'
        ), 
        order_number=order_number
    )
    
    # Explicitly get order items
    order_items = OrderItem.objects.filter(order=order)
    
    # Check if we have items
    if not order_items.exists():
        messages.warning(request, "Your order doesn't contain any items. This might be an error.")
    
    # Calculate subtotal from order items
    subtotal = sum(item.product_price for item in order_items)
    
    # Calculate total with shipping, discount, etc.
    shipping_fee = 40  # As shown in your template
    total = subtotal + shipping_fee
    
    # Add service fee if present
    if hasattr(order, 'service_fee') and order.service_fee is not None and order.service_fee > 0:
        total += order.service_fee
    
    # Subtract discount if present
    if hasattr(order, 'discount_amount') and order.discount_amount is not None and order.discount_amount > 0:
        total -= order.discount_amount
    
    context = {
        'order': order,
        'order_items': order_items,  # Pass items explicitly
        'subtotal': subtotal,
        'total': total
    }
    
    # For debugging
    print(f"Order #{order_number} has {order_items.count()} items")
    print(f"Subtotal: {subtotal}, Total: {total}")
    
    return render(request, 'order_confirmation.html', context)


def gift_card_history(request):
    """
    View to display all gift cards with filtering options
    """
    # Get filter parameters from request
    status = request.GET.get('status', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    search_query = request.GET.get('search', '')
    
    # Start with all gift cards
    gift_cards = GiftCard.objects.all().order_by('-created_at')
    
    # Apply status filter if specified
    if status == 'redeemed':
        gift_cards = gift_cards.filter(is_redeemed=True)
    elif status == 'active':
        gift_cards = gift_cards.filter(is_redeemed=False)
    
    # Apply date filters if specified
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            gift_cards = gift_cards.filter(created_at__date__gte=start_date_obj)
        except ValueError:
            messages.error(request, "Invalid start date format")
    
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            gift_cards = gift_cards.filter(created_at__date__lte=end_date_obj)
        except ValueError:
            messages.error(request, "Invalid end date format")
    
    # Apply search query if specified
    if search_query:
        gift_cards = gift_cards.filter(
            Q(recipient_name__icontains=search_query) |
            Q(recipient_email__icontains=search_query) |
            Q(sender_name__icontains=search_query) |
            Q(code__icontains=search_query)
        )
    
    # If user is not superuser, only show gift cards they have access to
    # Assuming you want to implement some kind of access control
    if not request.user.is_superuser:
        # This is a placeholder - implement according to your access control rules
        # For example, if gift cards are associated with specific users:
        # gift_cards = gift_cards.filter(created_by=request.user)
        pass
    
    context = {
        'gift_cards': gift_cards,
        'status_filter': status,
        'start_date': start_date,
        'end_date': end_date,
        'search_query': search_query,
    }
    
    return render(request, 'gift_card_history.html', context)

def gift_card_history(request):
    """
    View to display all gift cards with filtering options
    """
    # Get filter parameters from request
    status = request.GET.get('status', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    search_query = request.GET.get('search', '')
    
    # Start with all gift cards
    gift_cards = GiftCard.objects.all().order_by('-created_at')
    
    # Apply status filter if specified
    if status == 'redeemed':
        gift_cards = gift_cards.filter(is_redeemed=True)
    elif status == 'active':
        gift_cards = gift_cards.filter(is_redeemed=False)
    
    # Apply date filters if specified
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            gift_cards = gift_cards.filter(created_at__date__gte=start_date_obj)
        except ValueError:
            messages.error(request, "Invalid start date format")
    
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            gift_cards = gift_cards.filter(created_at__date__lte=end_date_obj)
        except ValueError:
            messages.error(request, "Invalid end date format")
    
    # Apply search query if specified
    if search_query:
        gift_cards = gift_cards.filter(
            Q(recipient_name__icontains=search_query) |
            Q(recipient_email__icontains=search_query) |
            Q(sender_name__icontains=search_query) |
            Q(code__icontains=search_query)
        )
    
 
    
    context = {
        'gift_cards': gift_cards,
        'status_filter': status,
        'start_date': start_date,
        'end_date': end_date,
        'search_query': search_query,
    }
    
    return render(request, 'gift_card_history.html', context)

 
 







def gift_card_detail(request, id):
    """
    View to display detailed information about a specific gift card
    """
    gift_card = get_object_or_404(GiftCard, id=id)
    
    
    
    
    context = {
        'gift_card': gift_card
    }
    
    return render(request, 'gift_card_detail.html', context)


def delete_gift_card(request, id):
    """
    View to delete a gift card
    """
    gift_card = get_object_or_404(GiftCard, id=id)
    gift_card.delete()
    messages.success(request,"Gift card deleted successfully!!")
   
    
     
    
    return redirect('shop_app:gift_card_history')

 
def edit_gift_card(request, id):
    gift_card = get_object_or_404(GiftCard, id=id)
    gift_card_types = GiftCardType.objects.all()
    
    if request.method == "POST":
        # Extract data from the form
        gift_card.gift_card_type_id = request.POST.get('gift_card_type')
        gift_card.recipient_name = request.POST.get('recipient_name')
        gift_card.recipient_email = request.POST.get('recipient_email')
        gift_card.recipient_phone = request.POST.get('recipient_phone')
        gift_card.sender_name = request.POST.get('sender_name')
        gift_card.message = request.POST.get('message')
        gift_card.amount = request.POST.get('amount')
        gift_card.delivery_date = request.POST.get('delivery_date') or None
        gift_card.is_redeemed = 'is_redeemed' in request.POST
        
        try:
            gift_card.save()
            messages.success(request, f"Gift Card #{gift_card.id} updated successfully!")
            return redirect('shop_app:gift_card_history')
        except Exception as e:
            messages.error(request, f"Error updating gift card: {str(e)}")
    
    context = {
        'gift_card': gift_card,
        'gift_card_types': gift_card_types,
    }
    return render(request, 'edit_gift_card.html', context)



from django.shortcuts import render
from django.db.models import Q, Count, Sum
from django.core.paginator import Paginator
from .models import Order, Customer, OrderItem

def order_history(request):
    """
    Display all orders with optional filtering
    All users can see all orders regardless of permissions
    """
    # Get query parameters for filtering
    status_filter = request.GET.get('status', None)
    search_query = request.GET.get('search', None)
    sort_by = request.GET.get('sort', '-created_at')  # Default: newest first
    customer_filter = request.GET.get('customer', None)
    
    # Handle date parameters safely
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)
    
    # Start with all orders and include related data to prevent N+1 queries
    # Use select_related for ForeignKey relationships (one-to-many)
    # Use prefetch_related for reverse relationships (many-to-one or many-to-many)
    orders = Order.objects.select_related(
        'customer', 
        'shipping_address', 
        'billing_address',
        'payment_method',
        'shipping_method'
    ).prefetch_related('items')
    
    # Apply customer filter if provided
    if customer_filter and customer_filter != 'None':
        orders = orders.filter(customer__id=customer_filter)
    
    # Apply status filter if provided
    if status_filter and status_filter not in ['all', 'None']:
        orders = orders.filter(status=status_filter)
    
    # Handle date filters safely
    if start_date and start_date != 'None':
        try:
            orders = orders.filter(created_at__gte=start_date)
        except ValueError:
            # Invalid date format - just ignore this filter
            pass
    
    if end_date and end_date != 'None':
        try:
            orders = orders.filter(created_at__lte=end_date)
        except ValueError:
            # Invalid date format - just ignore this filter
            pass
    
    # Apply search filter
    if search_query and search_query != 'None':
        orders = orders.filter(
            Q(order_number__icontains=search_query) |
            Q(items__product_name__icontains=search_query) |
            Q(customer__first_name__icontains=search_query) |
            Q(customer__last_name__icontains=search_query) |
            Q(customer__email__icontains=search_query)
        ).distinct()
    
    # Apply sorting
    orders = orders.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(orders, 10)  # 10 orders per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Get all customers for the filter dropdown
    customers = Customer.objects.all().order_by('last_name', 'first_name')
    
    context = {
        'orders': page_obj,
        'status_choices': Order.ORDER_STATUS,
        'current_status': status_filter,
        'search_query': search_query,
        'start_date': start_date,
        'end_date': end_date,
        'sort_by': sort_by,
        'customers': customers,
        'selected_customer': customer_filter,
    }
    
    return render(request, 'order_history_merch.html', context)

def order_detail(request, order_number):
    """
    Display detailed information about a specific order
    All users can access any order regardless of ownership
    """
    # Get the order directly without customer verification
    order = get_object_or_404(Order, order_number=order_number)
    
    # Get order items and other related information
    order_items = order.items.all()
    
    context = {
        'order': order,
        'order_items': order_items,
    }
    
    return render(request, 'order_detail_merch.html', context)


def cancel_order(request):
    """
    View function to delete an order completely from the database.
    Only allows deletion if order status is 'pending' or 'processing'.
    """
    order_number = request.POST.get('order_number')
    
    if not order_number:
        return JsonResponse({'success': False, 'message': 'Order number is required'}, status=400)
    
    # Get the order object or return 404
    order = get_object_or_404(Order, order_number=order_number)
    
    # Check if the order belongs to the logged-in user
    if order.customer.id != request.user.id and not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'You are not authorized to delete this order'}, status=403)
    
    # Check if the order can be deleted (only pending or processing)
    if order.status not in ['pending', 'processing']:
        return JsonResponse({'success': False, 'message': 'This order cannot be deleted'}, status=400)
    
    # Delete the order completely
    order.delete()
    
    # Return success response
    return JsonResponse({'success': True, 'message': 'Order deleted successfully'})


def custom_hampers_view(request):
    return render(request,"custom_hamper.html")



 
