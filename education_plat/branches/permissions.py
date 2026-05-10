from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminRole(BasePermission):
    """
    Повний CRUD для адміністраторів.
    Викладачі мають лише READ-ONLY доступ (GET, HEAD, OPTIONS).

    Використовується для: Branch, Subject, Group, SubscriptionPlan, Lesson.
    """

    message = 'Тільки адміністратор може виконувати цю дію.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Безпечні методи (GET, HEAD, OPTIONS) дозволені всім авторизованим
        if request.method in SAFE_METHODS:
            return True

        # Запис дозволено лише адміністраторам
        return request.user.is_admin


class IsAdminOrTeacherOwnLesson(BasePermission):
    """
    Права для відвідуваності (Attendance):

    - ADMIN: повний CRUD без обмежень.
    - TEACHER: може створювати (POST) та оновлювати (PUT/PATCH) записи,
      але ТІЛЬКИ для занять, де він є викладачем.
      Видалення (DELETE) заборонено.

    Перевірка на рівні об'єкта (has_object_permission) гарантує,
    що вчитель не зможе змінити чужий запис відвідуваності.
    """

    message = 'Ви не маєте права виконувати цю дію з відвідуваністю.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Адмін — все дозволено
        if request.user.is_admin:
            return True

        # Викладач — читання та створення/оновлення дозволено,
        # видалення заборонено
        if request.user.is_teacher:
            if request.method == 'DELETE':
                return False
            return True

        return False

    def has_object_permission(self, request, view, obj):
        # Адмін — все дозволено
        if request.user.is_admin:
            return True

        # Безпечні методи — дозволено (queryset вже відфільтрований)
        if request.method in SAFE_METHODS:
            return True

        # Викладач може змінювати лише відвідуваність СВОЇХ занять
        if request.user.is_teacher:
            return obj.lesson.teacher_id == request.user.pk

        return False


class IsAdminOrTeacherMarkAttendance(BasePermission):
    """
    Окремий permission для кастомної дії mark_attendance на LessonViewSet.

    - ADMIN: дозволено завжди.
    - TEACHER: дозволено лише для занять, де він є викладачем.
    """

    message = 'Ви можете відмічати відвідуваність лише на своїх заняттях.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_admin:
            return True

        if request.user.is_teacher:
            return obj.teacher_id == request.user.pk

        return False
