# API Endpoint Mapping — Education Platform

## Загальна структура

Базовий шлях: `/api/v1/`

Формат відповіді: JSON

Автентифікація: Token-based (буде реалізовано у Phase 2)

---

## Authentication (Автентифікація)

| Метод | URL | Опис |
|-------|-----|------|
| POST | `/api/v1/auth/login/` | Вхід за номером телефону + пароль |
| POST | `/api/v1/auth/logout/` | Вихід з системи |
| GET | `/api/v1/auth/me/` | Отримати профіль поточного користувача |

---

## Branches (Гілки)

| Метод | URL | Опис | Доступ |
|-------|-----|------|--------|
| GET | `/api/v1/branches/` | Список активних гілок | Admin, Teacher |
| POST | `/api/v1/branches/` | Створити гілку | Admin |
| GET | `/api/v1/branches/{id}/` | Деталі гілки | Admin, Teacher |
| PUT | `/api/v1/branches/{id}/` | Оновити гілку | Admin |
| DELETE | `/api/v1/branches/{id}/` | Архівувати гілку (soft delete) | Admin |
| POST | `/api/v1/branches/{id}/restore/` | Відновити з архіву | Admin |

---

## Subjects (Предмети)

| Метод | URL | Опис | Доступ |
|-------|-----|------|--------|
| GET | `/api/v1/subjects/` | Список предметів (фільтр по гілці: `?branch=ID`) | Admin, Teacher |
| POST | `/api/v1/subjects/` | Створити предмет | Admin |
| GET | `/api/v1/subjects/{id}/` | Деталі предмету | Admin, Teacher |
| PUT | `/api/v1/subjects/{id}/` | Оновити предмет | Admin |
| DELETE | `/api/v1/subjects/{id}/` | Видалити/архівувати предмет | Admin |

---

## Students (Студенти)

| Метод | URL | Опис | Доступ |
|-------|-----|------|--------|
| GET | `/api/v1/students/` | Список студентів (фільтр: `?branch=ID`) | Admin, Teacher |
| POST | `/api/v1/students/` | Створити студента | Admin |
| GET | `/api/v1/students/{id}/` | Деталі студента | Admin, Teacher |
| PUT | `/api/v1/students/{id}/` | Оновити студента | Admin |
| DELETE | `/api/v1/students/{id}/` | Архівувати студента (soft delete) | Admin |
| POST | `/api/v1/students/{id}/restore/` | Відновити з архіву | Admin |

---

## Groups (Групи)

| Метод | URL | Опис | Доступ |
|-------|-----|------|--------|
| GET | `/api/v1/groups/` | Список груп (фільтр: `?branch=ID`) | Admin, Teacher |
| POST | `/api/v1/groups/` | Створити групу | Admin |
| GET | `/api/v1/groups/{id}/` | Деталі групи | Admin, Teacher |
| PUT | `/api/v1/groups/{id}/` | Оновити групу | Admin |
| POST | `/api/v1/groups/{id}/add_student/` | Додати студента до групи | Admin |
| POST | `/api/v1/groups/{id}/remove_student/` | Видалити студента з групи | Admin |

---

## Subscription Plans (Абонементи)

| Метод | URL | Опис | Доступ |
|-------|-----|------|--------|
| GET | `/api/v1/plans/` | Список абонементів (фільтр: `?branch=ID`) | Admin |
| POST | `/api/v1/plans/` | Створити абонемент | Admin |
| GET | `/api/v1/plans/{id}/` | Деталі абонементу | Admin |
| PUT | `/api/v1/plans/{id}/` | Оновити абонемент | Admin |
| DELETE | `/api/v1/plans/{id}/` | Видалити абонемент | Admin |

---

## Lessons (Заняття)

| Метод | URL | Опис | Доступ |
|-------|-----|------|--------|
| GET | `/api/v1/lessons/` | Список занять (фільтр: `?group=ID&date=YYYY-MM-DD`) | Admin, Teacher |
| POST | `/api/v1/lessons/` | Створити заняття | Admin, Teacher |
| GET | `/api/v1/lessons/{id}/` | Деталі заняття | Admin, Teacher |
| PUT | `/api/v1/lessons/{id}/` | Оновити заняття | Admin, Teacher |
| DELETE | `/api/v1/lessons/{id}/` | Скасувати заняття | Admin |

---

## Attendance (Відвідування)

| Метод | URL | Опис | Доступ |
|-------|-----|------|--------|
| GET | `/api/v1/attendance/` | Список відвідувань (фільтр: `?lesson=ID&student=ID`) | Admin, Teacher |
| POST | `/api/v1/attendance/` | Додати запис відвідування | Teacher |
| PUT | `/api/v1/attendance/{id}/` | Оновити статус відвідування | Teacher |
| POST | `/api/v1/attendance/bulk/` | Масове відмічання (для всієї групи) | Teacher |

---

## Фільтрація та пагінація

- Пагінація: `?page=1&page_size=20`
- Сортування: `?ordering=created_at` або `?ordering=-name`
- Пошук: `?search=текст`
- Фільтрація по гілці (Branch-Level Isolation): `?branch=ID`
