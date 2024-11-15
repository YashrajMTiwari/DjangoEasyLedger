from django.shortcuts import render, get_object_or_404, redirect
from .models import Customer, Product, Purchase
from .forms import CustomerForm, ProductForm, PurchaseForm
from django.contrib.auth.decorators import login_required
from datetime import date
from django.db.models import Sum
from django.utils import timezone
from django.db.models.functions import TruncMonth, TruncYear
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login
from django.core.mail import send_mail
from django.conf import settings


def home(request):
    return render(request, 'app/landingpage.html')


# List all customers
@login_required
def customer_list(request):
    customers = Customer.objects.filter(shop_owner=request.user)
    return render(request, 'app/customer_list.html', {'customers': customers})


# Create a new customer
@login_required
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.shop_owner = request.user  # Assign the logged-in user as the shop owner
            customer.save()
            return redirect('customer_list')
    else:
        form = CustomerForm()
    return render(request, 'app/customer_form.html', {'form': form})


# Update an existing customer
@login_required
def customer_update(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if customer.shop_owner != request.user:
        return redirect('customer_list')

    form = CustomerForm(request.POST or None, instance=customer)
    if form.is_valid():
        form.save()
        return redirect('customer_list')
    return render(request, 'app/customer_form.html', {'form': form})


# Delete a customer
@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if customer.shop_owner != request.user:
        return redirect('customer_list')
    
    if request.method == 'POST':
        customer.delete()
        return redirect('customer_list')
    return render(request, 'app/customer_confirm_delete.html', {'customer': customer})


# Add Product View
@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request=request)  # Pass request to form
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(request=request)  # Pass request to form

    return render(request, 'app/product_form.html', {'form': form})


# List Products View
@login_required
def product_list(request):
    products = Product.objects.filter(shop_owner=request.user)  # Only show products for the logged-in user
    return render(request, 'app/product_list.html', {'products': products})


# Remove Product View
@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if product.shop_owner != request.user:
        return redirect('product_list')
    
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'app/product_confirm_delete.html', {'product': product})

@login_required
def purchase_create(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    if request.method == 'POST':
        form = PurchaseForm(request.POST, user=request.user)
        
        if form.is_valid():
            product = form.cleaned_data['product']
            quantity = form.cleaned_data['quantity']
            total_amount = form.cleaned_data['total_amount']  # Calculated in form, not shown on page
            payment_status = form.cleaned_data['payment_status']

            # Save the purchase
            purchase = Purchase(
                customer=customer,
                product=product,
                quantity=quantity,
                total_amount=total_amount,
                payment_status=payment_status
            )
            purchase.save()
            return redirect('customer_detail', pk=customer.id)
    
    else:
        form = PurchaseForm(user=request.user)
    
    return render(request, 'app/purchase_form.html', {'form': form, 'customer': customer})

@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    purchases = Purchase.objects.filter(customer=customer)
    return render(request, 'app/customer_detail.html', {'customer': customer, 'purchases': purchases})


# Remove Purchase View
@login_required
def purchase_delete(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)
    if purchase.customer.shop_owner != request.user:
        return redirect('customer_detail', pk=purchase.customer.id)
    
    if request.method == 'POST':
        purchase.delete()
        return redirect('customer_detail', pk=purchase.customer.id)
    return render(request, 'app/purchase_confirm_delete.html', {'purchase': purchase})


# Update Product View
@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if product.shop_owner != request.user:
        return redirect('product_list')

    form = ProductForm(request.POST or None, instance=product)
    if form.is_valid():
        form.save()
        return redirect('product_list')

    return render(request, 'app/product_form.html', {'form': form, 'product': product})


# Dashboard View
@login_required
def dashboard(request):
    customer_count = Customer.objects.filter(shop_owner=request.user).count()
    today = date.today()

    period = request.GET.get('period', 'daily')  # default to 'daily' if not specified

    if period == 'daily':
        sales = Purchase.objects.filter(purchase_date=today, product__shop_owner=request.user)
        total_sales = sales.aggregate(total_sales=Sum('total_amount'))['total_sales'] or 0
    elif period == 'monthly':
        sales = Purchase.objects.filter(purchase_date__month=today.month, purchase_date__year=today.year, product__shop_owner=request.user)
        total_sales = sales.aggregate(total_sales=Sum('total_amount'))['total_sales'] or 0
    elif period == 'yearly':
        sales = Purchase.objects.filter(purchase_date__year=today.year, product__shop_owner=request.user)
        total_sales = sales.aggregate(total_sales=Sum('total_amount'))['total_sales'] or 0
    else:
        total_sales = 0
        sales = Purchase.objects.none()

    paid_sales_count = sales.filter(payment_status=True).count()
    unpaid_sales_count = sales.filter(payment_status=False).count()

    return render(request, 'app/dashboard.html', {
        'customer_count': customer_count,
        'total_sales': total_sales,
        'paid_sales_count': paid_sales_count,
        'unpaid_sales_count': unpaid_sales_count,
        'period': period,
        'sales': sales,
    })


# Register View
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'app/register.html', {'form': form})


def custom_login(request):
    return render(request, 'login.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'login.html')

# Email Remainder

def get_customers_with_pending_payments():
    pending_payments = Purchase.objects.filter(status='pending', due_date__lte=timezone.now())
    customers = [payment.customer for payment in pending_payments]
    return customers

def send_payment_reminder(customer):
    subject = 'Reminder: Pending Payment for Your Account'
    message = f"""
    Dear {customer.name},
    
    We are writing to remind you that you have a pending payment of {customer.amount_due} for your recent purchase with EasyLedger.
    
    Payment details:
    - Amount Due: {customer.amount_due}
    - Due Date: {customer.payment_due_date}
    
    Please make sure to complete your payment before the due date to avoid any late fees or service disruptions.

    If you have any questions, feel free to contact us.

    Best regards,
    The EasyLedger Team
    """

    # Send the email
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [customer.email],
        fail_silently=False,
    )

