from django.shortcuts import render, redirect
from .models import CustomUser, Address
from adminapp.models import Product, Product_Slider, Collection, Brand, Cart, CartItem, Wishlist, WishlistItem, Order, OrderItem, PersonalWallet, Coupen, PersonalWalletTransactions
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import random, time
import json
import uuid
from django.db import transaction
from django.views.decorators.cache import never_cache
from django.core.exceptions import ValidationError
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.contrib.auth import get_backends
from django.core.cache import cache
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from datetime import timedelta
from django.core.mail import send_mail
from django.db.models import Q
from decimal import Decimal
from django.shortcuts import get_object_or_404
from django.urls import reverse
import razorpay
from django.conf import settings
from django.template.loader import render_to_string
from weasyprint import HTML
from django.views.decorators.http import require_http_methods
from itertools import chain


def user_home(request):
    products = Product.objects.filter(
        Q(is_listed=True),
        Q(collection__is_listed=True),
        Q(collection__brand__is_listed=True),
        Q(for_men=True) | Q(for_women=True)
    ).order_by('-popularity')[:3]

    product_slider = Product_Slider.objects.all()

    return render(request, 'user_home.html', {
        'products': products,
        'product_slider': product_slider,
    })


def user_list_product(request):
    products = Product.objects.filter(
        Q(is_listed=True),
        Q(collection__is_listed=True),
        Q(collection__brand__is_listed=True),
        Q(for_men=True) | Q(for_women=True)
    )
    return render(request, 'user_list_product.html', {'products': products})


def user_list_product_catogory(request):
    products = Product.objects.filter(
        Q(is_listed=True),
        Q(collection__is_listed=True),
        Q(collection__brand__is_listed=True),
        Q(for_men=True) | Q(for_women=True)
    )

    # Handle sorting
    sort_option = request.GET.get('sort')
    if sort_option == 'name_asc':
        products = products.order_by('name')  # A-Z
    elif sort_option == 'name_desc':
        products = products.order_by('-name')  # Z-A
    elif sort_option == 'price_asc':
        products = products.order_by('price')  # Low to High
    elif sort_option == 'price_desc':
        products = products.order_by('-price')  # High to Low
    elif sort_option == 'newest':
        products = products.order_by('-created_at')  # Newest first
    elif sort_option == 'popularity':
        products = products.order_by('-popularity')  # Assuming you have a popularity field

    gender_filter = request.GET.get('gender_filter')

    if gender_filter:
        if gender_filter == 'men':
            products = Product.objects.filter(
                Q(for_men=True),
                Q(for_women=False),
                Q(is_listed=True),
                Q(collection__is_listed=True),
                Q(collection__brand__is_listed=True)
            )
        elif gender_filter == 'women':
            products = Product.objects.filter(
                Q(for_women=True),
                Q(for_men=False),
                Q(is_listed=True),
                Q(collection__is_listed=True),
                Q(collection__brand__is_listed=True)
            )
        elif gender_filter == 'unisex':
            products = Product.objects.filter(
                Q(for_women=True),
                Q(for_men=True),
                Q(is_listed=True),
                Q(collection__is_listed=True),
                Q(collection__brand__is_listed=True)
            )
    return render(request, 'user_list_product_catogory.html', {'products': products})


def user_list_brand(request):
    brands = Brand.objects.filter(
        Q(is_listed=True)
    )
    return render(request, 'user_list_brands.html', {'brands': brands})


def user_list_collection(request):
    collection = Collection.objects.filter(
        Q(is_listed=True),
        Q(brand__is_listed=True)
    )
    return render(request, 'user_list_collection.html', {'collections': collection})


@never_cache
def user_login(request):
    if request.user.is_authenticated:
        return redirect('user_profile')

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        if CustomUser.objects.filter(email=email).exists():
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('user_profile')
            else:
                messages.error(request, "Password Wrong")
        else:
            messages.error(request, 'Email Does Not Exist')

    return render(request, 'user_login.html')


@never_cache
def user_signup(request):
    if request.user.is_authenticated:
        return redirect('user_profile')

    if request.method == 'POST':
        FirstName = request.POST.get('FirstName')
        LastName = request.POST.get('LastName')
        email = request.POST.get('email')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')

        user_data = {
            'FirstName': FirstName,
            'LastName': LastName,
            'email': email,
            'pass1': pass1,
            'pass2': pass2
        }

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email Already Exists')
            return render(request, 'user_signup.html', {'user': user_data})

        if pass1 != pass2:
            messages.error(request, "Your password and confirm password do not match!")
            return render(request, 'user_signup.html', {'user': user_data})

        # If all checks pass, generate an OTP and send it to the user's email
        otp = generate_otp()
        send_otp_via_email(email, otp)

        # Store user details and OTP in session for later verification
        request.session['signup_data'] = user_data
        request.session['otp'] = otp
        request.session['otp_timestamp'] = timezone.now().isoformat()

        messages.success(request, 'OTP sent successfully for verification!')
        return redirect('otp_page')  # Redirect to the OTP verification page

    return render(request, 'user_signup.html')


@never_cache
def user_forgot_password(request):
    if request.method == "POST":
        email = request.POST['email']

        if CustomUser.objects.filter(email=email).exists():
            otp = generate_otp()

            request.session['otp'] = otp
            request.session['otp_timestamp'] = timezone.now().isoformat()
            request.session['reset_pass_email'] = email
            send_otp_via_email(email=email, otp=otp)
            messages.success(request, 'OTP sent successfully for reset password!')
            return redirect('otp_page')
        else:
            messages.error(request, 'Email Does Not Exist')
            return redirect('user_forgot_password')
    try:
        user = CustomUser.objects.get(email=request.user)
        return render(request, 'user_forgot_password.html', {'user': user})
    except CustomUser.DoesNotExist:
        return render(request, 'user_forgot_password.html')


@never_cache
def user_reset_password(request):
    if request.user.is_authenticated:
        return redirect('user_profile')
    if request.method == "POST":
        email = request.POST.get('email') or request.session.get('reset_email')
        password = request.POST.get('password')
        cpassword = request.POST.get('confirm_password')

        if email:
            request.session['reset_email'] = email

        user = CustomUser.objects.filter(email=email).first()

        if user is not None:
            # Check if passwords match
            if password != cpassword:
                messages.error(request, 'Passwords do not match. Please try again.')
                return render(request, 'user_reset_password.html', {'user': user})

            # Check if new password is different from the old one
            if user.check_password(password):
                messages.error(request, 'Password cannot be an existing password.')
                return render(request, 'user_reset_password.html', {'user': user})

            # Set new password and log the user in
            user.set_password(password)
            user.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            request.session.pop('reset_email', None)  # Clear email from session after success
            messages.success(request, 'Your password was reset successfully.')
            return redirect('user_profile')
        else:
            messages.error(request, 'Email does not exist.')
            return redirect('user_forgot_password')

    # Render form if GET request
    else:
        email = request.session.get('reset_email')
        user = CustomUser.objects.filter(email=email).first() if email else None
        return render(request, 'user_reset_password.html', {'user': user})


def otp_page(request):
    return render(request, 'user_otp.html', {'start_timer': True})


def generate_otp():
    return random.randint(100000, 999999)


def send_otp_via_email(email, otp):
    subject = 'Your OTP Code'
    message = f'Your OTP code for login to ChronoCrust is {otp}. It is valid for 5 minutes.'
    send_mail(subject, message, 'roshanjabir7@gmail.com', [email])


def resend_otp(request):
    email = request.session.get('email')
    signup_data = request.session.get('signup_data')
    reset_password_email = request.session.get('reset_pass_email')
    otp = generate_otp()  # Generate a new OTP
    if reset_password_email:
        request.session['otp'] = otp
        request.session['otp_timestamp'] = timezone.now().isoformat()
        if CustomUser.objects.filter(email=reset_password_email).exists():
            send_otp_via_email(email=reset_password_email, otp=otp)
            messages.success(request, 'Otp Resent Successfully')
        else:
            messages.error(request, 'Email Does Not Exist')
            return redirect('user_profile')
    elif signup_data:  # Check if email is present in session
        # Save the new OTP and current timestamp in the session
        request.session['otp'] = otp
        request.session['otp_timestamp'] = timezone.now().isoformat()
        email = signup_data['email']
        send_otp_via_email(email=email, otp=otp)
        messages.success(request, 'Otp Resent Successfully')
    elif email:  # Check if email is present in session
        # Save the new OTP and current timestamp in the session
        request.session['otp'] = otp
        request.session['otp_timestamp'] = timezone.now().isoformat()
        if CustomUser.objects.filter(email=email).exists():
            send_otp_via_email(email=email, otp=otp)
            messages.success(request, 'Otp Resent Successfully')
        else:
            messages.error(request, 'Email Does Not Exist')
            return redirect('user_profile')
    else:
        messages.error(request, 'Error resending the OTP')
    return redirect('otp_page')


def verify_otp(request):
    if request.method == "POST":
        user_otp = request.POST.get('otp')  # Use get() for safer access
        saved_otp = request.session.get('otp')
        otp_timestamp = request.session.get('otp_timestamp')

        if saved_otp and otp_timestamp:
            timestamp = timezone.datetime.fromisoformat(otp_timestamp)

            if str(user_otp) == str(saved_otp) and (timezone.now() - timestamp <= timedelta(minutes=5)):
                signup_data = request.session.get('signup_data')
                reset_pass_email = request.session.get('reset_pass_email')

                if signup_data:
                    my_user = CustomUser.objects.create_user(
                        email=signup_data['email'],
                        password=signup_data['pass1'],  # Use the stored password
                        first_name=signup_data['FirstName'],
                        last_name=signup_data['LastName'],
                    )
                    my_user.save()
                    loguser = authenticate(email=signup_data['email'], password=signup_data['pass1'])
                    if loguser:
                        login(request, loguser)
                        messages.success(request, 'Your account has been created successfully!')
                    else:
                        messages.error(request, 'Authentication failed. Please try again.')
                    del request.session['signup_data']
                elif reset_pass_email:
                    try:
                        user = CustomUser.objects.get(email=reset_pass_email)
                        del request.session['reset_pass_email']
                        return render(request, 'user_reset_password.html', {'user': user})
                    except CustomUser.DoesNotExist:
                        messages.error(request, 'No user found with the provided email address.')
                        return redirect('otp_page')
                else:
                    loguser = authenticate(email=request.session.get('email'), password=request.session.get('password'))
                    if loguser and loguser.is_active:
                        login(request, loguser)
                        messages.success(request, 'Login Successful')
                    else:
                        messages.error(request, 'User Blocked By Admins or Invalid credentials.')
                    del request.session['password']
                    del request.session['email']
                del request.session['otp']
                del request.session['otp_timestamp']
                return redirect('user_profile')
            else:
                messages.error(request, 'Invalid OTP or OTP has expired. Please try again.')
        else:
            messages.error(request, 'No OTP found. Please request a new one.')
    return redirect('otp_page')


def google_login_redirect(request):
    client_id = settings.SOCIALACCOUNT_PROVIDERS['google']['APP']['client_id']
    redirect_uri = request.build_absolute_uri('/accounts/google/login/callback/')

    google_login_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        "&response_type=code"
        "&scope=openid%20email%20profile"
    )

    return redirect(google_login_url)

@login_required(login_url='user_login')
def user_profile(request):
    if request.user.is_authenticated:
        user = CustomUser.objects.get(email=request.user.email)
        date_of_birth_str = str(user.date_of_birth)
        return render(request, 'user_profile.html', {'user': user, 'date_of_birth': date_of_birth_str})
    return redirect('login')


@login_required(login_url='user_login')
def user_profile_update(request):
    if request.method == 'POST':
        firstname = request.POST['FirstName']
        lastname = request.POST['LastName']
        email = request.POST['Email']
        phone = request.POST['Phone']
        dob = request.POST['Date_of_birth']
        user_data = CustomUser.objects.get(email=email)
        user_data.first_name = firstname
        user_data.last_name = lastname
        user_data.date_of_birth = dob
        if len(phone) != 10:
            messages.error(request, 'Phone Number Should Be Integer and 10 Digits')
            return redirect('user_profile')
        user_data.phone = phone
        user_data.save()
    return redirect('user_profile')


@login_required(login_url='user_login')
def personal_wallet(request):
    try:
        personal_wallet = PersonalWallet.objects.get(user=request.user)
    except PersonalWallet.DoesNotExist:
        personal_wallet = PersonalWallet.objects.create(user=request.user)
    transactions = personal_wallet.items.all()
    return render(request, 'user_wallet_chrono_crust.html', {'personal_wallet': personal_wallet, 'transactions': transactions})


@never_cache
@login_required(login_url='user_login')
def address_book(request):
    user = CustomUser.objects.get(email=request.user.email)
    addresses = Address.objects.filter(user=user, is_listed=True)

    # Handle the form submission to update addresses
    if request.method == 'POST':
        address_id = request.POST.get('address_id')
        address = Address.objects.get(id=address_id, user=user)
        address.street_address = request.POST.get('building_name')
        address.city = request.POST.get('city')
        address.state = request.POST.get('state')
        address.postal_code = request.POST.get('postal_cod')
        address.save()
        return redirect('user_address_book')  # Redirect after saving

    context = {
        'user': user,
        'addresses': addresses,
    }
    return render(request, 'user_profile_addresses.html', context)


@login_required(login_url='user_login')
def edit_user_address(request):
    # Get the logged-in user
    user = CustomUser.objects.get(email=request.user.email)

    # Handle the form submission to update the address
    if request.method == 'POST':
        # Retrieve the address ID from the hidden input field
        address_id = request.POST.get('address_id')
        address = get_object_or_404(Address, id=address_id, user=user)

        # Update the address fields
        address.building_name = request.POST.get('building_name')
        address.landmark = request.POST.get('landmark')
        address.city = request.POST.get('city')
        address.district = request.POST.get('district')
        address.state = request.POST.get('state')
        address.country = request.POST.get('country')
        address.postal_code = request.POST.get('postal_code')
        phone = request.POST.get('phone')

        # Validate the phone number (must be exactly 10 digits)
        if not phone.isdigit() or len(phone) != 10:
            messages.error(request, "Phone number must be exactly 10 digits.")
            return redirect('user_address_book')

        # Update the phone field
        address.phone = phone

        # Save the updated address
        address.save()
        messages.success(request, "Address updated successfully!")

        return redirect('user_address_book')  # Redirect after saving

    # If GET request (though this should not happen in your case)
    return redirect('user_address_book')


@login_required(login_url='user_login')
def add_user_address(request):
    if request.method == 'POST':
        # Check if the user already has 3 addresses
        if request.user.addresses.filter(is_listed=True).count() >= 3:
            messages.error(request, "You can only have a maximum of 3 addresses.")
            return redirect('user_address_book')

        # Extract data from request.POST
        building_name = request.POST.get('building_name')
        landmark = request.POST.get('landmark')
        city = request.POST.get('city')
        district = request.POST.get('district')
        state = request.POST.get('state')
        country = request.POST.get('country')
        postal_code = request.POST.get('postal_code')
        phone = request.POST.get('phone')
        is_default = request.POST.get('is_default') == 'on'  # Convert checkbox to boolean by using == 'on'
        # Validate the phone number (must be exactly 10 digits)
        if not phone.isdigit() or len(phone) != 10:
            messages.error(request, "Phone number must be exactly 10 digits.")
            return redirect('user_address_book')

        # Create the Address instance
        address = Address(
            user=request.user,  # set current logged in user
            building_name=building_name,
            landmark=landmark,
            city=city,
            district=district,
            state=state,
            country=country,
            postal_code=postal_code,
            phone=phone,
            is_default=is_default,
        )

        try:
            address.save()  # saving the address
            messages.success(request, "Address created successfully!")
            return redirect('user_address_book')
        except ValidationError as e:
            messages.error(request, str(e))  # error mesage

    return render(request, 'user_profile_addresses.html')


@login_required(login_url='user_login')
def add_user_address_on_order(request):
    if request.method == 'POST':
        # Check if the user already has 3 addresses
        if request.user.addresses.filter(is_listed=True).count() >= 3:
            messages.error(request, "You can only have a maximum of 3 addresses.")
            return redirect('user_address_book')

        # Extract data from request.POST
        building_name = request.POST.get('building_name')
        landmark = request.POST.get('landmark')
        city = request.POST.get('city')
        district = request.POST.get('district')
        state = request.POST.get('state')
        country = request.POST.get('country')
        postal_code = request.POST.get('postal_code')
        phone = request.POST.get('phone')
        is_default = request.POST.get('is_default') == 'on'  # Convert checkbox to boolean by using == 'on'
        # Validate the phone number (must be exactly 10 digits)
        if not phone.isdigit() or len(phone) != 10:
            messages.error(request, "Phone number must be exactly 10 digits.")
            return redirect('user_address_book')

        # Create the Address instance
        address = Address(
            user=request.user,  # set current logged in user
            building_name=building_name,
            landmark=landmark,
            city=city,
            district=district,
            state=state,
            country=country,
            postal_code=postal_code,
            phone=phone,
            is_default=is_default,
        )

        try:
            address.save()  # saving the address
            messages.success(request, "Address created successfully!")
            return redirect('user_address_book')
        except ValidationError as e:
            messages.error(request, str(e))  # error mesage

    return render(request, 'user_profile_addresses.html')


@login_required(login_url='user_login')
def delete_user_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.is_listed = False
    address.save()
    messages.success(request, "Address deleted successfully.")
    return redirect('user_address_book')


@login_required(login_url='user_login')
def change_password(request):
    pass


@never_cache
@login_required(login_url='user_login')
def user_cart_view(request):
    if request.user.is_authenticated:
        email = request.user.email
        user = CustomUser.objects.get(email=email)
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            cart = Cart.objects.create(user=user)

        # Handle item removal if it's a POST request
        if request.method == 'POST':
            item_id = request.POST.get('item_id')
            if item_id:
                try:
                    cart_item = CartItem.objects.get(cart=cart, id=item_id)
                    cart_item.delete()
                except CartItem.DoesNotExist:
                    pass  # Handle the case where the item does not exist

        # Fetch cart items after potential deletion
        cart_items = cart.items.all()
        total_price = cart.total_price
        return render(request, 'user_cart/user_cart_view.html', {'cart_items': cart_items, 'total_price': total_price})

    return HttpResponse('Unauthorized', status=401)  # More informative unauthorized response


@csrf_exempt
@never_cache
@login_required(login_url='user_login')
@require_POST
def update_cart_item_quantity_ajax(request):
    item_id = request.POST.get("item_id")
    new_quantity = request.POST.get("quantity")

    try:
        # Ensure new_quantity is a valid integer
        new_quantity = int(new_quantity)
        if new_quantity < 0:
            return JsonResponse({"status": "error", "message": "Quantity must be at least 1."})
        elif new_quantity > 8:
            return JsonResponse({"status": "error", "message": "Quantity Cannot be at greater than 8."})

        # Retrieve the cart item and update its quantity
        cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
        cart_item.quantity = new_quantity
        cart_item.save()

        # Calculate updated prices
        item_total_price = cart_item.total_price
        cart_total_price = cart_item.cart.total_price

        # Prepare the response data
        response_data = {
            'id': cart_item.id,
            'product_name': cart_item.product.name,
            'quantity': cart_item.quantity,
            'item_total_price': f"{item_total_price:.3f}",
            'total_price': f"{cart_total_price:.3f}",
            'price': f"{cart_item.product.offer_price:.3f}"
        }

        return JsonResponse({"status": "success", 'cart_item': response_data})

    except ValueError:
        return JsonResponse({"status": "error", "message": "Invalid quantity."})
    except Product.DoesNotExist:
        return JsonResponse({"status": "error", "message": 'Product does not exist'})
    except CartItem.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Item not found in cart."})
    except Exception as e:
        # Log the exception and return a generic error
        return JsonResponse({"status": "error", "message": "An error occurred. Please try again."})


@never_cache
def remove_from_cart(request, item_id):
    if request.method == 'POST':
        cart = Cart.objects.get(user=request.user)
        try:
            cart_item = CartItem.objects.get(cart=cart, product__id=item_id)
            cart_item.delete()
        except CartItem.DoesNotExist:
            pass  # Optionally handle the case where the item does not exist
    return redirect('user_cart_view')  # Redirect back to the cart view


@login_required(login_url='user_login')
@never_cache
def user_wishlist_view(request):
    if request.user.is_authenticated:
        email = request.user.email
        user = CustomUser.objects.get(email=email)
        try:
            wishlist = Wishlist.objects.get(user=user)
        except Cart.DoesNotExist:
            wishlist = Wishlist.objects.create(user=user)
        wishlist_items = wishlist.items.all()
        return render(request, 'user_wishlist/user_wishlist_view.html', {'wishlist_items': wishlist_items})
    return HttpResponse('shajh')


@never_cache
def user_move_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        wishlist_item_id = request.POST.get('wishlist_item_id')

        # Get the product and remove it from the wishlist
        product = get_object_or_404(Product, id=product_id)
        wishlist_item = get_object_or_404(WishlistItem, id=wishlist_item_id)

        # Add the product to the cart
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            # If the item already exists in the cart, update the quantity
            cart_item.quantity += 1  # or any other logic you want to implement
            cart_item.save()

        # Remove the item from the wishlist
        wishlist_item.delete()

        messages.success(request, f"{product.name} has been moved to your cart.")
        return redirect('user_wishlist_view')

    return redirect('user_wishlist_view')  # Redirect back if not a POST request


@login_required(login_url='user_login')
def user_remove_from_wishlist(request):
    if request.method == 'POST':
        wishlist_item_id = request.POST.get('wishlist_item_id')
        if wishlist_item_id:
            try:
                wishlist_item = WishlistItem.objects.get(id=wishlist_item_id)
                wishlist_item.delete()
            except WishlistItem.DoesNotExist:
                pass  # Handle the case where the item does not exist

    return redirect('user_wishlist_view')  # Redirect back to the wishlist view


@login_required(login_url='user_login')
def user_add_to_wishlist(request):
    if request.user.is_authenticated:
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)

        # Get or create the user's wishlist
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)

        # Check if the product is already in the wishlist
        if WishlistItem.objects.filter(wishlist=wishlist, product=product).exists():
            messages.info(request, 'Product is already in your wishlist.')
            return redirect('user_wishlist_view')
        elif CartItem.objects.filter(cart__user=request.user, product=product).exists():
            messages.info(request, 'Product is already in your cart.')
            return redirect('user_cart_view')
        else:
            WishlistItem.objects.create(wishlist=wishlist, product=product)
            messages.success(request, 'Product added to your wishlist.')
            return redirect('user_wishlist_view')
    else:
        messages.error(request, 'You need to be logged in to add items to your wishlist.')
        return redirect('user_profile')  # Redirect to the user profile or login page


@login_required(login_url='user_login')
def user_move_to_wishlist(request, item_id):
    # Retrieve the cart item by ID and check if it belongs to the current user
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product = cart_item.product

    # Get or create the user's wishlist
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)

    # Check if the product is already in the wishlist
    if WishlistItem.objects.filter(wishlist=wishlist, product=product).exists():
        messages.info(request, 'Product is already in your wishlist.')
    else:
        # Add the product to the wishlist and remove it from the cart
        WishlistItem.objects.create(wishlist=wishlist, product=product)
        cart_item.delete()
        messages.success(request, 'Product moved to your wishlist.')

    # Redirect back to the cart view
    return redirect('user_cart_view')


def generate_order_id():
    return f"order_{uuid.uuid4().hex[:10]}"  # First 10 characters of the UUID


@csrf_exempt  # Only use in development; ensure CSRF protection for deployment
@never_cache
def user_move_to_order(request):
    if request.method == 'POST':
        # Handle JSON payload (Razorpay payment)
        if request.headers.get('Content-Type') == 'application/json':
            data = json.loads(request.body)
            payment_id = data.get('payment_id')
            total_amount = request.session.get('total_price')
            discounted_amount = request.session.get('discount')
            order_id = data.get('order_id')
            payment_status = data.get('payment_status')

            try:
                # Attempt to retrieve existing order or create a new one
                order = Order.objects.get(id=order_id, user=request.user)
            except Order.DoesNotExist:
                # Create a new order if it doesn't exist
                item_ids = request.session.get('item_ids')
                selected_address_id = request.session.get('selected_address')

                if not item_ids or not selected_address_id:
                    return JsonResponse({'status': 'error', 'message': 'Incomplete order details.'}, status=400)

                item_ids = item_ids.split(',') if item_ids else []

                # Get the selected address
                try:
                    selected_address = Address.objects.get(id=selected_address_id, user=request.user)
                except Address.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': 'No Address Selected'}, status=400)

                # Create a new order with default pending status
                order = Order.objects.create(
                    id=order_id, 
                    user=request.user, 
                    address=selected_address,
                    total_amount=total_amount, 
                    discounted_amount=discounted_amount, 
                    payment_status='pending'
                )
                
                # Clear session discount and total price
                del request.session['discount']
                del request.session['total_price']

                # Process cart items and create order items
                for item_id in item_ids:
                    try:
                        cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)

                        # Create OrderItem
                        order_item = OrderItem.objects.create(
                            order=order,
                            product=cart_item.product,
                            quantity=cart_item.quantity,
                            price=cart_item.product.offer_price
                        )

                        # Adjust product stock
                        product = cart_item.product
                        if product.stock >= cart_item.quantity:
                            product.stock -= cart_item.quantity
                            product.save()
                        else:
                            return JsonResponse({'status': 'error', 'message': f'Insufficient stock for {product.name}'}, status=400)

                        # Remove item from cart
                        cart_item.delete()

                    except CartItem.DoesNotExist:
                        continue

            # Handle different payment scenarios
            if payment_status == 'cancelled':
                # Handle modal dismissal
                order.payment_status = 'failed'
                
                order.save()
                messages.warning(request, 'Payment Failed. Order Placed with Pending Payment.')
                return JsonResponse({'status': 'success', 'message': 'Order saved with cancelled payment'})

            # Verify payment status
            try:
                # Verify payment with Razorpay (recommended)
                razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
                payment_details = razorpay_client.payment.fetch(payment_id)
                
                if payment_details['status'] == 'captured':
                    # Payment successful
                    order.payment_id = payment_id
                    order.payment_status = 'paid'
                    messages.success(request, 'Payment Successful. Order Placed.')
                else:
                    # Payment failed
                    order.payment_id = payment_id
                    order.payment_status = 'failed'
                    messages.warning(request, 'Payment Failed. Order Placed with Pending Payment.')
            except Exception as e:
                # Payment verification failed
                order.payment_id = payment_id
                order.payment_status = 'failed'
                messages.warning(request, 'Payment Verification Failed. Order Placed with Pending Payment.')

            # Save the order with updated payment status
            order.save()

            # Respond with success
            return JsonResponse({'status': 'success'})

        # Handle non-JSON requests (Cash on Delivery or Wallet)
        else:
            payment_method = request.POST.get('payment_method')
            item_ids = request.session.get('item_ids')
            selected_address_id = request.session.get('selected_address')
            discounted_amount = request.session.get('discount')
            total_price = request.session.get('total_price')
            order_id = generate_order_id()

            if not item_ids or not selected_address_id:
                return JsonResponse({'status': 'error', 'message': 'Incomplete order details.'}, status=400)

            item_ids = item_ids.split(',') if item_ids else []

            # Get the selected address
            try:
                selected_address = Address.objects.get(id=selected_address_id, user=request.user)
            except Address.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'No Address Selected'}, status=400)

            with transaction.atomic():
                # Create a new order for COD or Wallet
                order = Order.objects.create(
                    id=order_id, 
                    user=request.user, 
                    address=selected_address, 
                    payment_status=payment_method, 
                    total_amount=total_price, 
                    discounted_amount=discounted_amount
                )
                
                # Clear session data
                del request.session['discount']
                del request.session['total_price']

                # Process cart items
                for item_id in item_ids:
                    try:
                        cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)

                        # Create OrderItem
                        order_item = OrderItem.objects.create(
                            order=order,
                            product=cart_item.product,
                            quantity=cart_item.quantity,
                            price=cart_item.product.offer_price,
                        )

                        # Adjust product stock
                        product = cart_item.product
                        if product.stock >= cart_item.quantity:
                            product.stock -= cart_item.quantity
                            product.save()
                        else:
                            return JsonResponse({'status': 'error', 'message': f'Insufficient stock for {product.name}'}, status=400)

                        # Remove item from cart
                        cart_item.delete()
                        messages.success(request, f'Order Placed Successfully via {payment_method.upper()}.')

                    except CartItem.DoesNotExist:
                        continue
                return redirect('user_order_history')
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


def prepare_razorpay_payment(request, order_id):
    try:
        # Retrieve the specific order
        order = Order.objects.get(id=order_id, user=request.user, payment_status='failed')
        # Initialize Razorpay client
        razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

        # Create Razorpay order
        razorpay_order = razorpay_client.order.create({
            'amount': int(order.total_amount * 100),  # amount in paise
            'currency': 'INR',
            'payment_capture': 1  # Auto-capture payment
        })

        # Update order with Razorpay order ID
        order.id = razorpay_order['id']
        order.save()
        
        # Prepare response
        return JsonResponse({
            'razorpay_key': settings.RAZOR_KEY_ID,
            'razorpay_order_id': razorpay_order['id'],
            'amount': int(order.total_amount * 100),
            'currency': 'INR'
        })
    
    except Order.DoesNotExist:
        print('dad400')
        return JsonResponse({'status': 'error', 'message': 'Order not found'}, status=404)
    except Exception as e:
        print('dad400')
        print(e)
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def verify_razorpay_payment(request):
    try:
        # Get data from the request body
        data = json.loads(request.body)

        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_signature = data.get('razorpay_signature')
        order_id = data.get('order_id')

        # Retrieve the order from the database
        order = Order.objects.get(id=order_id, user=request.user, payment_status='failed')
        print(order)

        # Verify the payment signature with Razorpay
        razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

        # Construct the data for signature verification
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }

        # Verify the payment signature
        try:
            razorpay_client.utility.verify_payment_signature(params_dict)

            # If payment signature verification is successful, we now check the payment status
            # Confirm that Razorpay has marked the payment as successful
            payment_details = razorpay_client.payment.fetch(razorpay_payment_id)

            if payment_details['status'] == 'success':
                # Update the order status to 'paid' if payment is successful
                order.payment_status = 'paid'
                
                order.save()

                # Respond with success
                return JsonResponse({'status': 'success', 'message': 'Payment verified successfully'}, status=200)
            else:
                # If Razorpay payment status is not 'success', return failure response
                return JsonResponse({'status': 'error', 'message': 'Payment failed'}, status=400)

        except razorpay.errors.SignatureVerificationError:
            # If signature verification fails, return error response
            return JsonResponse({'status': 'error', 'message': 'Payment signature verification failed'}, status=400)

    except Order.DoesNotExist:
        # If the order does not exist, return an error
        return JsonResponse({'status': 'error', 'message': 'Order not found'}, status=404)
    except Exception as e:
        # Handle any other exceptions
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required(login_url='user_login')
@never_cache
def user_order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-updated_at')
    return render(request, 'user_order_history.html', {'orders': orders})


def user_order_details(request, order_id):
    if request.method == 'GET':
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            items = [
                {
                    'product': {
                        'name': item.product.name,
                        'image_url': item.product.image.url,  # Adjust based on your image field
                        'offer_price': item.product.offer_price  # Assuming product has a 'price' field
                    },
                    'quantity': item.quantity,
                    'total_price': item.quantity * item.product.offer_price,
                }
                for item in order.items.all()
            ]

            # Calculate the total order price
            total_order_price = sum(item['total_price'] for item in items)

            # Start preparing the response data
            data = {
                'order': {
                    'id': order.id,
                    'date': order.updated_at.strftime('%Y-%m-%d %H:%M'),
                    'payment_status': order.payment_status,
                    'address': f"{order.address.building_name}, {order.address.city}, {order.address.state}, {order.address.postal_code}, {order.address.country}"
                },
                'items': items,
                'total_price': total_order_price,
                'total_discount': order.total_discount,
                'discounded_price': order.discounted_amount
            }

            # Add the order status only if the payment status is 'paid'
            if order.payment_status == 'paid':
                data['order']['status'] = order.status

            return JsonResponse(data)

        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found'}, status=404)


def user_cancel_order(request, order_id):
    if request.method == 'POST':
        # Fetch the order to be canceled
        order = get_object_or_404(Order, id=order_id)
        payment = get_object_or_404(PersonalWallet, user=request.user)

        # Check the order status and set the appropriate message
        if order.status == 'pending' or order.status == 'Pending' and order.payment_status == 'paid':
            try:
                # Loop through each OrderItem to update the stock
                for order_item in order.items.all():  # Adjusted to use 'items'
                    product = order_item.product
                    product.stock += order_item.quantity  # Restore the stock
                    
                    product.save()

                # Update the order status to 'Cancelled'
                order.status = 'cancelled'  # Use the correct choice value
                order.payment_status = 'refunded'
                order.save()  # Save the updated order
                payment.balance += order.total_amount
                payment.save()
        
                messages.success(request, 'Order has been successfully cancelled.')
            except Exception as e:
                # If there is an error while updating the order
                messages.error(request, f'Error canceling order: {e}')
        elif order.status == 'delivered':
            messages.error(request, f'Product already delivered to address {order.address}.')
        elif order.status == 'shipped':
            messages.error(request, 'Order has been shipped and cannot be cancelled.')
        else:
            messages.error(request, 'This order cannot be canceled.')

    # Redirect back to the order history page
    return redirect('user_order_history')


def address_selection(request):
    if request.method == 'POST':
        item_ids = request.POST.get('item_ids')
        discounted_price = request.POST.get('discounted_price')
        total_price = request.POST.get('total_price')

        request.session['discount'] = discounted_price
        request.session['total_price'] = total_price
        request.session['item_ids'] = item_ids

        user_addresses = Address.objects.filter(user=request.user, is_listed=True)
        return render(request, 'checkout/address_selection.html', {'user_addresses': user_addresses})
    return redirect('user_address_book')


razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))


@never_cache
def user_payment_method_selection(request):
    if request.method == 'POST':
        selected_address_id = request.POST.get('selected_address')
        request.session['selected_address'] = selected_address_id

        item_ids = request.session.get('item_ids')
        total_amount = request.session.get('discount')

        item_ids = item_ids.split(',') if item_ids else []

        client = razorpay.Client(auth=("rzp_test_ogXW1qOaXCrzZG", "xh7Hg2R6cJmhk7p02eCGhtZC"))
        if total_amount:
            amount = int(float(total_amount) * 100)
            personal_wallet = PersonalWallet.objects.get(user=request.user)
    
            data = {"amount": amount, "currency": "INR"}
            amount = amount/100
            payment = client.order.create(data=data)
            order_id = payment['id']
            return render(request, 'checkout/payment_method.html', {'order_id': order_id, 'total_amount': amount, 'personal_wallet_balance': personal_wallet})
    return redirect('user_profile')


@login_required(login_url='user_login')
def user_logout(request):
    logout(request)
    return redirect('user_home')


def view_product(request, id):
    product = Product.objects.get(id=id)
    return render(request, 'user_product.html', {'product': product})


def view_brand(request, id):
    brand = Brand.objects.get(id=id)
    lis = []
    for product_list in brand.collection.filter(is_listed=True): # appending all products in each collection so that we get a query set of all products inn each collection..then we use chain from iterable
        lis.append(list(product_list.product.filter(is_listed=True)))
    product = list(chain.from_iterable(lis)) # this will return a list with all the products from the given brand
    return render(request, 'user_list_product.html', {'products': product})


def view_collection(request, id):
    collection = Collection.objects.get(id=id)
    lis = []
    for product_list in collection.product.filter(is_listed=True):
        lis.append(product_list)
    print(lis)
    return render(request, 'user_list_product.html', {'products': lis})


@never_cache
def user_add_to_cart(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Login Required')
        return redirect('user_profile')

    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)

        # Get or create the user's cart
        cart, created = Cart.objects.get_or_create(user=request.user)

        # Check if the product is already in the cart
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            if cart_item.quantity >= int(product.stock):
                messages.error(request, f"Cannot add more than {product.stock} of {product.name} to the cart.")
                return redirect('user_cart_view')  # Redirect to cart view if stock limit reached
            elif cart_item.quantity >= 15:
                messages.error(request, f"Cannot add more than 15 of {product.name} to the cart.")
                return redirect('user_cart_view')
            else:
                cart_item.quantity += 1  # Increase quantity if stock is available
                cart_item.save()

        # Remove the product from the wishlist if it exists
        WishlistItem.objects.filter(wishlist__user=request.user, product=product).delete()

        return redirect('user_cart_view')  # Redirect to the cart view

    return redirect(request.META.get('HTTP_REFERER', '/'))  # Redirect back if not a POST request


@csrf_exempt
def validate_coupon_ajax(request):
    if request.method == "POST":
        coupon_code = request.POST.get("coupon_code")
        selected_total = float(request.POST.get("selected_total"))

        try:
            coupon = Coupen.objects.get(code=coupon_code, active=True)

            # Check if coupon's minimum purchase requirement is met
            if hasattr(coupon, 'min_required') and selected_total < coupon.min_required:
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


def add_money_to_wallet(request):
    pass


def user_generate_invoice(request, order_id):
    order = Order.objects.get(user=request.user, id=order_id)
    context = {
        'user': request.user,
        'order': order
    }
    html_string = render_to_string('invoice.html', context)
    html = HTML(string=html_string)
    pdf = html.write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="invoice_{order_id}.pdf"'
    return response
