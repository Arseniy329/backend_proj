# Планування API / URL-маршрутів

## Поточна архітектура

Проект використовує серверний рендеринг (Django templates) з HTML-формами.  
URL-маршрути організовані по додатках і підключені через `include()` в головному `urls.py`.

---

## Маршрути

### Автентифікація (`users/urls.py`)

| Метод | URL | View | Name | Опис |
|-------|-----|------|------|------|
| GET/POST | `/login/` | `login_view` | `login` | Авторизація (телефон + пароль) |
| GET | `/logout/` | `logout_view` | `logout` | Вихід із системи |
| GET | `/` | `dashboard_view` | `dashboard` | Головна панель управління |

---

### Гілки (`branches/urls.py`)

| Метод | URL | View | Name | Опис |
|-------|-----|------|------|------|
| GET | `/branches/` | `branch_list` | `branch_list` | Список гілок |
| GET/POST | `/branches/create/` | `branch_create` | `branch_create` | Створення гілки |
| GET/POST | `/branches/<pk>/edit/` | `branch_edit` | `branch_edit` | Редагування гілки |
| GET | `/branches/<pk>/archive/` | `branch_archive` | `branch_archive` | Архівувати гілку |
| GET | `/branches/<pk>/restore/` | `branch_restore` | `branch_restore` | Відновити гілку |

**Параметри фільтрації:** `?archived=1` — показати архівовані.

---

### Предмети (`branches/urls.py`)

| Метод | URL | View | Name | Опис |
|-------|-----|------|------|------|
| GET | `/subjects/` | `subject_list` | `subject_list` | Список предметів |
| GET/POST | `/subjects/create/` | `subject_create` | `subject_create` | Створення предмету |
| GET/POST | `/subjects/<pk>/edit/` | `subject_edit` | `subject_edit` | Редагування предмету |

**Параметри фільтрації:** `?branch=<id>` — фільтр по гілці.

---

### Групи (`branches/urls.py`)

| Метод | URL | View | Name | Опис |
|-------|-----|------|------|------|
| GET | `/groups/` | `group_list` | `group_list` | Список груп |
| GET/POST | `/groups/create/` | `group_create` | `group_create` | Створення групи |
| GET/POST | `/groups/<pk>/edit/` | `group_edit` | `group_edit` | Редагування групи |

**Параметри фільтрації:** `?branch=<id>` — фільтр по гілці.

---

### Студенти (`students/urls.py`)

| Метод | URL | View | Name | Опис |
|-------|-----|------|------|------|
| GET | `/students/` | `student_list` | `student_list` | Список студентів |
| GET/POST | `/students/create/` | `student_create` | `student_create` | Створення студента |
| GET/POST | `/students/<pk>/edit/` | `student_edit` | `student_edit` | Редагування студента |
| GET | `/students/<pk>/archive/` | `student_archive` | `student_archive` | Архівувати студента |
| GET | `/students/<pk>/restore/` | `student_restore` | `student_restore` | Відновити студента |

**Параметри фільтрації:** `?branch=<id>`, `?archived=1`.

---

### Адмін-панель

| URL | Опис |
|-----|------|
| `/admin/` | Стандартна Django Admin для всіх моделей |

---

## Dashboard — агреговані дані

Головна сторінка (`/`) показує лічильники:

| Лічильник | Джерело |
|-----------|---------|
| Гілок | `Branch.objects.filter(status='active').count()` |
| Студентів | `Student.objects.filter(status='active').count()` |
| Предметів | `Subject.objects.filter(status='active').count()` |
| Груп | `Group.objects.filter(status='active').count()` |
| Занять | `Lesson.objects.count()` |

---

## Захист маршрутів

- **Усі** маршрути, крім `/login/`, захищені `@login_required`.
- Неавторизованих користувачів перенаправляє на `/login/`.
- Після логіну — редирект на `/` (dashboard).
