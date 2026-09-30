from django.contrib import admin
from .models import BorrowTransaction, Reservation, FinePayment

@admin.register(BorrowTransaction)
class BorrowTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'borrow_date', 'due_date', 'status', 'fine_amount')
    list_filter = ('status', 'borrow_date')
    search_fields = ('user__username', 'book__title')
    readonly_fields = ('borrow_date', 'created_at', 'updated_at')

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'reservation_date', 'expiry_date', 'status')
    list_filter = ('status', 'reservation_date')
    search_fields = ('user__username', 'book__title')

@admin.register(FinePayment)
class FinePaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'payment_date', 'status', 'receipt_number')
    list_filter = ('status', 'payment_date')
    search_fields = ('user__username', 'receipt_number')