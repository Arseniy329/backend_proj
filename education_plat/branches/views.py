from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import Branch, Subject, Group


@login_required
def branch_list(request):
    show_archived = request.GET.get('archived', '') == '1'
    if show_archived:
        branches = Branch.objects.filter(status=Branch.Status.ARCHIVED)
    else:
        branches = Branch.objects.filter(status=Branch.Status.ACTIVE)
    return render(request, 'branches/branch_list.html', {
        'branches': branches,
        'show_archived': show_archived,
    })


@login_required
def branch_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        address = request.POST.get('address', '').strip()
        city = request.POST.get('city', '').strip()
        if not name or not city:
            messages.error(request, 'Назва та місто обов\'язкові.')
            return render(request, 'branches/branch_form.html', {'action': 'Створити'})

        Branch.objects.create(name=name, address=address, city=city)
        messages.success(request, f'Гілку "{name}" створено.')
        return redirect('branch_list')

    return render(request, 'branches/branch_form.html', {'action': 'Створити'})


@login_required
def branch_edit(request, pk):
    branch = get_object_or_404(Branch, pk=pk)

    if request.method == 'POST':
        branch.name = request.POST.get('name', '').strip()
        branch.address = request.POST.get('address', '').strip()
        branch.city = request.POST.get('city', '').strip()

        if not branch.name or not branch.city:
            messages.error(request, 'Назва та місто обов\'язкові.')
            return render(request, 'branches/branch_form.html', {'branch': branch, 'action': 'Зберегти'})

        branch.save()
        messages.success(request, f'Гілку "{branch.name}" оновлено.')
        return redirect('branch_list')

    return render(request, 'branches/branch_form.html', {'branch': branch, 'action': 'Зберегти'})


@login_required
def branch_archive(request, pk):
    branch = get_object_or_404(Branch, pk=pk)
    branch.archive()
    messages.success(request, f'Гілку "{branch.name}" архівовано.')
    return redirect('branch_list')


@login_required
def branch_restore(request, pk):
    branch = get_object_or_404(Branch, pk=pk)
    branch.restore()
    messages.success(request, f'Гілку "{branch.name}" відновлено.')
    return redirect('branch_list')


@login_required
def subject_list(request):
    branch_id = request.GET.get('branch')
    subjects = Subject.objects.filter(
        status=Subject.Status.ACTIVE,
    ).prefetch_related('branches')
    if branch_id:
        subjects = subjects.filter(branches__id=branch_id)
    branches = Branch.objects.filter(status=Branch.Status.ACTIVE)
    return render(request, 'branches/subject_list.html', {
        'subjects': subjects,
        'branches': branches,
        'selected_branch': branch_id,
    })


@login_required
def subject_create(request):
    branches = Branch.objects.filter(status=Branch.Status.ACTIVE)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        branch_ids = request.POST.getlist('branches')

        if not name:
            messages.error(request, 'Назва обов\'язкова.')
            return render(request, 'branches/subject_form.html', {
                'branches': branches, 'action': 'Створити'
            })

        subject = Subject.objects.create(name=name, description=description)
        if branch_ids:
            subject.branches.set(branch_ids)
        messages.success(request, f'Предмет "{name}" створено.')
        return redirect('subject_list')

    return render(request, 'branches/subject_form.html', {
        'branches': branches, 'action': 'Створити'
    })


@login_required
def subject_edit(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    branches = Branch.objects.filter(status=Branch.Status.ACTIVE)

    if request.method == 'POST':
        subject.name = request.POST.get('name', '').strip()
        subject.description = request.POST.get('description', '').strip()
        branch_ids = request.POST.getlist('branches')

        if not subject.name:
            messages.error(request, 'Назва обов\'язкова.')
            return render(request, 'branches/subject_form.html', {
                'subject': subject, 'branches': branches, 'action': 'Зберегти'
            })

        subject.save()
        subject.branches.set(branch_ids)
        messages.success(request, f'Предмет "{subject.name}" оновлено.')
        return redirect('subject_list')

    return render(request, 'branches/subject_form.html', {
        'subject': subject, 'branches': branches, 'action': 'Зберегти'
    })


@login_required
def group_list(request):
    branch_id = request.GET.get('branch')
    groups = Group.objects.select_related(
        'branch',
    ).prefetch_related(
        'subjects', 'students',
    ).filter(status='active')
    if branch_id:
        groups = groups.filter(branch_id=branch_id)
    branches = Branch.objects.filter(status=Branch.Status.ACTIVE)
    return render(request, 'branches/group_list.html', {
        'groups': groups,
        'branches': branches,
        'selected_branch': branch_id,
    })


@login_required
def group_create(request):
    branches = Branch.objects.filter(status=Branch.Status.ACTIVE)
    subjects = Subject.objects.filter(status=Subject.Status.ACTIVE)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        branch_id = request.POST.get('branch')
        subject_ids = request.POST.getlist('subjects')

        if not name or not branch_id or not subject_ids:
            messages.error(request, 'Назва, гілка та предмети обов\'язкові.')
            return render(request, 'branches/group_form.html', {
                'branches': branches, 'subjects': subjects, 'action': 'Створити'
            })

        group = Group.objects.create(
            name=name,
            branch_id=branch_id,
        )
        group.subjects.set(subject_ids)
        messages.success(request, f'Групу "{name}" створено.')
        return redirect('group_list')

    return render(request, 'branches/group_form.html', {
        'branches': branches, 'subjects': subjects, 'action': 'Створити'
    })


@login_required
def group_edit(request, pk):
    group = get_object_or_404(Group, pk=pk)
    branches = Branch.objects.filter(status=Branch.Status.ACTIVE)
    subjects = Subject.objects.filter(status=Subject.Status.ACTIVE)

    if request.method == 'POST':
        group.name = request.POST.get('name', '').strip()
        group.branch_id = request.POST.get('branch')
        subject_ids = request.POST.getlist('subjects')

        if not group.name or not group.branch_id or not subject_ids:
            messages.error(request, 'Назва, гілка та предмети обов\'язкові.')
            return render(request, 'branches/group_form.html', {
                'group': group, 'branches': branches, 'subjects': subjects,
                'action': 'Зберегти'
            })

        group.save()
        group.subjects.set(subject_ids)
        messages.success(request, f'Групу "{group.name}" оновлено.')
        return redirect('group_list')

    return render(request, 'branches/group_form.html', {
        'group': group, 'branches': branches, 'subjects': subjects,
        'action': 'Зберегти'
    })
