from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import Student
from branches.models import Branch


@login_required
def student_list(request):
    branch_id = request.GET.get('branch')
    show_archived = request.GET.get('archived', '') == '1'

    if show_archived:
        students = Student.objects.filter(status=Student.Status.ARCHIVED)
    else:
        students = Student.objects.filter(status=Student.Status.ACTIVE)

    if branch_id:
        students = students.filter(branch_id=branch_id)

    students = students.select_related('branch').prefetch_related('groups')
    branches = Branch.objects.filter(status=Branch.Status.ACTIVE)

    return render(request, 'students/student_list.html', {
        'students': students,
        'branches': branches,
        'selected_branch': branch_id,
        'show_archived': show_archived,
    })


@login_required
def student_create(request):
    branches = Branch.objects.filter(status=Branch.Status.ACTIVE)

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        date_of_birth = request.POST.get('date_of_birth') or None
        parent_name = request.POST.get('parent_name', '').strip()
        parent_phone = request.POST.get('parent_phone', '').strip()
        parent_email = request.POST.get('parent_email', '').strip()
        branch_id = request.POST.get('branch') or None

        if not first_name or not last_name:
            messages.error(request, 'Ім\'я та прізвище обов\'язкові.')
            return render(request, 'students/student_form.html', {
                'branches': branches, 'action': 'Створити'
            })

        Student.objects.create(
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            date_of_birth=date_of_birth,
            parent_name=parent_name,
            parent_phone=parent_phone,
            parent_email=parent_email,
            branch_id=branch_id,
        )
        messages.success(request, f'Студента "{first_name} {last_name}" створено.')
        return redirect('student_list')

    return render(request, 'students/student_form.html', {
        'branches': branches, 'action': 'Створити'
    })


@login_required
def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    branches = Branch.objects.filter(status=Branch.Status.ACTIVE)

    if request.method == 'POST':
        student.first_name = request.POST.get('first_name', '').strip()
        student.last_name = request.POST.get('last_name', '').strip()
        student.phone = request.POST.get('phone', '').strip()
        student.date_of_birth = request.POST.get('date_of_birth') or None
        student.parent_name = request.POST.get('parent_name', '').strip()
        student.parent_phone = request.POST.get('parent_phone', '').strip()
        student.parent_email = request.POST.get('parent_email', '').strip()
        branch_id = request.POST.get('branch')
        student.branch_id = branch_id if branch_id else None

        if not student.first_name or not student.last_name:
            messages.error(request, 'Ім\'я та прізвище обов\'язкові.')
            return render(request, 'students/student_form.html', {
                'student': student, 'branches': branches, 'action': 'Зберегти'
            })

        student.save()
        messages.success(request, f'Студента "{student}" оновлено.')
        return redirect('student_list')

    return render(request, 'students/student_form.html', {
        'student': student, 'branches': branches, 'action': 'Зберегти'
    })


@login_required
def student_archive(request, pk):
    student = get_object_or_404(Student, pk=pk)
    student.archive()
    messages.success(request, f'Студента "{student}" архівовано.')
    return redirect('student_list')


@login_required
def student_restore(request, pk):
    student = get_object_or_404(Student, pk=pk)
    student.restore()
    messages.success(request, f'Студента "{student}" відновлено.')
    return redirect('student_list')
