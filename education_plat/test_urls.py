import django
django.setup()
from django.urls import get_resolver
resolver = get_resolver()
for url_pattern in resolver.url_patterns:
    print(url_pattern)
