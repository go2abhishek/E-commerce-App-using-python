from django.shortcuts import render
from .models import *
from django.http import JsonResponse
import json
import datetime
from .utils import cookieCart, cartData

# Create your views here.

def store(request):
    products = Product.objects.all()
    cartData_ = cartData(request)
    context = {'products':products, 'cartItems':cartData_['cartItems'], 'shipping':False}
    return render(request, 'store/store.html', context)

def cart(request):
    cartData_ = cartData(request)
    context = {'items':cartData_['items'], 'order':cartData_['order'], 'cartItems':cartData_['cartItems'], 'shipping':False}
    return render(request, 'store/cart.html', context)

def checkout(request):
    cartData_ = cartData(request)
    context = {'items':cartData_['items'], 'order':cartData_['order'], 'cartItems':cartData_['cartItems'], 'shipping':False}
    return render(request, 'store/checkout.html', context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print('action :', action)
    print('productId :', productId)
    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
    if action == 'add':
        orderItem.quantity = (orderItem.quantity+1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity-1)
    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was updated', safe=False)

def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        total = round(data['form']['total'], 2)
        order.transaction_id = transaction_id

        print('form total', total)
        print('actual total', round(order.get_cart_total, 2))
        if total == round(order.get_cart_total, 2):
            print('completing order', order.transaction_id)
            order.complete = True
        order.save()

        if order.shipping == True:
            ShippingAddress.objects.create(
                customer = customer,
                order = order,
                address = data['shipping']['address'],
                city = data['shipping']['city'],
                state = data['shipping']['state'],
                zipcode = data['shipping']['zipcode']
            )
    else:
        print('User is not logged in....')
    return JsonResponse('Payment complete', safe=False)