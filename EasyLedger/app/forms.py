from django import forms
from .models import Customer, Product, Purchase

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone', 'address']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'description']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if self.request:
            instance.shop_owner = self.request.user
        
        if commit:
            instance.save()
        return instance




class PurchaseForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.none(), required=True)
    quantity = forms.IntegerField(min_value=1, required=True)
    payment_status = forms.BooleanField(required=False, label="Payment Completed")  

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None) 
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['product'].queryset = Product.objects.filter(shop_owner=user)

    def clean(self):
        cleaned_data = super().clean()

        product = cleaned_data.get('product')
        quantity = cleaned_data.get('quantity')

        if not product:
            self.add_error('product', 'Please select a product.')
        if quantity is None or quantity <= 0:
            self.add_error('quantity', 'Please enter a valid quantity.')

        if product and quantity:
            total_amount = product.price * quantity
            cleaned_data['total_amount'] = total_amount  

        return cleaned_data
