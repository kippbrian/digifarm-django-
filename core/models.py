from django.db import models
from django.conf import settings
from django.shortcuts import reverse
from django_countries.fields import CountryField
# choices for products.
CATEGORY_CHOICES = (
    ('AP', 'animal'),
    ('PP', 'plant product'),

)


# start of the product model
class Product(models.Model):
    img = models.ImageField()
    title = models.CharField(max_length=100)
    category = models.CharField(CATEGORY_CHOICES, max_length=2)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    description = models.TextField()
    slug = models.SlugField()

    def _str_(self):
        return self.title

    def get_absolute_url(self):
        return reverse('core:productdetail', kwargs={'slug': self.slug})

    def get_add_to_cart_url(self):
        return reverse('core:add-to-cart', kwargs={'slug': self.slug})

    def remove_from_cart_url(self):
        return reverse('core:remove-from-cart', kwargs={'slug': self.slug})
# end of the product  model

# start of service model


class Service(models.Model):
    image = models.ImageField()
    name = models.CharField(max_length=100)
    service = models.CharField(max_length=100)
    rate = models.FloatField()


# start of the order product model
class OrderProduct(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def _str_(self):
        return f"{self.quantity}of{self.product.title}"

    def get_total_product_price(self):
        return self.quantity*self.product.price

    def get_total_discount_price(self):
        return self.quantity*self.product.discount_price

    def get_ammount_saved(self):
        return self.get_total_product_price() - self.get_total_discount_price()

    def get_final_price(self):
        if self.product.discount_price:
            return self.get_total_discount_price()
        return self.get_total_product_price()

# end of the order product model


# end of the order  model
class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    products = models.ManyToManyField(OrderProduct)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    billing_address = models.ForeignKey(
        "BillingAddress", on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(
        "Payment", on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True
    )

    def _str_(self):
        return self.user.username

    def get_total(self):
        total = 0
        for orderproduct in self.products.all():
            total += orderproduct.get_final_price()
        return total


# end of the order  model
class BillingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    house_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=50)

    def _str_(self):
        return self.user.username


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    ammount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return self.user.username


class Coupon(models.Model):
    code = models.CharField(max_length=15)

    def _str_(self):
        return self.code
