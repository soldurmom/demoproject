from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404

from django.http import JsonResponse

# Create your views here.
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic import CreateView
from demo.form import RegisterUserForm
from demo.models import User, Order, Product, ProductsInCart, ProductsInOrder, Category


class RegisterView(CreateView):
    template_name = 'registration/register.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('login')


def validate(request):
    fieldname = request.GET.get('name')
    response = {'is_taken': True};

    if fieldname == 'username':
        response.update({'is_taken': User.objects.filter(username__iexact=request.GET.get('value')).exists()})

    if fieldname == 'email':
        response.update({'is_taken': User.objects.filter(email__iexact=request.GET.get('value')).exists()})

    return JsonResponse(response)


def about(request):
    products = Product.objects.filter(count__gte=1).order_by('datetime')[:5]
    return render(request, 'demo/about.html', context={'products': products})


def catalog(request):
    category = request.GET.get('category')

    if category:
        products = Product.objects.filter(count__gte=1, category=category)
    else:
        products = Product.objects.filter(count__gte=1)

    order_by = request.GET.get('order_by')
    if order_by:
        products = products.order_by(order_by)
    else:
        products = products.order_by('datetime')

    return render(request, 'demo/catalog.html', context={'category': Category.objects.all(), 'products': products})


def product(request, pk):
    product_ = get_object_or_404(Product, pk=pk)
    return render(request, 'demo/product.html', context={'product': product_})


def contact(request):
    return render(request, 'demo/contact.html')


@login_required
def cart(request):
    cart_items = request.user.productsincart_set.all()

    return render(request, 'demo/cart.html', context={'cart_items': cart_items})


@login_required
def checkout(request):
    password = request.GET.get('password')
    valid = request.user.check_password(password)
    if not valid:
        return JsonResponse({'error': 'Неверный пароль'})
    items_in_cart = request.user.productsincart_set.all()
    if not items_in_cart:
        return JsonResponse({'error': 'Корзина пуста'})

    order_ = Order.objects.create(user=request.user)
    for item in items_in_cart:
        ProductsInOrder.objects.create(order=order_, product=item.product,
                                       count=item.count, price=item.count * item.product.price)
    items_in_cart.delete()
    return JsonResponse({'message': 'Заказ оформлен'})


class OrderListView(LoginRequiredMixin, generic.ListView):
    model = Order
    template_name = 'demo/orders.html'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('date')


@login_required
def delete_order(request, pk):
    order = Order.objects.filter(user=request.user, pk=pk, status='new')
    if order:
        order.delete()
    return redirect('orders')


@login_required
def to_cart(request, pk):
    product_ = get_object_or_404(Product, pk=pk)
    item_in_cart = ProductsInCart.objects.filter(user=request.user, product=product_).first()

    if item_in_cart:
        if item_in_cart.count + 1 > item_in_cart.product.count:
            return JsonResponse({'error': 'Can\'t add more'})
        item_in_cart.count += 1
        item_in_cart.save()
        return JsonResponse({'count': item_in_cart.count})

    item_in_cart = ProductsInCart(user=request.user, product=product_, count=1)
    item_in_cart.save()

    return JsonResponse({'count': item_in_cart.count})


@login_required
def rem_cart(request, pk):
    product_ = get_object_or_404(Product, pk=pk)
    item_in_cart = ProductsInCart.objects.filter(user=request.user, product=product_).first()

    if item_in_cart:
        item_in_cart.count -= 1
        if item_in_cart.count <= 0:
            item_in_cart.delete()
        else:
            item_in_cart.save()

        return JsonResponse({'count': item_in_cart.count})
    else:
        item_in_cart.count = 0

    return JsonResponse({'count': item_in_cart.count})
