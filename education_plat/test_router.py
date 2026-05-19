import django
django.setup()
from django.urls import reverse
print(reverse('api-root'))
