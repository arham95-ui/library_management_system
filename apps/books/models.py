from django.db import models
from django.utils import timezone
from ckeditor.fields import RichTextField
from django.core.validators import MinValueValidator, MaxValueValidator

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_book_count(self):
        return self.books.filter(is_available=True).count()

class Author(models.Model):
    name = models.CharField(max_length=200)
    biography = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    death_date = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    profile_image = models.ImageField(upload_to='authors/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def get_book_count(self):
        return self.books.count()

class Publisher(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class Book(models.Model):
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('borrowed', 'Borrowed'),
        ('reserved', 'Reserved'),
        ('damaged', 'Damaged'),
        ('lost', 'Lost'),
        ('maintenance', 'Under Maintenance'),
    )
    
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200, blank=True)
    isbn = models.CharField(max_length=20, unique=True)
    authors = models.ManyToManyField(Author, related_name='books')
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True, related_name='books')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='books')
    publication_year = models.IntegerField(validators=[MinValueValidator(1000), MaxValueValidator(9999)])
    edition = models.CharField(max_length=50, blank=True)
    pages = models.IntegerField(default=0)
    language = models.CharField(max_length=50, default='English')
    description = RichTextField(blank=True)
    cover_image = models.ImageField(upload_to='book_covers/', null=True, blank=True)
    
    total_copies = models.IntegerField(default=1)
    available_copies = models.IntegerField(default=1)
    borrowed_copies = models.IntegerField(default=0)
    reserved_copies = models.IntegerField(default=0)
    
    shelf_location = models.CharField(max_length=50, blank=True)
    rack_number = models.CharField(max_length=20, blank=True)
    tags = models.CharField(max_length=200, blank=True)
    rating = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    number_of_reviews = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)
    is_new_arrival = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['title']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['isbn']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.isbn})"
    
    def is_available(self):
        return self.available_copies > 0 and self.status == 'available'
    
    def update_availability(self):
        self.available_copies = self.total_copies - self.borrowed_copies - self.reserved_copies
        if self.available_copies > 0:
            self.status = 'available'
        elif self.borrowed_copies > 0:
            self.status = 'borrowed'
        elif self.reserved_copies > 0:
            self.status = 'reserved'
        else:
            self.status = 'damaged'
        self.save()

class BookReview(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['book', 'user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.book.title} - {self.rating}★"