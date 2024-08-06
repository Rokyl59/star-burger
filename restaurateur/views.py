from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from geopy import distance

from foodcartapp.models import Product, Restaurant, Order, RestaurantMenuItem
from address.models import Address


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability for item in product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False) for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    items = RestaurantMenuItem.objects.all()
    products_vs_rests = items.values('product', 'restaurant__name')
    restaurants = list(Restaurant.objects.all())

    orders = Order.objects.with_price().exclude(status='04_completed')\
        .order_by('status')
    addresses = []
    for order in orders:
        addresses.append(order.address)
    orders_addresses = Address.objects.filter(address__in=addresses)

    for order in orders:
        for element in order.elements.all():
            available_in = list(filter(
                lambda d: d['product'] == element.product.id, products_vs_rests
            ))
            element.available_in = [d['restaurant__name'] for d in available_in]

        order_available_in = set.intersection(
            *map(set, [elem.available_in for elem in order.elements.all()])
        )

        order_address = orders_addresses.get(address=order.address)
        order_coord = (order_address.latitude, order_address.longitude)

        restaurants_with_distances = []
        for restaurant in restaurants:
            if restaurant.name in order_available_in:
                restaurant_coord = (restaurant.latitude, restaurant.longitude)
                restaurants_with_distances.append(
                    (restaurant.name, distance.distance(
                        order_coord,
                        restaurant_coord,
                    ).km),
                )

        restaurants_with_distances.sort(key=lambda dist: dist[1])
        text = '{} - {:.2f} км'
        order.available_in = [
            text.format(rest[0], rest[1]) for rest in restaurants_with_distances
        ]

    context = {'orders': orders}
    return render(request, template_name='order_items.html', context=context)