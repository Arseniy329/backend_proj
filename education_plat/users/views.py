from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages


def login_view(request):
    """Авторизація за номером телефону та паролем."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=phone, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Вітаємо, {user.first_name}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Невірний номер телефону або пароль.')

    return render(request, 'users/login.html')


@login_required
def logout_view(request):
    """Вихід з системи."""
    logout(request)
    messages.info(request, 'Ви вийшли з системи.')
    return redirect('login')


@login_required
def dashboard_view(request):
    """Головна сторінка панелі управління."""
    from branches.models import Branch, Subject, Group, Lesson
    from students.models import Student

    context = {
        'branches_count': Branch.objects.filter(status='active').count(),
        'students_count': Student.objects.filter(status='active').count(),
        'subjects_count': Subject.objects.filter(status='active').count(),
        'groups_count': Group.objects.filter(status='active').count(),
        'lessons_count': Lesson.objects.count(),
    }
    return render(request, 'users/dashboard.html', context)
