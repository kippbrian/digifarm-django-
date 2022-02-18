from django.conf import settings
from django.shortcuts import render
from django.views.generic import ListView, DetailView, View
from .models import Product, OrderProduct, Order, BillingAddress, Payment, Coupon, Service
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from .forms import CheckoutForm
import stripe
# Create your views here.
stripe.api_key = settings.STRIPE_SECRET_KEY


def index(request):
    return render(request, 'index.html')


class ProductHomeView(ListView):
    model = Product
    paginate_by = 10
    template_name = 'producthome.html'


def services(request):
    context = Service.objects.all()
    return render(request, 'services.html', {'context': context})


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'ordersummary.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, 'you do not have an active order')
            return redirect('/')


class ProductDetailView(DetailView):
    model = Product
    template_name = 'productdetail.html'


class checkoutView(View):
    def get(self, *args, **kwargs):
        form = CheckoutForm()
        context = {
            'form': form
        }
        return render(self.request, 'checkout.html', context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                house_address = form.cleaned_data.get('house_address')
                country = form.cleaned_data.get('country')
                zip = form.cleaned_data.get('zip')
                # to do-add functionality to the buttons
                # same_shipping_address = form.cleaned_data.get(
                #    'same_shipping_address')
                #save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')
                billing_address = BillingAddress(
                    user=self.request.user,
                    street_address=street_address,
                    house_address=house_address,
                    country=country,
                    zip=zip
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()
                # add redirect to the selected payment option
                if payment_option == 'S':
                    return redirect('core:payment', payment_option='stripe')
                elif payment_option == 'P':
                    return redirect('core:payment', payment_option='paypal')
                elif payment_option == 'M':
                    return redirect('core:payment', payment_option='Mpesa')
                else:
                    message.warning(self.request, 'failed to checkout')
                    return redirect('core:checkout')

        except ObjectDoesNotExist:
            messages.error(self.request, 'you do not have an active order')
            return redirect('core:ordersummary')


class PaymentView(View):
    def get(self, *args, **kwargs):
        # order
        order = Order.objects.get(user=self.request.user, ordered=False)
        context = {
            'order': order
        }
        return render(self.request, 'payment.html', context)

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        ammount = int(order.get_total()*100),  # payment made in cents
        try:
            token = self.request.POST.get('stripeToken')
            stripe.Charge.create(

                currency='ksh',
                source=token,  # obtained with stripe.js
            )
            order.ordered = True

            # create the payment.
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.ammount = order.get_total()
            payment.save()
            # assign the payment to the user

            order_products = order.products.all()
            order_products.update(ordered=True)
            for Product in order_products:
                product.save

            order.ordered = True
            order.payment = payment
            order.save()

            messages.success(
                self.request, 'your order was succersful check your email')
            return redirect('/')
        except stripe.error.CardError as e:
            body = e.json_body
            err = body.get('error', {})
            messages.error(self.request, f"{err.get('message')}")
            return redirect('/')

        # add all the other error handlers using stripe.


# make sure you are logged in to acces adding to cart
@login_required
def add_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    order_product, created = OrderProduct.objects.get_or_create(
        product=product,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is the order
        if order.products.filter(product__slug=product.slug).exists():
            order_product.quantity += 1
            order_product.save()
            messages.info(request, 'product quantity updated to cart')
            return redirect('core:productdetail', slug=slug)
        else:
            order.products.add(order_product)
            messages.info(request, 'product added to cart')
            return redirect('core:productdetail', slug=slug)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.products.add(order_product)
        messages.info(request, 'product added to cart')
    return redirect('core:productdetail', slug=slug)


# start of removing from cart
@login_required
def remove_from_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if product is in the order
        if order.products.filter(product__slug=product.slug).exists():
            order_product = OrderProduct.objects.filter(
                product=product, user=request.user, ordered=False)[0]
            order.products.remove(order_product)
            messages.info(request, 'item removed from cart')
            return redirect('core:productdetail', slug=slug)
        else:
            messages.info(request, 'product was not in your cart')
            return redirect('core:productdetail', slug=slug)
    else:
        messages.info(request, 'you do not have an active order')
        return redirect(request, 'core:productdetail', slug=slug)


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
    except ObjectDoesNotExist:
        message.info(request, 'coupon code does not exist')
        return redirect('core:checkout')


def add_coupon(request, code):
    try:
        order = Order.objects.get(user=request.user, ordered=False)
        order.coupon = get_coupon(request, code)
        order.save()
        messages.success(request, 'coupon added succesfully')
        return redirect('core:checkout')

    except ObjectDoesNotExist:
        messages.info(request, 'you do not have an active order')
        return redirect('core:checkout')


def ihub(request):
    return render(request)
