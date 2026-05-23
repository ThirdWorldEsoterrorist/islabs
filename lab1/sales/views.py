from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from .models import *
from .forms import *
from decimal import Decimal
from django.db import transaction
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.contrib import messages
def homepage(request):
    return render(request, 'home.html')

def client_base(request):
    clients = Client.objects.all()
    return render(request, 'client_base.html', {"clients": clients})

def client_search(request):
    clients = Client.objects.all()
    search_res = clients.none()

    if request.method == "POST":
        form = ClientSearchForm(request.POST)
        if form.is_valid():
            search_name = form.cleaned_data.get('search')
            search_res = clients.filter(name__icontains=search_name)
    else:
        form = ClientSearchForm()
    return render(request, 'client_search.html', {"form" :  form, "clients" : search_res})

def product_base(request):
    products = Product.objects.all()
    return render(request, 'product_base.html', {"products": products})

"""
def create_database(request):
    if request.method == "POST":
        form = ClientAddForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = ClientAddForm()
    return render(request, 'product_add.html', {"form" : form})
"""

def product_add(request):
    products = Product.objects.all()

    if request.method == "POST":
        form = ProductAddForm(request.POST)
        form.price_error = ""
        form.stock_error = ""

        if form.is_valid():
            name = form.cleaned_data.get('name')
            price = Decimal(form.cleaned_data.get('price'))
            stock = int(form.cleaned_data.get('stock'))
            try:
                get_name = products.get(name=name)
                price = get_name.price
                stock += get_name.stock
            except ObjectDoesNotExist:
                price = Decimal(form.cleaned_data.get('price'))

            if stock == 0:
                form.stock_error = "Указана недопустимое количество товара"
            if not form.stock_error:
                if price <= 0:
                    form.price_error = "Указана недопустимая цена"
                else:
                    obj, created = Product.objects.update_or_create(
                        name=name,
                        defaults={'price': price, 'stock': stock} #defaults только, не по отдельности!!!
                    )
                    return redirect('product_base')
    else:
        form = ProductAddForm()
    return render(request, 'product_add.html', {"product_add" : product_add, "form" :  form})



def order_create(request):

    if request.method == 'POST':
        form = OrderForm(request.POST)
        error_message = None

        if form.is_valid():
            with transaction.atomic():
                product_id = request.POST.getlist('products[]')
                stock = request.POST.getlist('stocks[]')
                total_sum = 0
                order_items_data = []

                # проверка на соответствие условиям
                client=form.cleaned_data.get('client')
                payment = form.cleaned_data.get('payment')
                for p_id, qty in zip(product_id, stock):
                    if p_id and qty:
                        product = Product.objects.get(id=p_id)
                        quantity = int(qty)
                        if (quantity > product.stock) and (payment != 'return'):
                            error_message = f"Недостаточно товара {product.name} на складе! Текущее количество на складе - {product.stock}"
                        total_sum += product.price * quantity
                        order_items_data.append({'product': product, 'qty': quantity})

                if payment == 'card':
                    if client.a_current < total_sum:
                        error_message = f"Недостаточно средств на счету! Текущий счёт клиента: {client.a_current}"
                if payment == 'credit':
                    if client.credit_remain < total_sum:
                        error_message = f"Недостаточно средств на кредитном счету! Текущий остаток кредита клиента: {client.credit_remain}"
                if payment == 'barter':
                    b_id = request.POST.getlist('barter_products[]')
                    b_qty = request.POST.getlist('barter_stocks[]')
                    barter_sum = 0
                    for b_idi, b_qtyi in zip(b_id, b_qty):
                        if b_idi and b_qtyi:
                            b_product = Product.objects.get(id=b_idi)
                            barter_sum += b_product.price * int(b_qtyi)
                    if total_sum != barter_sum:
                        error_message = f"Ошибка бартера: суммы не равны! Заказ: {total_sum} руб., Обмен: {barter_sum} руб."

                #непосредственно создание заказа
                if error_message:
                    messages.error(request, error_message)
                else:
                    order = Order.objects.create(
                        client=form.cleaned_data.get('client'),
                        payment=form.cleaned_data.get('payment')
                    )

                    for item in order_items_data:
                        current_product = item['product']
                        OrderItem.objects.create(
                            order=order,
                            product=item['product'],
                            quantity=item['qty']
                        )

                        if order.payment == 'return':
                            current_product.stock += item['qty']
                        else:
                            current_product.stock -= item['qty']

                        current_product.save()
                    order.process_payment(total_sum)

                    if order.payment == 'barter':
                        for b_idi, b_qtyi in zip(b_id, b_qty):
                            if b_idi and b_qtyi:
                                b_product = Product.objects.get(id=b_idi)
                                b_product.stock += int(b_qtyi)
                                b_product.save()
    else:
        form = OrderForm()
    products = Product.objects.all()
    clients = Client.objects.all()
    return render(request, 'order_create.html', {"form": form, "products": products, "clients": clients})

def order_base(request):
    orders = Order.objects.all()
    return render(request, 'order_base.html', {"orders": orders})