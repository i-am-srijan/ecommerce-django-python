from django.shortcuts import render
from store.models import Product

def home(request):
    products = Product.objects.all().filter(is_available=True) # this help to return all the product in database
    context = {
        'allProducts': products,
    }
    return render(request, 'home.html', context)    