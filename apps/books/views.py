from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Book, Category, Author, BookReview
from .forms import BookReviewForm
from apps.transactions.models import BorrowTransaction, Reservation

def book_list(request):
    books = Book.objects.all()
    
    search = request.GET.get('search', '')
    category = request.GET.get('category', '')
    author = request.GET.get('author', '')
    sort = request.GET.get('sort', 'title')
    
    if search:
        books = books.filter(
            Q(title__icontains=search) |
            Q(isbn__icontains=search) |
            Q(authors__name__icontains=search)
        )
    
    if category:
        books = books.filter(category__slug=category)
    
    if author:
        books = books.filter(authors__id=author)
    
    books = books.order_by(sort)
    
    paginator = Paginator(books, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    authors = Author.objects.all()
    
    context = {
        'books': page_obj,
        'categories': categories,
        'authors': authors,
        'search': search,
        'selected_category': category,
        'selected_author': author,
        'sort': sort,
    }
    return render(request, 'books/book_list.html', context)

def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    reviews = book.reviews.all()
    is_borrowed = False
    is_reserved = False
    
    if request.user.is_authenticated:
        is_borrowed = BorrowTransaction.objects.filter(
            user=request.user,
            book=book,
            status__in=['active', 'overdue']
        ).exists()
        
        is_reserved = Reservation.objects.filter(
            user=request.user,
            book=book,
            status='active'
        ).exists()
    
    related_books = Book.objects.filter(
        category=book.category,
        status='available'
    ).exclude(id=book.id)[:6]
    
    context = {
        'book': book,
        'reviews': reviews,
        'is_borrowed': is_borrowed,
        'is_reserved': is_reserved,
        'related_books': related_books,
        'review_form': BookReviewForm() if request.user.is_authenticated else None,
    }
    return render(request, 'books/book_detail.html', context)

@login_required
def borrow_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    
    if not request.user.can_borrow():
        messages.error(request, "You cannot borrow books right now.")
        return redirect('books:book_detail', pk=book.pk)
    
    if not book.is_available():
        messages.error(request, "This book is currently not available.")
        return redirect('books:book_detail', pk=book.pk)
    
    transaction = BorrowTransaction.objects.create(
        user=request.user,
        book=book,
        status='active'
    )
    
    book.borrowed_copies += 1
    book.update_availability()
    request.user.current_books_borrowed += 1
    request.user.save()
    
    messages.success(request, f"Book '{book.title}' borrowed successfully.")
    return redirect('books:book_detail', pk=book.pk)

@login_required
def return_book(request, transaction_id):
    transaction = get_object_or_404(
        BorrowTransaction,
        id=transaction_id,
        user=request.user
    )
    
    if transaction.status in ['returned', 'rejected']:
        messages.error(request, "This transaction cannot be returned.")
        return redirect('core:dashboard')
    
    transaction.return_book()
    
    if transaction.fine_amount > 0:
        messages.warning(request, f"Book returned with a fine of PKR {transaction.fine_amount}. Please pay the fine.")
    else:
        messages.success(request, f"Book '{transaction.book.title}' returned successfully.")
    
    return redirect('core:dashboard')

@login_required
def reserve_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    
    if Reservation.objects.filter(user=request.user, book=book, status='active').exists():
        messages.warning(request, "You have already reserved this book.")
        return redirect('books:book_detail', pk=book.pk)
    
    if not book.is_available() and book.available_copies == 0:
        messages.error(request, "This book cannot be reserved right now.")
        return redirect('books:book_detail', pk=book.pk)
    
    Reservation.objects.create(
        user=request.user,
        book=book
    )
    
    book.reserved_copies += 1
    book.update_availability()
    
    messages.success(request, f"Book '{book.title}' reserved successfully.")
    return redirect('books:book_detail', pk=book.pk)

@login_required
def add_review(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    
    if request.method == 'POST':
        form = BookReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.book = book
            review.user = request.user
            review.save()
            messages.success(request, "Review added successfully.")
        else:
            messages.error(request, "Failed to add review.")
    
    return redirect('books:book_detail', pk=book.pk)