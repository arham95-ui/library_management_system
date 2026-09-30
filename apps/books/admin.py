from django.contrib import admin
from .models import Category, Author, Publisher, Book, BookReview
from import_export.admin import ImportExportModelAdmin

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'get_book_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'nationality', 'get_book_count')
    search_fields = ('name',)

@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email')
    search_fields = ('name',)

@admin.register(Book)
class BookAdmin(ImportExportModelAdmin):
    list_display = ('title', 'isbn', 'status', 'available_copies', 'total_copies', 'rating')
    list_filter = ('status', 'category', 'language', 'is_featured')
    search_fields = ('title', 'isbn', 'authors__name')
    filter_horizontal = ('authors',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(BookReview)
class BookReviewAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('book__title', 'user__username')