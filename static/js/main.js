// Main JavaScript for Library Management System

$(document).ready(function() {
    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);
    
    // Confirm before actions
    $('.confirm-delete').click(function(e) {
        if (!confirm('Are you sure you want to delete this item?')) {
            e.preventDefault();
        }
    });
    
    // Book search with live preview
    $('#book-search').on('input', function() {
        var query = $(this).val();
        if (query.length >= 2) {
            // Perform AJAX search
            $.ajax({
                url: '/search/',
                data: { q: query },
                success: function(data) {
                    $('#search-results').html(data);
                }
            });
        }
    });
    
    // Toggle password visibility
    $('.toggle-password').click(function() {
        var input = $(this).closest('.input-group').find('input');
        if (input.attr('type') === 'password') {
            input.attr('type', 'text');
            $(this).find('i').removeClass('fa-eye').addClass('fa-eye-slash');
        } else {
            input.attr('type', 'password');
            $(this).find('i').removeClass('fa-eye-slash').addClass('fa-eye');
        }
    });
    
    // Return book with confirmation
    $('.return-book').click(function(e) {
        e.preventDefault();
        var form = $(this).closest('form');
        if (confirm('Are you sure you want to return this book?')) {
            form.submit();
        }
    });
    
    // Book rating stars
    $('.rating-stars').each(function() {
        var rating = parseFloat($(this).data('rating'));
        var stars = $(this).find('.star');
        stars.each(function(index) {
            if (index < Math.floor(rating)) {
                $(this).removeClass('far').addClass('fas');
            } else if (index < rating) {
                $(this).removeClass('far').addClass('fas fa-star-half-alt');
            } else {
                $(this).removeClass('fas').addClass('far');
            }
        });
    });
});

// Utility Functions
function formatDate(date) {
    var d = new Date(date);
    return d.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function formatCurrency(amount) {
    return 'PKR ' + parseFloat(amount).toFixed(2);
}

function showToast(message, type) {
    var classes = {
        'success': 'bg-success',
        'error': 'bg-danger',
        'warning': 'bg-warning',
        'info': 'bg-info'
    };
    
    var toast = $(`
        <div class="toast align-items-center text-white ${classes[type] || 'bg-primary'} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `);
    
    $('.toast-container').append(toast);
    var bsToast = new bootstrap.Toast(toast);
    bsToast.show();
}

// Export functions for use in other scripts
window.showToast = showToast;
window.formatDate = formatDate;
window.formatCurrency = formatCurrency;