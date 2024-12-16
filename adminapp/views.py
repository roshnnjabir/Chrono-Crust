from django.shortcuts import render, redirect
from user.models import CustomUser
from .models import Product, Brand, Collection, Order, OrderItem, Coupen, PersonalWallet, TransactionHistory
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
import datetime
from django.core.mail import send_mail
from django.db import transaction
from PIL import Image as PILImage
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from io import BytesIO
from django.contrib.auth import logout, login, authenticate
from django.db.models import Q, Count, Sum, F, FloatField
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.cache import never_cache
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import json
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, DecimalField
import matplotlib
matplotlib.use('Agg')  # Set the backend before importing pyplot
import matplotlib.pyplot as plt
import io
import base64
from django.db.models.functions import Cast
from django.db.models.functions import Coalesce


# Create your views here.
@staff_member_required(login_url='admin_login')
def admin(request):
    return render(request, 'admin_home.html')


@never_cache
@staff_member_required(login_url="admin_login")
def admin_list_user(request):
    query = request.GET.get('query', '')  # Get the search query from GET request
    if query:
        users = CustomUser.objects.filter(
            (Q(first_name__icontains=query) | Q(email__icontains=query) | Q(last_name__icontains=query)) & (Q(is_staff=False))
        )  # Filter by first name or email
    else:
        users = CustomUser.objects.filter(is_staff=False)

    # Handle AJAX request
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        results = list(users.values('id', 'first_name', 'last_name', 'email', 'is_active'))
        return JsonResponse(results, safe=False)

    # Handle standard request (render the full page)
    return render(request, 'admin_list_user.html', {'users': users})


@staff_member_required(login_url="admin_login")
def admin_show_user_details(request, id):
    user = get_object_or_404(CustomUser, id=id)
    addresses = user.addresses.all()
    context = {
        'user': user,
        'addresses': addresses,
        'show_order': False
    }
    return render(request, 'admin_show_user_details.html', context)


@staff_member_required(login_url="admin_login")
def admin_show_order_of_specific_user(request, id):
    user = get_object_or_404(CustomUser, id=id)
    orders = user.orders.all()
    addresses = user.addresses.all()
    context = {
        'user': user,
        'orders': orders,
        'addresses': addresses,
        'show_orders': True
    }
    return render(request, 'admin_show_user_details.html', context)


@staff_member_required(login_url="admin_login")
def admin_list_blocked_user(request):
    query = request.GET.get('query', '')  # Get the search query from GET request
    if query:
        users = CustomUser.objects.filter(
            (Q(first_name__icontains=query) | Q(email__icontains=query) | Q(last_name__icontains=query)) & (Q(is_staff=False) & Q(is_active=False))
        )  # Filter by first name or email
    else:
        users = CustomUser.objects.filter(Q(is_staff=False), Q(is_active=False))  # If no query, return all users

    # Handle AJAX request
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        results = list(users.values('id', 'first_name', 'last_name', 'email', 'is_active'))  # Prepare JSON response
        return JsonResponse(results, safe=False)  # Send JSON response for AJAX

    # Handle standard request (render the full page)
    return render(request, 'admin_list_blocked_user.html', {'users': users})


def admin_logout(request):
    logout(request)
    return redirect('admin')


def admin_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(email=email, password=password)
        if user is not None:
            if user.is_staff:
                login(request, user)
                return redirect('admin')
            else:
                messages.error(request, 'not staff member')
        else:
            messages.error(request, 'Password or Email Wrong')
    return render(request, 'admin_login.html')


@staff_member_required(login_url="admin_login")
def admin_block_unblock_user(request, id):
    user_data = CustomUser.objects.get(id=id)
    if user_data.is_active:
        user_data.is_active = False
    else:
        user_data.is_active = True

    user_data.save()
    return redirect('admin_list_user')


@staff_member_required(login_url="admin_login")
def admin_list_product(request):
    query = request.GET.get('query', '')
    brand_id = request.GET.get('brand_id', 'all')  # Get selected brand ID

    # Filter products based on search query
    if query:
        products = Product.objects.filter(
            (
                Q(name__icontains=query) |
                Q(collection__name__icontains=query) |
                Q(collection__brand__name__icontains=query)
            ) & Q(is_listed=True)
        )
    else:
        products = Product.objects.all()

    # Filter by brand if a specific brand is selected
    if brand_id and brand_id != 'all':
        products = products.filter(collection__brand__id=brand_id)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        results = [
            {
                'id': product.id,
                'image': request.build_absolute_uri(product.image.url),  # Full URL for the image
                'name': product.name,
                'is_listed': product.is_listed,
                'collection__name': product.collection.name,
                'collection__is_listed': product.collection.is_listed,
                'collection__brand__name': product.collection.brand.name,
                'collection_brand_is_listed': product.collection.brand.is_listed,
                'stock': product.stock,
                'price': product.price,
            }
            for product in products
        ]
        return JsonResponse(results, safe=False)

    return render(request, 'admin_list_products.html', {
        'products': products,
        'brands': Brand.objects.all(),  # Pass all brands to the template
    })


@staff_member_required(login_url="admin_login")
def admin_add_product(request):
    if request.method == "POST":
        productname = request.POST['productname']
        price = request.POST['price']
        collect = request.POST['collection']
        stock = request.POST['stock']
        reference_no = request.POST['reference_no']
        image1 = request.POST['image1']
        image2 = request.POST['image2']
        image3 = request.POST['image3']
        image4 = request.POST['image4']
        description1 = request.POST['description']
        description2 = request.POST['description1']
        description3 = request.POST['description2']

        collection = Collection.objects.get(id=collect)
        Product.objects.create(name=productname, price=price, collection=collection, stock=stock, reference_no=reference_no, image=image1, image1=image2, image2=image3, image3=image4, description=description1, description1=description2, description2=description3)
        return redirect('admin_list_product')
    collection = Collection.objects.all()
    return render(request, 'admin_add_product.html', {'collections': collection})


@staff_member_required(login_url="admin_login")
def admin_list_unlist_product(request, id):
    product = Product.objects.get(id=id)
    if product.is_listed:
        product.is_listed = False
    else:
        product.is_listed = True
    product.save()
    return redirect('admin_list_product')


@staff_member_required(login_url="admin_login")
def admin_edit_product(request, id):
    if request.method == "POST":
        limited_edition = request.POST.get('limited_edition') == 'True'
        for_men = request.POST.get('for_men') == 'True'
        for_women = request.POST.get('for_women') == 'True'
        productid = request.POST['product-id']
        productname = request.POST['productname']
        price = request.POST['price']
        offerprice = request.POST['offerprice']
        collection_id = request.POST['collection']
        stock = request.POST['stock']
        diameter = request.POST['diameter']
        frequency = request.POST['frequency']
        power_reserve = request.POST['power_reserve']
        water_resistance = request.POST['water_resistance']
        description1 = request.POST['description']
        description2 = request.POST['description1']
        description3 = request.POST['description2']
        image1 = request.POST['image1']
        image2 = request.POST['image2']
        image3 = request.POST['image3']

        product = Product.objects.get(id=productid)
        collection = Collection.objects.get(id=collection_id)

        product.name = productname
        product.collection = collection
        product.price = price
        product.offer_price = offerprice
        product.stock = stock
        product.diameter = diameter
        product.frequency = frequency
        product.power_reserve = power_reserve
        product.water_resistance = water_resistance
        product.limited_edition = limited_edition
        product.for_men = for_men
        product.for_women = for_women
        product.image = image1
        product.image1 = image2
        product.image2 = image3
        product.description = description1
        product.description1 = description2
        product.description2 = description3
        product.save()

        return redirect('admin_list_product')

    product = Product.objects.get(id=id)
    collections = Collection.objects.all()
    return render(request, 'admin_edit_products.html', {'product': product, 'collections': collections})


@staff_member_required(login_url="admin_login")
def admin_delete_product(request, id):
    product = Product.objects.get(id=id)
    product.delete()
    return redirect('admin_list_product')


@staff_member_required(login_url="admin_login")
def admin_list_collection(request):
    collections = Collection.objects.all()
    return render(request, 'admin_list_collection.html', {'collections': collections})


@staff_member_required(login_url="admin_login")
def admin_add_collection(request):
    if request.method == "POST":
        collection_name = request.POST['collection']
        brand_id = request.POST['brand']
        logo_image = request.POST.get('image1')
        banner_image = request.POST.get('image2')
        if Collection.objects.filter(name=collection_name).exists():
            messages.error(request, f"The collection '{collection_name}' already exists.")
            return redirect('admin_add_collection')
        brand = Brand.objects.get(id=brand_id)
        Collection.objects.create(name=collection_name, brand=brand, logo_image=logo_image, banner_image=banner_image)
        return redirect('admin_list_collection')
    brands = Brand.objects.all()
    return render(request, 'admin_add_collection.html', {'brands': brands})


@staff_member_required(login_url="admin_login")
def admin_list_unlist_collection(request, id):
    collection = Collection.objects.get(id=id)
    if collection.is_listed:
        collection.is_listed = False
    else:
        collection.is_listed = True
    collection.save()
    return redirect('admin_list_collection')


@staff_member_required(login_url="admin_login")
def admin_edit_collection(request, id):
    collection = Collection.objects.get(id=id)
    if request.method == "POST":
        brand_id = request.POST['brand']
        collect_name = request.POST['collection']
        logo_image = request.POST.get('image1')
        banner_image = request.POST.get('image2')
        if Collection.objects.filter(name=collect_name, brand_id=brand_id).exclude(id=id).exists():
            messages.error(request, "Collection name already exists.")
        else:
            collection.name = collect_name
            brand = Brand.objects.get(id=brand_id)
            collection.brand = brand
            collection.logo_image = logo_image
            collection.banner_image = banner_image
            collection.save()
            return redirect('admin_list_collection')
    brands = Brand.objects.all()
    return render(request, 'admin_edit_collection.html', {'collection': collection, 'brands': brands})


@staff_member_required(login_url="admin_login")
def admin_delete_collection(request, id):
    collection = Collection.objects.get(id=id)
    collection.delete()
    return redirect('admin_list_collection')


@staff_member_required(login_url="admin_login")
def admin_list_brand(request):
    brand = Brand.objects.all()
    return render(request, 'admin_list_brand.html', {'brands': brand})


@staff_member_required(login_url="admin_login")
def admin_add_brand(request):
    if request.method == "POST":
        brand_name = request.POST['brandname']
        logo_image = request.POST.get('image1')
        banner_image = request.POST.get('image2')
        if Brand.objects.filter(name=brand_name).exists():
            messages.error(request, f"The Brand '{brand_name}' already exists.")
            return redirect('admin_add_brand')
        Brand.objects.create(name=brand_name, logo_image=logo_image, banner_image=banner_image)
        return redirect('admin_list_brand')
    brands = Brand.objects.all()
    return render(request, 'admin_add_brand.html', {'brands': brands})


@staff_member_required(login_url="admin_login")
def admin_list_unlist_brand(request, id):
    brand = Brand.objects.get(id=id)
    if brand.is_listed:
        brand.is_listed = False
    else:
        brand.is_listed = True
    brand.save()
    return redirect('admin_list_brand')


@staff_member_required(login_url="admin_login")
def admin_edit_brand(request, id):
    brand = Brand.objects.get(id=id)
    if request.method == "POST":
        brand_name = request.POST.get('brandname')
        logo_image = request.POST.get('image1')
        banner_image = request.POST.get('image2')
        if Brand.objects.filter(name=brand_name).exclude(id=id).exists():
            messages.error(request, "Brand name already exists.")
        else:
            brand.name = brand_name
            brand.logo_image = logo_image
            brand.banner_image = banner_image
            brand.save()
            return redirect('admin_list_brand')
    return render(request, 'admin_edit_brand.html', {'brand': brand})


@staff_member_required(login_url="admin_login")
def admin_delete_brand(request, id):
    brand = Brand.objects.get(id=id)
    brand.delete()
    return redirect('admin_list_brand')


@never_cache
@staff_member_required(login_url="admin_login")
def admin_list_orders(request):
    orders = Order.objects.all().order_by('-updated_at')
    # Filter by order status
    status_filter = request.GET.get('status', 'all')
    payment_status = request.GET.get('payment_status', 'all')
    last_7_days = request.GET.get('last_7_days') == 'true'

    if status_filter and status_filter != 'all':
        orders = orders.filter(status=status_filter)

    if payment_status and payment_status != 'all':
        orders = orders.filter(payment_status=payment_status)

    if last_7_days:
        seven_days_ago = timezone.now() - timedelta(days=7)
        orders = orders.filter(updated_at__gte=seven_days_ago)

    # Filter by user
    user_filter = request.GET.get('user')
    if user_filter:
        orders = orders.filter(user__id=user_filter)

    # Filter by date
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        orders = orders.filter(updated_at__date__range=[start_date, end_date])

    # Filter by price
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price and max_price:
        orders = orders.filter(total_amount__range=[min_price, max_price])

    users = CustomUser.objects.all()
    total_orders = orders.count()
    return render(request, 'admin_list_orders.html', {
        'orders': orders,
        'total_orders': total_orders,
        'status_filter': status_filter,
        'users': users,
        'start_date': start_date,
        'end_date': end_date,
        'min_price': min_price,
        'max_price': max_price,
    })


@staff_member_required(login_url="admin_login")
def admin_order_details(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    status_choices = Order.STATUS_CHOICES
    payment_status_choices = Order.PAYMENT_STATUS_CHOICES
    return render(request, 'admin_order_details.html', {
        'order': order,
        'status_choices': status_choices,
        'payment_status_choices': payment_status_choices,
    })


def update_order_status(request, order_id):
    if request.method == 'POST':
        try:
            # Parse the JSON data
            data = json.loads(request.body)
            new_status = data.get('status')

            # Validate the new status against the model's status choices
            if new_status in dict(Order.STATUS_CHOICES):
                order = Order.objects.get(id=order_id)

                # If the status is 'returned', apply return order logic
                if new_status == 'returned':
                    try:
                        return_order(order)
                    except Exception as e:
                        print(f"Error in return_order: {e}")
                        raise

                order.status = new_status
                order.save()
                return JsonResponse({'message': 'Order status updated successfully'})
            else:
                return JsonResponse({'error': 'Invalid status'}, status=400)
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


def update_payment_status(request, order_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_payment_status = data.get('payment_status')

            if new_payment_status in dict(Order.PAYMENT_STATUS_CHOICES):
                order = Order.objects.get(id=order_id)
                order.payment_status = new_payment_status
                order.save()
                return JsonResponse({'message': 'Payment status updated successfully'})
            else:
                return JsonResponse({'error': 'Invalid payment status'}, status=400)
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


@staff_member_required(login_url='/')
def admin_list_return_orders(request):
    orders = Order.objects.filter(Q(status='return_requested') | Q(status='returned'))
    print(orders)
    return render(request, 'admin_list_return_orders.html', {'orders':orders})


def return_order(order):
    print(order.status)
    print(order.payment_status)
    try:
        payment = PersonalWallet.objects.get(user=order.user)
    except PersonalWallet.DoesNotExist:
        raise ValueError('Personal wallet not found.')

    if order.status in ['return_requested', 'Return Requested']:
        if order.payment_status == 'cod':
            # For COD orders: update stock, refund via wallet.
            with transaction.atomic():
                for order_item in order.items.all():
                    product = order_item.product
                    product.stock += order_item.quantity
                    product.save()
                order.payment_status = 'refunded'
                order.status = 'returned'
                order.save()

                # Send email to user
                send_mail(
                    subject=f"Your order {order.id} has been initiated for return",
                    message=f"Dear {order.user.first_name},\n\n"
                            f"Your order {order.id} has been initiated for return successfully. You will be contacted by our delivery partner soon.\n\n"
                            "Thank you for shopping with Chrono Crust!",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[order.user.email],
                )
        elif order.payment_status == 'paid':
            # For Paid orders: refund to wallet, update stock.
            with transaction.atomic():
                for order_item in order.items.all():
                    product = order_item.product
                    product.stock += order_item.quantity
                    product.save()
                order.status = 'returned'
                order.payment_status = 'refunded'
                payment.balance += order.total_amount
                payment.save()

                # Log the transaction for the refund
                transaction_history = TransactionHistory(
                    user=order.user,
                    wallet=payment,
                    balance=payment.balance,
                    amount=order.total_amount,
                    transaction_type='REFUND',
                    payment_method='RAZORPAY',  # Assuming Razorpay or adjust as necessary
                    status='SUCCESS',
                    description=f"Refund for Returned order {order.id}",
                )
                transaction_history.save()

                order.save()

                # Send email to user
                send_mail(
                    subject=f"Order {order.id} Cancelled and Refunded",
                    message=f"Dear {order.user.first_name},\n\n"
                            f"Your order {order.id} has been successfully cancelled and refunded.\n\n"
                            "The amount has been refunded to your in-site personal wallet.\n\n"
                            "Thank you for shopping with Chrono Crust!",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[order.user.email],
                )

        elif order.payment_status == 'pwallet':
            # For wallet payments: similar refund process to paid
            with transaction.atomic():
                for order_item in order.items.all():
                    product = order_item.product
                    product.stock += order_item.quantity
                    product.save()
                order.status = 'returned'
                order.payment_status = 'refunded'

                payment.balance += order.total_amount
                payment.save()

                order.save()

                # Log the transaction for the refund
                transaction_history = TransactionHistory(
                    user=order.user,
                    wallet=payment,
                    balance=payment.balance,
                    amount=order.total_amount,
                    transaction_type='REFUND',
                    payment_method='PWALLET',  # Wallet refund method
                    status='SUCCESS',
                    description=f"Refund for Returned order {order.id}",
                )
                transaction_history.save()

                # Send email to user
                send_mail(
                    subject=f"Order {order.id} Cancelled and Refunded to Wallet",
                    message=f"Dear {order.user.first_name},\n\n"
                            f"Your order {order.id} has been successfully cancelled and refunded to your wallet.\n\n"
                            "The refund has been credited to your personal wallet.\n\n"
                            "Thank you for shopping with us!",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[order.user.email],
                )
        else:
            raise ValueError('Invalid payment status for cancellation.')
    else:
        raise ValueError('This order cannot be returned.')


@staff_member_required(login_url="admin_login")
@never_cache
def admin_coupons(request):
    coupons = Coupen.objects.all()
    return render(request, 'admin_list_coupon.html', {'coupons': coupons})


def admin_add_coupon(request):
    if request.method == "POST":
        # Get form data from the POST request
        code = request.POST.get('code')
        min_required = request.POST.get('min_required')
        maximum_discount = request.POST.get('maximum_discount')
        discount_percentage = request.POST.get('discount_percentage')
        usage_limit = request.POST.get('usage_limit')
        valid_from = request.POST.get('valid_from')
        valid_to = request.POST.get('valid_to')
        active = request.POST.get('active') == 'on'  # Checkbox returns 'on' when checked

        if Coupen.objects.filter(code=code).exists():
            messages.error(request, ' This Coupen Code Already Exist')
            return redirect('admin_add_coupon')

        # Convert date strings to datetime objects
        valid_from = timezone.datetime.fromisoformat(valid_from)
        valid_to = timezone.datetime.fromisoformat(valid_to)

        # Create the coupon object
        Coupen.objects.create(
            code=code,
            min_required=min_required,
            maximum_discount=maximum_discount,
            discount_percentage=discount_percentage,
            # usage_limit=usage_limit,
            valid_from=valid_from,
            valid_to=valid_to,
            active=active
        )

        # Redirect to the list of coupons after creation
        return redirect('admin_list_coupons')

    return render(request, 'admin_add_coupon.html')


def admin_edit_coupon(request, coupon_id):
    # Fetch the coupon to edit
    coupon = get_object_or_404(Coupen, id=coupon_id)

    if request.method == "POST":
        # Get form data from the POST request
        code = request.POST.get('code')
        min_required = request.POST.get('min_required')
        maximum_discount = request.POST.get('maximum_discount')
        discount_percentage = request.POST.get('discount_percentage')
        # usage_limit = request.POST.get('usage_limit')
        valid_from = request.POST.get('valid_from')
        valid_to = request.POST.get('valid_to')
        active = request.POST.get('active') == 'on'  # Checkbox returns 'on' when checked

        # Check if the coupon code has changed and if the new code already exists
        if code != coupon.code and Coupen.objects.filter(code=code).exists():
            messages.error(request, 'This Coupon Code Already Exists')
            return redirect('admin_edit_coupon', coupon_id=coupon.id)

        # Convert date strings to datetime objects
        valid_from = timezone.datetime.fromisoformat(valid_from)
        valid_to = timezone.datetime.fromisoformat(valid_to)

        # Update the coupon object
        coupon.code = code
        coupon.min_required = min_required
        coupon.maximum_discount = maximum_discount
        coupon.discount_percentage = discount_percentage
        # coupon.usage_limit = usage_limit
        coupon.valid_from = valid_from
        coupon.valid_to = valid_to
        coupon.active = active
        coupon.save()

        # Redirect to the list of coupons after editing
        messages.success(request, 'Coupon updated successfully')
        return redirect('admin_list_coupons')

    return render(request, 'admin_edit_coupon.html', {'coupon': coupon})


def admin_delete_coupon(request, code):
    coupen = Coupen.objects.get(code=code)
    coupen.delete()
    return redirect('admin_list_coupons')


def generate_sales_pdf(request, context):
    """
    Generate a comprehensive PDF sales report with date filtering and graphs
    
    Args:
        request: Django request object
        context: Dictionary containing sales report data
    
    Returns:
        HttpResponse with PDF content
    """
    time_frame = request.GET.get('time_frame', 'Custom')
    
    # If a specific time frame was used, show that
    if time_frame in ['1', '7', '30']:
        start_date = timezone.now() - timedelta(days=int(time_frame))
        end_date = timezone.now()
    else:
        # Use the dates from GET parameters if available
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

    # Create a file-like buffer to receive PDF data
    buffer = BytesIO()
    
    # Create the PDF document (landscape for better graph visibility)
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Get sample stylesheet
    styles = getSampleStyleSheet()
    
    # Title
    title = Paragraph("Detailed Sales Report", styles['Title'])
    elements.append(title)
    
    # Create filter data using actual dates
    # Create filter data using actual dates
    filter_data = [
        ['Filter Type', 'Value'],
        ['Time Frame', f"{time_frame} days" if time_frame in ['1', '7', '30'] else time_frame],
        ['Start Date', start_date.strftime('%Y-%m-%d') if hasattr(start_date, 'strftime') else str(start_date or 'N/A')],
        ['End Date', end_date.strftime('%Y-%m-%d') if hasattr(end_date, 'strftime') else str(end_date or 'N/A')],
        ['Minimum Price', request.GET.get('min_price', 'N/A')],
        ['Maximum Price', request.GET.get('max_price', 'N/A')]
    ]
    filter_table = Table(filter_data, colWidths=[200, 300])
    filter_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    elements.append(filter_table)
    elements.append(Spacer(1, 12))
    
    # Sales Summary Section
    summary_data = [
        ['Metric', 'Value'],
        ['Total Sales', str(context['total_sales'])],
        ['Average Price', f"${context['average_price']:.2f}"],
        ['Total Revenue', f"${context['total_revenue']:.2f}"],
        ['Total Discount', f"${context['total_sale_discount']:.2f}"]
    ]
    summary_table = Table(summary_data, colWidths=[200, 300])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 12))
    
    def add_graph_to_pdf(graph_base64, title, is_pie_chart=False):
        if graph_base64:
            
            graph_data = base64.b64decode(graph_base64)
            graph_image = PILImage.open(io.BytesIO(graph_data))
            
            graph_path = f"{title.lower().replace(' ', '_')}_graph.png"
            graph_image.save(graph_path, quality=95, optimize=True)
            
            if is_pie_chart:
                width = height = 4*inch
            else:
                width = 6*inch
                height = 3*inch
            
            graph_img = Image(graph_path, width=width, height=height)
            graph_title = Paragraph(title, styles['Heading3'])
            elements.append(graph_title)
            elements.append(graph_img)
            elements.append(Spacer(1, 12))

    add_graph_to_pdf(context.get('product_line_graph'), "Product Sales Trend")
    add_graph_to_pdf(context.get('product_pie_graph'), "Product Sales Percentage", is_pie_chart=True)
    
    add_graph_to_pdf(context.get('collection_line_graph'), "Collection Sales Trend")
    add_graph_to_pdf(context.get('collection_pie_graph'), "Collection Sales Percentage", is_pie_chart=True)
        
    # Product Popularity Section
    product_header = Paragraph("Top 5 Product Sales", styles['Heading2'])
    elements.append(product_header)
    
    product_data = [['Product', 'Total Sales', 'Percentage']]
    for product in context['product_popularity']:
        product_data.append([
            product.name, 
            str(product.total_sales), 
            f"{product.sales_percentage:.2f}%"
        ])
    
    product_table = Table(product_data, colWidths=[200, 150, 150])
    product_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    elements.append(product_table)
    elements.append(Spacer(1, 12))
    
    # Collection Popularity Section
    collection_header = Paragraph("Top 5 Collection Sales", styles['Heading2'])
    elements.append(collection_header)
    
    collection_data = [['Collection', 'Total Sales', 'Percentage']]
    for collection in context['collection_popularity']:
        collection_data.append([
            collection.name, 
            str(collection.total_sales), 
            f"{collection.sales_percentage:.2f}%"
        ])
    
    collection_table = Table(collection_data, colWidths=[200, 150, 150])
    collection_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    elements.append(collection_table)
    
    # Build PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer and write it to the response
    pdf = buffer.getvalue()
    buffer.close()
    
    response = HttpResponse(content_type='application/pdf')
    
    # Customize filename based on filtering
    if time_frame in ['1', '7', '30']:
        filename = f"sales_report_{time_frame}_days.pdf"
    elif start_date and end_date:
        filename = f"sales_report_{start_date}_to_{end_date}.pdf"
    else:
        filename = "sales_report.pdf"
    
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.write(pdf)
    
    return response


def admin_sales(request):
    plt.close('all')
    
    orders = Order.objects.filter(payment_status='paid')
    
    time_frame = request.GET.get('time_frame')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if time_frame in ['1', '7', '30', '90']:
        start_date = timezone.now() - timedelta(days=int(time_frame))
        orders = orders.filter(updated_at__date__gte=start_date.date())

    if start_date and end_date:
        orders = orders.filter(updated_at__date__range=[start_date, end_date])

    if min_price and max_price:
        try:
            min_price = float(min_price)
            max_price = float(max_price)
            orders = orders.filter(total_amount__range=[min_price, max_price])
        except ValueError:
            pass

    total_amount = orders.aggregate(
        total=Coalesce(Sum('total_amount'), 0, output_field=DecimalField())
    )['total']
    
    total_sale_discount = orders.aggregate(
        discount=Coalesce(Sum('total_discount'), 0, output_field=DecimalField())
    )['discount']
    
    order_count = orders.count()

    average_price = round(total_amount / order_count, 2) if order_count > 0 else 0

    total_product_sales = OrderItem.objects.filter(order__in=orders).aggregate(
        total_sales=Coalesce(Sum('quantity'), 0, output_field=DecimalField())  # Ensure no None values
    )['total_sales']
    
    product_popularity = Product.objects.filter(orderitem__order__in=orders).annotate(
        total_sales=Coalesce(Sum('orderitem__quantity'), 0, output_field=DecimalField()),
        sales_percentage=Cast(
            Coalesce(Sum('orderitem__quantity'), 0) * 100.0 / (total_product_sales if total_product_sales > 0 else 1), 
            FloatField()
        )
    ).order_by('-total_sales')[:5]

    total_collection_sales = OrderItem.objects.filter(order__in=orders).aggregate(
        total_sales=Coalesce(Sum('quantity'), 0, output_field=DecimalField())  # Ensure no None values
    )['total_sales']
    
    collection_popularity = Collection.objects.filter(product__orderitem__order__in=orders).annotate(
        total_sales=Coalesce(Sum('product__orderitem__quantity'), 0, output_field=DecimalField()),
        sales_percentage=Cast(
            Coalesce(Sum('product__orderitem__quantity'), 0) * 100.0 / (total_collection_sales if total_collection_sales > 0 else 1),
            FloatField()
        )
    ).order_by('-total_sales')[:5]

    def generate_line_graph(data, title, x_label, y_label):
        try:
            fig, ax = plt.subplots(figsize=(10, 5))  # Notice the different width and height
            ax.plot([item.name for item in data], 
                    [item.total_sales for item in data], 
                    marker='o')
            ax.set_title(title)
            ax.set_xlabel(x_label)
            ax.set_ylabel(y_label)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()

            buffer = io.BytesIO()
            fig.savefig(buffer, format='png')
            buffer.seek(0)
            graph = base64.b64encode(buffer.getvalue()).decode('utf-8')
            plt.close(fig)  # Close the specific figure
            return graph
        except Exception as e:
            return None

    def generate_pie_chart(data, title):
        try:
            fig, ax = plt.subplots(figsize=(8, 8))  # Equal width and height
            ax.pie([item.sales_percentage for item in data], 
                    labels=[item.name for item in data], 
                    autopct='%1.1f%%')
            ax.set_title(title)
            ax.axis('equal')

            buffer = io.BytesIO()
            fig.savefig(buffer, format='png')
            buffer.seek(0)
            chart = base64.b64encode(buffer.getvalue()).decode('utf-8')
            plt.close(fig)  # Close the specific figure
            return chart
        except Exception as e:
            return None

    product_line_graph = None
    product_pie_graph = None
    collection_line_graph = None
    collection_pie_graph = None
    
    if product_popularity:
        product_line_graph = generate_line_graph(
            product_popularity, 
            'Product Sales Trend', 
            'Product Name', 
            'Total Sales'
        )
        product_pie_graph = generate_pie_chart(
            product_popularity, 
            'Product Sales Percentage'
        )
    
    if collection_popularity:
        collection_line_graph = generate_line_graph(
            collection_popularity, 
            'Collection Sales Trend', 
            'Collection Name', 
            'Total Sales'
        )
        collection_pie_graph = generate_pie_chart(
            collection_popularity, 
            'Collection Sales Percentage'
        )

    plt.close('all')

    context = {
        'sales': orders,
        'total_revenue': total_amount,
        'total_sales': order_count,
        'average_price': average_price,
        'total_sale_discount': total_sale_discount,
        'product_line_graph': product_line_graph,
        'product_pie_graph': product_pie_graph,
        'collection_line_graph': collection_line_graph,
        'collection_pie_graph': collection_pie_graph,
        'product_popularity': product_popularity,
        'collection_popularity': collection_popularity
    }

    if request.GET.get('download_pdf') == '1':
        return generate_sales_pdf(request, context)
    
    return render(request, 'admin_sales.html', context=context)


def admin_list_offers(request):
    products = Product.objects.all()
    return render(request, 'offers/admin_list_offers.html', {'products': products})


def admin_add_offers(request):
    if request.method == 'POST':
        id = request.POST.get('product_id')
        offer_price = request.POST.get('offer_price')
        product = Product.objects.get(id=id)
        product.offer_price = offer_price
        product.save()
        return redirect('admin_offers')
    products = Product.objects.all()
    return render(request, 'offers/admin_add_offers.html', {'products': products})


@staff_member_required
def admin_delete_offer(request, id):
    product = Product.objects.get(id=id)
    product.offer_price = product.price
    product.save()
    return redirect('admin_offers')


@csrf_exempt
@staff_member_required(login_url="admin_login")
def upload_cropped_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image_file = request.FILES['image']
        # Save the file to media directory
        file_name = default_storage.save('products/' + image_file.name, image_file)
        file_url = default_storage.url(file_name)
        return JsonResponse({'status': 'success', 'file_url': file_url})
    return JsonResponse({'status': 'error'}, status=400)