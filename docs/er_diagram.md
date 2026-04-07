# ER-діаграма бази даних

## Огляд

База даних складається з **8 моделей** у **3 додатках** Django.

| Додаток    | Моделі                                                    |
|------------|-----------------------------------------------------------|
| `users`    | CustomUser                                                |
| `branches` | Branch, Subject, Group, SubscriptionPlan, Lesson, Attendance |
| `students` | Student                                                   |

---

## Діаграма зв'язків

```mermaid
erDiagram
    CustomUser {
        BigAutoField id PK
        CharField phone UK
        CharField first_name
        CharField last_name
        CharField role "admin | teacher"
        BooleanField is_active
        BooleanField is_staff
        DateTimeField date_joined
    }

    Branch {
        BigAutoField id PK
        CharField name
        CharField address
        CharField city
        CharField status "active | archived"
    }

    Subject {
        BigAutoField id PK
        CharField name
        TextField description
        CharField status "active | archived"
    }

    Group {
        BigAutoField id PK
        CharField name
        FK branch
        FK subject
        FK teacher
        CharField status "active | inactive"
    }

    Student {
        BigAutoField id PK
        CharField first_name
        CharField last_name
        CharField phone
        DateField date_of_birth
        CharField parent_name
        CharField parent_phone
        EmailField parent_email
        FK branch
        CharField status "active | archived"
    }

    SubscriptionPlan {
        BigAutoField id PK
        CharField name
        PositiveIntegerField lessons_count
        DecimalField price
        PositiveIntegerField duration_days
        FK branch
    }

    Lesson {
        BigAutoField id PK
        FK group
        FK teacher
        DateField date
        TimeField start_time
        TimeField end_time
        CharField topic
        CharField status "scheduled | completed | cancelled"
    }

    Attendance {
        BigAutoField id PK
        FK lesson
        FK student
        CharField status "present | absent | late"
        TextField note
    }

    Branch ||--o{ Group : "has"
    Branch ||--o{ Student : "enrolled in"
    Branch ||--o{ SubscriptionPlan : "offers"
    Subject ||--o{ Group : "taught in"
    Subject }o--o{ Branch : "M2M available at"
    CustomUser ||--o{ Group : "teaches"
    CustomUser ||--o{ Lesson : "conducts"
    Student }o--o{ Group : "M2M belongs to"
    Group ||--o{ Lesson : "has"
    Lesson ||--o{ Attendance : "tracks"
    Student ||--o{ Attendance : "recorded for"
```

---

## Таблиця зв'язків

| Зв'язок | Тип | on_delete | Опис |
|---------|-----|-----------|------|
| Group → Branch | FK | CASCADE | Група належить до гілки |
| Group → Subject | FK | CASCADE | Група вивчає предмет |
| Group → CustomUser | FK | SET_NULL | Викладач групи (необов'язковий) |
| Group ↔ Student | M2M | — | Студенти в групі |
| Subject ↔ Branch | M2M | — | Предмет доступний у гілках |
| Student → Branch | FK | CASCADE | Студент прикріплений до гілки |
| SubscriptionPlan → Branch | FK | CASCADE | Абонемент для конкретної гілки |
| Lesson → Group | FK | CASCADE | Заняття в групі |
| Lesson → CustomUser | FK | SET_NULL | Викладач заняття |
| Attendance → Lesson | FK | CASCADE | Відвідування заняття |
| Attendance → Student | FK | CASCADE | Відвідування студентом |

> **Constraint:** `Attendance` має `unique_together = ('lesson', 'student')` — один запис на студента на заняття.
