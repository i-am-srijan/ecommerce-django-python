from django.shortcuts import render, redirect
from store.models import Product, Variation
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.

from django.http import HttpResponse
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):# 🔍 Retrieve the product based on the given product_id
    product = Product.objects.get(id=product_id) #this get product
    product_variation = []
    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST[key]
            # print(key, value)
            try:
                variation = Variation.objects.get(product = product , variation_category__iexact=key, variation_value__iexact=value)
                #__iexact ignore capital letter or small 
                print(variation)
                product_variation.append(variation)
            except:
                pass
    
    try:  # 🛒 Try to get the cart associated with the current session
        cart = Cart.objects.get(cart_id = _cart_id(request)) #get the cart using the cart_id present in the session
    except Cart.DoesNotExist:
        # 🚀 If no cart exists, create a new  one using the session's cart_id
        cart =Cart.objects.create(
                cart_id = _cart_id(request)     
        )
        cart.save()
    is_cart_item_exists = CartItem.objects.filter(product = product, cart = cart).exists()

    if is_cart_item_exists:
        # 📦 Try to get the cart item for the product in the cart
        cart_item = CartItem.objects.filter(product = product, cart=cart)
        #existing_variation _ from database
        #current variation from product_variation
        #item_id from database
        ex_var_list =[]
        id = []
        for item in cart_item:
            existing_variation = item.variation.all()
            ex_var_list.append(list(existing_variation))
            id.append(item.id)
        print(ex_var_list)

        if product_variation in ex_var_list:
            #increase the cart item quantity
            index = ex_var_list.index(product_variation)
            item_id = id[index]
            item = CartItem.objects.get(product=product, id=item_id)
            item.quantity +=1
            item.save()

        else:
            item = CartItem.objects.create(product=product, quantity =1, cart=cart)

            if len(product_variation) > 0:
                item.variation.clear()
                item.variation.add(*product_variation)
            item.save()


    else:
        # 🆕 If the item doesn't exist in the cart, create it with quantity 1
        cart_item = CartItem.objects.create(
            product = product,
            quantity = 1,
            cart= cart,
        )
        if len(product_variation)>0:
            cart_item.variation.clear()
            cart_item.variation.add(*product_variation)
        cart_item.save()
        print(f"CartItem Variation after add: {[str(v) for v in cart_item.variation.all()]}")

    # return HttpResponse(cart_item.quantity  )
    # exit()
    # 🔄 After adding, redirect the user to the cart page
    return redirect('cart')

def remove_cart(request, product_id, cart_item_id):
    product = Product.objects.get(id=product_id)
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart , id = cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except (Cart.DoesNotExist, CartItem.DoesNotExist):
        pass

    return redirect('cart')

# def remove_cart_item(request, product_id):
#     cart = Cart.objects.get(cart_id=_card_id(request))
#     product = get_object_or_404(Product, id= product_id)
#     cart_item = CartItem.objects.get(product=product, cart=cart)
#     cart_item.delete()
#     return redirect('cart')

def remove_cart_item(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))  # use your session cart ID
    product = Product.objects.get(id=product_id)
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart , id= cart_item_id)
        if cart_item.quantity >1:
            cart_item.quantity -=1
            cart_item.save()
        else:
            cart_item.delete()
            
    except (Cart.DoesNotExist, CartItem.DoesNotExist):
        pass  # If no cart or cart item, just ignore

    return redirect('cart')

def cart(request, total=0, quantity = 0, cart_items= None):
    try:
        cart = Cart.objects.get(cart_id = _cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass
    context={
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total':  grand_total,
    }
    return render(request, 'store/cart.html', context)