from django.conf import settings

def site_settings(request):
    return {
        'SITE_NAME': 'LibraryMS',
        'SITE_DESCRIPTION': 'Professional Library Management System',
        'LIBRARY_SETTINGS': settings.LIBRARY_SETTINGS,
    }