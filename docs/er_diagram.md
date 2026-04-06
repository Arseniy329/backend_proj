# ER Diagram — Education Platform

## Діаграма зв'язків між сутностями

```
┌─────────────────────┐       ┌─────────────────────┐
│    CustomUser        │       │      Branch          │
│─────────────────────│       │─────────────────────│
│ PK id               │       │ PK id                │
│    phone (unique)    │       │    name              │
│    first_name        │       │    address           │
│    last_name         │       │    city              │
│    role (admin/      │       │    status (active/   │
│         teacher)     │       │           archived)  │
│    is_active         │       │    created_at        │
│    is_staff          │       └──────────┬──────────┘
│    date_joined       │                  │
└──────────┬──────────┘                  │ 1
           │                             │
           │                    ┌────────┴─────────┐
           │                    │                  │
           │ 1                  │ *                │ *
  ┌────────┴──────────┐  ┌─────┴───────────┐ ┌───┴──────────────┐
  │      Lesson        │  │    Student       │ │ SubscriptionPlan │
  │───────────────────│  │────────────────│ │─────────────────│
  │ PK id              │  │ PK id           │ │ PK id            │
  │ FK group_id        │  │    first_name   │ │    name           │
  │ FK teacher_id ─────┤  │    last_name    │ │    lessons_count  │
  │    date            │  │    phone        │ │    price          │
  │    start_time      │  │    date_of_birth│ │    duration_days  │
  │    end_time        │  │    parent_name  │ │ FK branch_id      │
  │    topic           │  │    parent_phone │ │    created_at     │
  │    status           │  │    parent_email │ └──────────────────┘
  │    created_at      │  │ FK branch_id    │
  └────────┬──────────┘  │    status        │
           │              │    created_at   │
           │ 1            └────────┬───────┘
           │                       │
           │                       │ M2M (through Group.students)
      ┌────┴──────────┐           │
      │  Attendance    │     ┌────┴────────────┐
      │───────────────│     │     Group         │
      │ PK id          │     │────────────────│
      │ FK lesson_id   │     │ PK id            │
      │ FK student_id ─┼─────│ FK branch_id     │
      │    status       │     │ FK subject_id    │
      │    note        │     │ FK teacher_id    │
      │    created_at  │     │ M2M students     │
      └───────────────┘     │    name           │
                             │    status         │
                             │    created_at     │
                             └────────┬─────────┘
                                      │
                                      │ FK
                              ┌───────┴────────┐
                              │    Subject      │
                              │───────────────│
                              │ PK id           │
                              │    name         │
                              │    description  │
                              │    status       │
                              │ M2M branches    │
                              │    created_at   │
                              └────────────────┘
```

## Зв'язки (Relationships)

| Зв'язок | Тип | Опис |
|---------|-----|------|
| Branch → Student | One-to-Many | Гілка має багато студентів |
| Branch → Group | One-to-Many | Гілка має багато груп |
| Branch → SubscriptionPlan | One-to-Many | Гілка має багато абонементів |
| Subject ↔ Branch | Many-to-Many | Предмет може викладатися в кількох гілках |
| Subject → Group | One-to-Many | Предмет має багато груп |
| CustomUser → Group | One-to-Many | Викладач веде багато груп |
| CustomUser → Lesson | One-to-Many | Викладач проводить багато занять |
| Group → Lesson | One-to-Many | Група має багато занять |
| Group ↔ Student | Many-to-Many | Студент може бути в кількох групах |
| Lesson → Attendance | One-to-Many | Заняття має багато записів відвідування |
| Student → Attendance | One-to-Many | Студент має багато записів відвідування |

## Сутності

### CustomUser (Користувач)
- Ідентифікація за номером телефону
- Ролі: `admin`, `teacher`

### Branch (Гілка)
- Фізична локація навчального закладу
- Soft delete через статус `archived`

### Subject (Предмет)
- Дисципліна, яка викладається
- M2M зв'язок з гілками

### Student (Студент)
- Учень з контактами батьків
- Soft delete через статус `archived`

### Group (Група)
- Навчальна група: гілка + предмет + викладач + студенти

### SubscriptionPlan (Абонемент)
- Тарифний план: кількість занять, ціна, тривалість

### Lesson (Заняття)
- Окреме заняття: дата, час, тема, статус

### Attendance (Відвідування)
- Запис відвідування: студент + заняття + статус
