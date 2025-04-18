from django.shortcuts import render,redirect
from django.utils import timezone
from django.http import HttpResponse
from django.contrib import messages
import datetime
import uuid
import random
import string
from .models import GiftCardType, GiftCard

from twilio.rest import Client


# Twilio credentials (from your console)
account_sid = 'AC4056bdd967749c0e84df8ee374e2db7c'
auth_token = 'd4ea0c4b2b9b5052f3f3b8a80f3456cb'
client = Client(account_sid, auth_token)

# Your Twilio WhatsApp-enabled number
twilio_whatsapp_number = 'whatsapp:+14155238886'

 

 
 

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