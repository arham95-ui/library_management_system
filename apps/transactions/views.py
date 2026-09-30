from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import BorrowTransaction, FinePayment

@login_required
def transaction_list(request):
    transactions = BorrowTransaction.objects.filter(user=request.user).order_by('-borrow_date')
    return render(request, 'transactions/transaction_list.html', {'transactions': transactions})

@login_required
def pay_fine(request, transaction_id):
    transaction = get_object_or_404(BorrowTransaction, id=transaction_id, user=request.user)
    
    if transaction.fine_amount <= 0:
        messages.error(request, "No fine to pay for this transaction.")
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        payment = FinePayment.objects.create(
            user=request.user,
            transaction=transaction,
            amount=transaction.fine_amount,
            status='completed'
        )
        transaction.fine_paid = True
        transaction.save()
        request.user.fine_amount -= transaction.fine_amount
        request.user.save()
        
        messages.success(request, f"Fine of PKR {transaction.fine_amount} paid successfully.")
        return redirect('core:dashboard')
    
    return render(request, 'transactions/pay_fine.html', {'transaction': transaction})