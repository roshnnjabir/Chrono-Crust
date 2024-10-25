from django.shortcuts import render, redirect
from .models import CustomUser, Address
from adminapp.models import Product, Collection, Brand, Cart, CartItem
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import random, time
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.contrib.auth import get_backends
from django.core.cache import cache
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from datetime import timedelta
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import get_object_or_404


# Create your views here.

def user_home(request):
    products = Product.objects.filter(
        Q(is_listed=True),
        Q(collection__is_listed=True),
        Q(collection__brand__is_listed=True)
    )
    return render(request, 'user_home.html', {'products': products})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('user_profile')

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        if CustomUser.objects.filter(email=email).exists():
            user = authenticate(request, email=email, password=password)
            if user is not None:
                if user.is_staff:
                    login(request, user)
                    return redirect('user_profile')

                otp = generate_otp()
                send_otp_via_email(email, otp)

                # Store the OTP and timestamp in session
                request.session['email'] = email
                request.session['password'] = password
                request.session['otp'] = otp
                request.session['otp_timestamp'] = timezone.now().isoformat()
                messages.success(request, 'Otp Sent Successfully')
                return redirect('otp_page')
            else:
                messages.error(request, "Password Wrong")
        else:
            messages.error(request, 'Email Does Not Exist')

    return render(request, 'user_login.html')


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
    return render(request, 'user_forgot_password.html')


def user_reset_password(request):
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
    send_mail(subject, message, 'roshanjbair7@gmail.com', [email])


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
            print('uep')
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

                if reset_pass_email:
                    try:
                        user = CustomUser.objects.get(email=reset_pass_email)
                        del request.session['reset_pass_email']
                        return render(request, 'user_reset_password.html', {'user': user})
                    except CustomUser.DoesNotExist:
                        messages.error(request, 'No user found with the provided email address.')
                        return redirect('otp_page')
                elif signup_data:
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
    pass


@login_required(login_url='user_login')
def address_book(request):
    user = CustomUser.objects.get(email=request.user.email)
    addresses = user.addresses.all()

    # Handle the form submission to update addresses
    if request.method == 'POST':
        address_id = request.POST.get('address_id')
        address = Address.objects.get(id=address_id, user=user)
        address.street_address = request.POST.get('street_address')
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
        address.street_address = request.POST.get('street')
        address.city = request.POST.get('city')
        address.state = request.POST.get('state')
        address.postal_code = request.POST.get('postal_code')
        address.save()

        return redirect('user_address_book')  # Redirect after saving

    # If GET request (though this should not happen in your case)
    return redirect('user_address_book')  # Or you could render an error message


@login_required(login_url='user_login')
def add_user_address(request):
    if request.method == 'POST':
        # Check if the user already has 3 addresses
        if request.user.addresses.count() >= 3:
            messages.error(request, "You can only have a maximum of 3 addresses.")
            return redirect('user_address_book')  # Redirect back to the address creation page

        # Extract data from request.POST
        street_address = request.POST.get('street_address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        country = request.POST.get('country')
        postal_code = request.POST.get('postal_code')
        is_default = request.POST.get('is_default') == 'on'  # Convert checkbox to boolean

        # Create the Address instance
        address = Address(
            user=request.user,  # Set the current user
            street_address=street_address,
            city=city,
            state=state,
            country=country,
            postal_code=postal_code,
            is_default=is_default,
        )

        try:
            address.save()  # Try to save the address
            messages.success(request, "Address created successfully!")
            return redirect('user_address_book')  # Redirect to a success page or address list
        except ValidationError as e:
            messages.error(request, str(e))  # Handle validation errors and display messages

    return render(request, 'user_profile_addresses.html')


@login_required(login_url='user_login')
def delete_user_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.delete()
    messages.success(request, "Address deleted successfully.")
    return redirect('user_address_book')


@login_required(login_url='user_login')
def change_password(request):
    pass


@login_required(login_url='user_login')
def order_history(request):
    pass


@login_required(login_url='user_login')
def user_logout(request):
    logout(request)
    return redirect('user_home')


def view_product(request, id):
    product = Product.objects.get(id=id)
    print(product.is_listed, product.collection.is_listed, product.collection.brand.is_listed, product.stock)
    return render(request, 'user_product.html', {'product': product})


from django.http import HttpResponseRedirect


def user_add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)

        # Get or create the user's cart
        cart, created = Cart.objects.get_or_create(user=request.user)

        # Check if the product is already in the cart
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            # If the item already exists, update the quantity
            cart_item.quantity += 1  # Change this if you want to add a specific quantity
            cart_item.save()
        return redirect('cart_view')  # Redirect to a cart view or product detail page
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))  # Redirect back if not a POST request


def user_cart_view(request, user_id):
    if request.method == 'POST':
        email = request.POST['email']
        