from django.db import models
from django.utils import timezone
from decimal import Decimal

class BorrowTransaction(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('active', 'Active'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
        ('rejected', 'Rejected'),
    )
    
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='borrow_transactions')
    book = models.ForeignKey('books.Book', on_delete=models.CASCADE, related_name='borrow_transactions')
    borrow_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fine_paid = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-borrow_date']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['due_date']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.book.title} ({self.status})"
    
    def is_overdue(self):
        if self.status in ['returned', 'rejected']:
            return False
        return timezone.now() > self.due_date
    
    def calculate_fine(self):
        if not self.is_overdue():
            return Decimal('0')
        days_overdue = (timezone.now() - self.due_date).days
        fine_per_day = Decimal('50')
        return days_overdue * fine_per_day
    
    def return_book(self):
        self.return_date = timezone.now()
        self.status = 'returned'
        if self.is_overdue():
            self.fine_amount = self.calculate_fine()
        self.book.borrowed_copies -= 1
        self.book.update_availability()
        self.user.current_books_borrowed -= 1
        self.user.save()
        self.save()

class Reservation(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('fulfilled', 'Fulfilled'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    )
    
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='reservations')
    book = models.ForeignKey('books.Book', on_delete=models.CASCADE, related_name='reservations')
    reservation_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    notified = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-reservation_date']
        unique_together = ['user', 'book', 'status']
    
    def __str__(self):
        return f"{self.user.username} - {self.book.title}"

class FinePayment(models.Model):
    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='fine_payments')
    transaction = models.ForeignKey(BorrowTransaction, on_delete=models.CASCADE, related_name='fine_payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    receipt_number = models.CharField(max_length=50, unique=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.receipt_number:
            import uuid
            self.receipt_number = f"FINE-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)