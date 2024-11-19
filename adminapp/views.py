from django.shortcuts import render, redirect
from user.models import CustomUser
from .models import Product, Brand, Collection, Order, OrderItem, Coupen
from django.contrib.auth import logout, login, authenticate
from django.db.models import Q, Count
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.cache import never_cache
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from datetime import timedelta


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
    print(user.profile_image)
    addresses = user.addresses.all()
    print(addresses)
    context = {
        'user': user,
        'addresses': addresses,
        'show_order': False
    }
    return render(request, 'admin_show_user_details.html', context)


@staff_member_required(login_url="admin_login")
def admin_show_order_of_specific_user(request, id):
    user = get_object_or_404(CustomUser, id=id)
    print(user.profile_image)
    orders = user.orders.all()
    addresses = user.addresses.all()
    print(orders)
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
        print('Is active')
        user_data.is_active = False
    else:
        print('Is not active')
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
        print(request.POST['collection'], 'hrh')
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
        print(limited_edition)

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
        print(product.limited_edition)
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
        if Collection.objects.filter(name=collection_name).exists():
            messages.error(request, f"The collection '{collection_name}' already exists.")
            return redirect('admin_add_collection')
        brand = Brand.objects.get(id=brand_id)
        Collection.objects.create(name=collection_name, brand=brand)
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
        if Collection.objects.filter(name=collect_name, brand_id=brand_id).exclude(id=id).exists():
            messages.error(request, "Collection name already exists.")
        else:
            collection.name = collect_name
            brand = Brand.objects.get(id=brand_id)
            collection.brand = brand
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
        logo_image = request.POST.get('brandlogo')
        banner_image = request.POST.get('brandbanner')
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
    orders = Order.objects.all()
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

    users = CustomUser.objects.all()  # Get all users for the user filter
    return render(request, 'admin_list_orders.html', {
        'orders': orders,
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
    status_choices = Order.STATUS_CHOICES  # Get the status choices from the model
    payment_status_choices = Order.PAYMENT_STATUS_CHOICES
    return render(request, 'admin_order_details.html', {
        'order': order,
        'status_choices': status_choices,
        'payment_status_choices': payment_status_choices,
    })


@staff_member_required(login_url="admin_login")
@csrf_exempt
def update_order_status(request, order_id):
    if request.method == 'POST':
        try:
            order = Order.objects.get(id=order_id)
            new_status = request.POST.get('status')

            # Validate the new status against the model's status choices
            if new_status in dict(Order.STATUS_CHOICES):
                order.status = new_status
                order.save()
                return JsonResponse({'message': 'Order status updated successfully'})
            else:
                return JsonResponse({'error': 'Invalid status'}, status=400)
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found'}, status=404)


@staff_member_required(login_url="admin_login")
@csrf_exempt
def update_payment_status(request, order_id):
    if request.method == 'POST':
        try:
            order = Order.objects.get(user=request.user)
            print(order)
            new_payment_status = request.POST.get('payment_status')

            # Validate the new payment status against the model's choices
            if new_payment_status in dict(Order.PAYMENT_STATUS_CHOICES):
                order.payment_status = new_payment_status
                order.save()
                return JsonResponse({'message': 'Payment status updated successfully'})
            else:
                return JsonResponse({'error': 'Invalid payment status'}, status=400)
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found'}, status=404)


@staff_member_required(login_url="admin_login")
@never_cache
def admin_coupons(request):
    coupons = Coupen.objects.all()
    return render(request, 'admin_list_coupon.html', {'coupons': coupons})


# def admin_coupon_details(request, code):
#     coupen = Coupen.objects.get(code=code)
#     print(coupen)
#     return HttpResponse('ahj')


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
        print(active)
        
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
            usage_limit=usage_limit,
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
        usage_limit = request.POST.get('usage_limit')
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
        coupon.usage_limit = usage_limit
        coupon.valid_from = valid_from
        coupon.valid_to = valid_to
        coupon.active = active
        coupon.save()

        # Redirect to the list of coupons after editing
        messages.success(request, 'Coupon updated successfully')
        return redirect('admin_list_coupons')

    return render(request, 'admin_edit_coupon.html', {'coupon': coupon})


@csrf_exempt
def validate_coupon_ajax(request):
    if request.method == "POST":
        coupon_code = request.POST.get("coupon_code")
        selected_total = float(request.POST.get("selected_total"))

        try:
            coupon = Coupen.objects.get(code=coupon_code, active=True)
            
            # Check if coupon's minimum purchase requirement is met
            if hasattr(coupon, 'minimum_purchase') and selected_total < coupon.min_required:
                return JsonResponse({
                    "status": "error",
                    "message": f"Minimum purchase amount of ${coupon.min_required} required."
                })

            # Calculate discount
            discount_amount = selected_total * (int(coupon.discount_percentage) / 100)
            
            # If coupon has maximum discount limit
            if hasattr(coupon, 'maximum_discount') and discount_amount > coupon.maximum_discount:
                discount_amount = coupon.maximum_discount
            
            discounted_total = selected_total - discount_amount

            return JsonResponse({
                "status": "success",
                "original_total": selected_total,
                "discount_percentage": coupon.discount_percentage,
                "discount_amount": round(discount_amount, 2),
                "discounted_total": round(discounted_total, 2),
                "message": f"Coupon applied! {coupon.discount_percentage}% discount"
            })

        except Coupen.DoesNotExist:
            return JsonResponse({
                "status": "error", 
                "message": "Invalid or expired coupon code."
            })
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": "An error occurred while processing the coupon."
            })

    return JsonResponse({
        "status": "error", 
        "message": "Invalid request method."
    })


def admin_delete_coupon(request, code):
    coupen = Coupen.objects.get(code=code)
    coupen.delete()
    return redirect('admin_list_coupons')


def admin_sales(request):
    orders = Order.objects.all()
    total_amount = 0
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    order_count = orders.count()
    if order_count > 0:
        average_price = round(total_amount/order_count, 2)
    else:
        average_price = 0

    if start_date and end_date:
        orders = orders.filter(updated_at__date__range=[start_date, end_date])

    if min_price and max_price:
        orders = orders.filter(total_amount__range=[min_price, max_price])

    for order in orders:
        total_amount += order.total_amount
        print(total_amount)
    context = {
        'sales': orders,
        'total_revenue': total_amount,
        'total_sales': orders.count(),
        'average_price': average_price
    }
    return render(request, 'admin_sales.html', context=context)


def admin_list_offers(request):
    products = Product.objects.all()
    return render(request, 'admin_list_offers.html', {'products': products})


def admin_add_offers(request):
    if request.method == 'POST':
        id = request.POST.get('product_id')
        offer_price = request.POST.get('offer_price')
        print(id)
        product = Product.objects.get(id=id)
        product.offer_price = offer_price
        print(product.offer_price)
        product.save()
        return redirect('admin_offers')
    products = Product.objects.all()
    return render(request, 'admin_add_offers.html', {'products': products})


def admin_delete_offer(request):
    pass


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
