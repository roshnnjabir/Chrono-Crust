from django.shortcuts import render, redirect
from user.models import CustomUser
from .models import Product, Brand, Collection
from django.contrib.auth import logout, login, authenticate
from django.db.models import Q, Count
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.cache import never_cache
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import imghdr
from django.shortcuts import render, get_object_or_404


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


def admin_show_user_details(request, id):
    user = get_object_or_404(CustomUser, id=id)
    addresses = user.addresses.all()
    context = {
        'user': user,
        'addresses': addresses,
    }
    return render(request, 'admin_show_user_details.html', context)


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



def admin_add_product(request):
    if request.method == "POST":
        productname = request.POST['productname']
        price = request.POST['price']
        collect = request.POST['collection']
        stock = request.POST['stock']
        print(request.POST['collection'], 'hrh')
        image1 = request.POST['image1']
        image2 = request.POST['image2']
        image3 = request.POST['image3']
        
        collection = Collection.objects.get(id=collect)
        Product.objects.create(name=productname, price=price, collection=collection, stock=stock, image=image1, image1=image2, image2= image3)
        return redirect('admin_list_product')
    collection = Collection.objects.all()
    return render(request, 'admin_add_product.html', {'collections': collection})


def admin_list_unlist_product(request, id):
    product = Product.objects.get(id=id)
    if product.is_listed:
        product.is_listed = False
    else:
        product.is_listed = True
    product.save()
    return redirect('admin_list_product')


def admin_edit_product(request, id):
    if request.method == "POST":
        productid = request.POST['product-id']
        productname = request.POST['productname']
        price = request.POST['price']
        collection_id = request.POST['collection']
        stock = request.POST['stock']
        image1 = request.POST['image1']
        image2 = request.POST['image2']
        image3 = request.POST['image3']

        product = Product.objects.get(id=productid)
        collection = Collection.objects.get(id=collection_id)

        product.name = productname
        product.collection = collection
        product.price = price
        product.stock = stock
        product.image = image1
        product.image1 = image2
        product.image2 = image3
        product.save()
        return redirect('admin_list_product')
    product = Product.objects.get(id=id)
    collections = Collection.objects.all()
    return render(request, 'admin_edit_products.html', {'product': product, 'collections': collections})


def admin_delete_product(request, id):
    product = Product.objects.get(id=id)
    product.delete()
    return redirect('admin_list_product')


def admin_list_collection(request):
    collections = Collection.objects.all()
    return render(request, 'admin_list_collection.html', {'collections': collections})


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


def admin_list_unlist_collection(request, id):
    collection = Collection.objects.get(id=id)
    if collection.is_listed:
        collection.is_listed = False
    else:
        collection.is_listed = True
    collection.save()
    return redirect('admin_list_collection')


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


def admin_delete_collection(request, id):
    collection = Collection.objects.get(id=id)
    collection.delete()
    return redirect('admin_list_collection')


def admin_list_brand(request):
    brand = Brand.objects.all()
    return render(request, 'admin_list_brand.html', {'brands': brand})


def admin_add_brand(request):
    if request.method == "POST":
        brand_name = request.POST['brand']
        if Brand.objects.filter(name=brand_name).exists():
            messages.error(request, f"The Brand '{brand_name}' already exists.")
            return redirect('admin_add_brand')
        Brand.objects.create(name=brand_name)
        return redirect('admin_list_brand')
    brands = Brand.objects.all()
    return render(request, 'admin_add_brand.html', {'brands': brands})


def admin_list_unlist_brand(request, id):
    brand = Brand.objects.get(id=id)
    if brand.is_listed:
        brand.is_listed = False
    else:
        brand.is_listed = True
    brand.save()
    return redirect('admin_list_brand')


def admin_edit_brand(request, id):
    brand = Brand.objects.get(id=id)
    if request.method == "POST":
        brand_name = request.POST['brand']
        if Brand.objects.filter(name=brand_name).exclude(id=id).exists():
            messages.error(request, "Brand name already exists.")
        else:
            brand.name = brand_name
            brand.save()
            return redirect('admin_list_brand')
    return render(request, 'admin_edit_brand.html', {'brand': brand})


def admin_delete_brand(request, id):
    brand = Brand.objects.get(id=id)
    brand.delete()
    return redirect('admin_list_brand')


@csrf_exempt
def upload_cropped_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image_file = request.FILES['image']
        # Save the file to media directory
        file_name = default_storage.save('products/' + image_file.name, image_file)
        file_url = default_storage.url(file_name)
        return JsonResponse({'status': 'success', 'file_url': file_url})
    return JsonResponse({'status': 'error'}, status=400)
