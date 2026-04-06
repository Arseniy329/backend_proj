import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'education_plat.settings'
django.setup()

from users.models import CustomUser

if not CustomUser.objects.filter(phone='+380000000000').exists():
    u = CustomUser.objects.create_superuser(
        phone='+380000000000',
        password='admin123',
        first_name='Admin',
        last_name='User',
    )
    print(f'Superuser created: {u}')
else:
    print('Superuser already exists')
