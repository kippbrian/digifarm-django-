from django import forms
from django_countries.fields import CountryField

PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('p', 'Paypal'),
    ('M', 'Mpesa')
)


class CheckoutForm(forms.Form):
    street_address = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': '1234Main St'}))
    house_address = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'placeholder': 'Apartment or suite'}))
    country = CountryField(blank_label='(Select your country)').formfield(attrs={
        'class': 'custom-select d-block w-100'
    })
    zip = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    same_shipping_address = forms.BooleanField(
        widget=forms.CheckboxInput(), required=False)
    save_info = forms.BooleanField(
        widget=forms.CheckboxInput(), required=False)
    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_CHOICES)
