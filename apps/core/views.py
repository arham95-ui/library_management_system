from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone
from apps.books.models import Book, Category
from apps.transactions.models import BorrowTransaction, Reservation
from apps.accounts.models import CustomUser, UserActivityLog
from django.http import JsonResponse

def home(request):
    featured_books = Book.objects.filter(is_featured=True, status='available')[:8]
    new_arrivals = Book.objects.filter(is_new_arrival=True, status='available')[:8]
    categories = Category.objects.annotate(book_count=Count('books'))
    
    context = {
        'featured_books': featured_books,
        'new_arrivals': new_arrivals,
        'categories': categories,
    }
    return render(request, 'core/home.html', context)

@login_required
def dashboard(request):
    user = request.user
    today = timezone.now()
    
    total_books = Book.objects.count()
    available_books = Book.objects.filter(status='available').count()
    
    borrowed_books = BorrowTransaction.objects.filter(
        user=user,
        status__in=['active', 'overdue']
    )
    overdue_books = borrowed_books.filter(due_date__lt=today)
    reservations = Reservation.objects.filter(user=user, status='active')
    recent_transactions = BorrowTransaction.objects.filter(user=user)[:10]
    total_fine = user.fine_amount
    
    context = {
        'total_books': total_books,
        'available_books': available_books,
        'borrowed_books': borrowed_books,
        'overdue_books': overdue_books,
        'reservations': reservations,
        'recent_transactions': recent_transactions,
        'total_fine': total_fine,
        'borrowed_count': borrowed_books.count(),
    }
    return render(request, 'core/dashboard.html', context)

@login_required
@user_passes_test(lambda u: u.user_type in ['admin', 'librarian'])
def admin_dashboard(request):
    total_users = CustomUser.objects.count()
    total_books = Book.objects.count()
    total_transactions = BorrowTransaction.objects.count()
    active_borrowings = BorrowTransaction.objects.filter(status='active').count()
    overdue_borrowings = BorrowTransaction.objects.filter(status='overdue').count()
    total_fines = BorrowTransaction.objects.aggregate(total=Sum('fine_amount'))['total'] or 0
    
    recent_activities = UserActivityLog.objects.all()[:20]
    
    current_month = timezone.now().month
    current_year = timezone.now().year
    
    monthly_stats = {
        'borrowed': BorrowTransaction.objects.filter(
            borrow_date__month=current_month,
            borrow_date__year=current_year
        ).count(),
        'returned': BorrowTransaction.objects.filter(
            return_date__month=current_month,
            return_date__year=current_year
        ).count(),
        'new_members': CustomUser.objects.filter(
            membership_date__month=current_month,
            membership_date__year=current_year
        ).count(),
    }
    
    context = {
        'total_users': total_users,
        'total_books': total_books,
        'total_transactions': total_transactions,
        'active_borrowings': active_borrowings,
        'overdue_borrowings': overdue_borrowings,
        'total_fines': total_fines,
        'recent_activities': recent_activities,
        'monthly_stats': monthly_stats,
    }
    return render(request, 'core/admin_dashboard.html', context)

def search(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    
    books = Book.objects.filter(status='available')
    
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(isbn__icontains=query) |
            Q(authors__name__icontains=query) |
            Q(publisher__name__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()
    
    if category:
        books = books.filter(category__slug=category)
    
    categories = Category.objects.all()
    
    context = {
        'books': books,
        'query': query,
        'categories': categories,
        'selected_category': category,
        'total_results': books.count(),
    }
    return render(request, 'core/search_results.html', context)