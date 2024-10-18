from django.shortcuts import render, redirect
from .models import CustomUser
from adminapp.models import Product
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import random, time
from django.http import JsonResponse
from django.contrib.auth import get_backends
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail


# Create your views here.
def user_home(request):
    products = Product.objects.filter(is_listed=True)
    return render(request, 'user_home.html', {'products': products})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('user_home')

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
        return redirect('user_home')
    if request.method == 'POST':
        FirstName = request.POST.get('FirstName')
        LastName = request.POST.get('LastName')
        email = request.POST.get('email')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')
        user = {
            'FirstName': FirstName,
            'LastName': LastName,
            'email': email,
            'pass1': pass1,
            'pass2': pass2
        }
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email Already Exist')
            return render(request, 'user_signup.html', {'user': user})
        else:
            if pass1 != pass2:
                messages.error(request, "Your password and conform password are not Same!!")
                return render(request, 'user_signup.html', {'user': user})
            else:
                user = CustomUser.objects.create_user(email=email, first_name=FirstName, last_name=LastName, password=pass1)
                backend = get_backends()[0]
                user.backend = f'{backend.__module__}.{backend.__class__.__name__}'
                login(request, user, backend=user.backend)
                return redirect('user_profile')
    return render(request, 'user_signup.html')


def otp_page(request):
    return render(request, 'user_otp.html')


def generate_otp():
    return random.randint(100000, 999999)


def send_otp_via_email(email, otp):
    subject = 'Your OTP Code'
    message = f'Your OTP code for login to ChronoCrust is {otp}. It is valid for 5 minutes.'
    send_mail(subject, message, 'roshanjbair7@gmail.com', [email])


def resend_otp(request):
    email = request.session.get('email')
    print(email)
    otp = generate_otp()  # Generate a new OTP
    if email:  # Check if email is present in session
        # Save the new OTP and current timestamp in the session
        request.session['otp'] = otp
        request.session['otp_timestamp'] = timezone.now().isoformat()
        send_otp_via_email(email=email, otp=otp)
        messages.success(request, 'Otp Resent Successfully')
    else:
        messages.error(request, 'Error resending the OTP')
    return redirect('otp_page')


def verify_otp(request):
    if request.method == "POST":
        user_otp = request.POST['otp']
        saved_otp = request.session.get('otp')
        otp_timestamp = request.session.get('otp_timestamp')

        # Check if the OTP and timestamp are available
        if saved_otp and otp_timestamp:
            timestamp = timezone.datetime.fromisoformat(otp_timestamp)

            # Check if the OTP is valid and hasn't expired
            if str(user_otp) == str(saved_otp) and (timezone.now() - timestamp <= timedelta(minutes=5)):
                signup_data = request.session.get('signup_data')

                if signup_data:
                    my_user = CustomUser.objects.create_user(
                        email=signup_data['email'],
                        password=signup_data['password'],  # Use the stored password
                        first_name=signup_data['FirstName'],
                        last_name=signup_data['LastName'],
                    )
                    my_user.save()
                    loguser = authenticate(email=signup_data['email'], password=signup_data['password'])
                    login(request, loguser)
                    del request.session['signup_data']
                    messages.success(request, 'Your account has been created successfully!')
                else:
                    loguser = authenticate(email=request.session['email'], password=request.session['password'])
                    if loguser and loguser.is_active:
                        login(request, loguser)
                        messages.success(request, 'Login Successful')
                    else:
                        messages.error(request, 'User Blocked By Admins')
                
                # Clean up session data
                del request.session['otp']
                del request.session['password']
                del request.session['email']
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


def user_logout(request):
    logout(request)
    return redirect('user_home')


def view_product(request, id):
    product = Product.objects.get(id=id)
    return render(request, 'user_product.html', {'product': product})