from django import forms
from .models import BookReview

class BookReviewForm(forms.ModelForm):
    class Meta:
        model = BookReview
        fields = ('rating', 'comment')
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your review here...'}),
            'rating': forms.Select(choices=[(i, f'{i} ★') for i in range(1, 6)]),
        }