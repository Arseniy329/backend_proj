"""
Phase 3 — Unit tests for models and business logic.

Coverage:
  1. User Model & Authentication (JWT phone login)
  2. Lesson Scheduling & Conflict Prevention
  3. Attendance Marking
"""
import datetime

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from users.models import CustomUser
from students.models import Student
from branches.models import Branch, Subject, Group, Lesson, Attendance


# ---------------------------------------------------------------------------
#  Reusable test-data mixin
# ---------------------------------------------------------------------------

class BaseTestDataMixin:
    """
    Creates a shared set of objects used across multiple test classes:
      - branch, subject, group
      - admin user, teacher user
      - student (added to group)
    """

    def _create_base_data(self):
        # Branch
        self.branch = Branch.objects.create(
            name='Головна філія',
            address='вул. Тестова, 1',
            city='Київ',
        )

        # Subject
        self.subject = Subject.objects.create(
            name='Математика',
            description='Курс математики',
        )
        self.subject.branches.add(self.branch)

        # Admin
        self.admin = CustomUser.objects.create_user(
            phone='+380990000001',
            password='AdminPass123!',
            first_name='Адмін',
            last_name='Тестовий',
            role=CustomUser.Role.ADMIN,
            is_staff=True,
        )

        # Teacher
        self.teacher = CustomUser.objects.create_user(
            phone='+380990000002',
            password='TeacherPass123!',
            first_name='Викладач',
            last_name='Тестовий',
            role=CustomUser.Role.TEACHER,
        )

        # Second teacher (for conflict-free checks)
        self.teacher2 = CustomUser.objects.create_user(
            phone='+380990000003',
            password='TeacherPass123!',
            first_name='Другий',
            last_name='Викладач',
            role=CustomUser.Role.TEACHER,
        )

        # Student
        self.student = Student.objects.create(
            first_name='Іван',
            last_name='Тестовий',
            branch=self.branch,
        )

        # Group with the student
        self.group = Group.objects.create(
            name='Група А',
            branch=self.branch,
        )
        self.group.subjects.add(self.subject)
        self.group.students.add(self.student)

        # Second group (separate students for conflict tests)
        self.student2 = Student.objects.create(
            first_name='Петро',
            last_name='Другий',
            branch=self.branch,
        )
        self.group2 = Group.objects.create(
            name='Група Б',
            branch=self.branch,
        )
        self.group2.subjects.add(self.subject)
        self.group2.students.add(self.student2)


# ===========================================================================
#  1. User Model & Authentication
# ===========================================================================

class UserAuthenticationTests(BaseTestDataMixin, TestCase):
    """Tests for phone-based JWT authentication."""

    def setUp(self):
        self._create_base_data()
        self.client = APIClient()
        self.login_url = '/api/auth/login/'

    def test_login_with_valid_credentials(self):
        """Active user logs in with correct phone + password → 200 + tokens."""
        response = self.client.post(self.login_url, {
            'phone': '+380990000002',
            'password': 'TeacherPass123!',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('access', data)
        self.assertIn('refresh', data)
        self.assertEqual(data['user']['phone'], '+380990000002')
        self.assertEqual(data['user']['role'], 'teacher')

    def test_login_with_wrong_password(self):
        """Wrong password → 400 with error message."""
        response = self.client.post(self.login_url, {
            'phone': '+380990000002',
            'password': 'WrongPassword!',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('access', response.json())

    def test_login_inactive_user_rejected(self):
        """Inactive user (is_active=False) cannot log in."""
        self.teacher.is_active = False
        self.teacher.save(update_fields=['is_active'])

        response = self.client.post(self.login_url, {
            'phone': '+380990000002',
            'password': 'TeacherPass123!',
        })
        # Django's authenticate() returns None for inactive users,
        # so the serializer raises a validation error.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('access', response.json())

    def test_login_nonexistent_phone(self):
        """Phone number not in DB → 400."""
        response = self.client.post(self.login_url, {
            'phone': '+380999999999',
            'password': 'SomePass123!',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_role_detection(self):
        """Admin login returns role='admin'."""
        response = self.client.post(self.login_url, {
            'phone': '+380990000001',
            'password': 'AdminPass123!',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['user']['role'], 'admin')


# ===========================================================================
#  2. Lesson Scheduling & Conflict Prevention
# ===========================================================================

class LessonCreationTests(BaseTestDataMixin, TestCase):
    """Tests for creating lessons without conflicts."""

    def setUp(self):
        self._create_base_data()
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)
        self.lessons_url = '/api/lessons/'

    def test_create_lesson_success(self):
        """Creating a lesson with no conflicts succeeds with SCHEDULED status."""
        response = self.client.post(self.lessons_url, {
            'group': self.group.pk,
            'subject': self.subject.pk,
            'teacher': self.teacher.pk,
            'date': '2026-06-15',
            'start_time': '10:00',
            'end_time': '11:00',
            'topic': 'Алгебра — вступ',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertEqual(data['status'], Lesson.Status.SCHEDULED)
        self.assertEqual(data['teacher'], self.teacher.pk)

    def test_lesson_defaults_to_scheduled(self):
        """Without explicit status, new lesson is SCHEDULED."""
        lesson = Lesson.objects.create(
            group=self.group,
            subject=self.subject,
            teacher=self.teacher,
            date=datetime.date(2026, 7, 1),
            start_time=datetime.time(9, 0),
            end_time=datetime.time(10, 0),
        )
        self.assertEqual(lesson.status, Lesson.Status.SCHEDULED)


class TeacherConflictTests(BaseTestDataMixin, TestCase):
    """Tests that teacher schedule conflicts are properly detected."""

    def setUp(self):
        self._create_base_data()
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)
        self.lessons_url = '/api/lessons/'

        # Existing lesson: 10:00–11:00
        self.existing_lesson = Lesson.objects.create(
            group=self.group,
            subject=self.subject,
            teacher=self.teacher,
            date=datetime.date(2026, 6, 20),
            start_time=datetime.time(10, 0),
            end_time=datetime.time(11, 0),
        )

    def test_teacher_overlap_rejected(self):
        """
        Creating a lesson for the same teacher at 10:30–11:30
        (overlaps 10:00–11:00) must be rejected.
        """
        response = self.client.post(self.lessons_url, {
            'group': self.group2.pk,
            'subject': self.subject.pk,
            'teacher': self.teacher.pk,
            'date': '2026-06-20',
            'start_time': '10:30',
            'end_time': '11:30',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertIn('schedule_conflict', data)

    def test_teacher_full_overlap_rejected(self):
        """
        Creating a lesson that fully contains the existing one
        (09:00–12:00 vs 10:00–11:00) must be rejected.
        """
        response = self.client.post(self.lessons_url, {
            'group': self.group2.pk,
            'subject': self.subject.pk,
            'teacher': self.teacher.pk,
            'date': '2026-06-20',
            'start_time': '09:00',
            'end_time': '12:00',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('schedule_conflict', response.json())

    def test_teacher_back_to_back_allowed(self):
        """
        Back-to-back lessons (10:00–11:00 then 11:00–12:00)
        must NOT trigger a conflict (start_1 < end_2 AND start_2 < end_1
        is NOT satisfied when end_1 == start_2).
        """
        response = self.client.post(self.lessons_url, {
            'group': self.group2.pk,
            'subject': self.subject.pk,
            'teacher': self.teacher.pk,
            'date': '2026-06-20',
            'start_time': '11:00',
            'end_time': '12:00',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_teacher_before_existing_allowed(self):
        """
        A lesson ending exactly when the existing one starts
        (09:00–10:00 before 10:00–11:00) is allowed.
        """
        response = self.client.post(self.lessons_url, {
            'group': self.group2.pk,
            'subject': self.subject.pk,
            'teacher': self.teacher.pk,
            'date': '2026-06-20',
            'start_time': '09:00',
            'end_time': '10:00',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_different_teacher_no_conflict(self):
        """
        Same time slot but DIFFERENT teacher → no conflict."""
        response = self.client.post(self.lessons_url, {
            'group': self.group2.pk,
            'subject': self.subject.pk,
            'teacher': self.teacher2.pk,
            'date': '2026-06-20',
            'start_time': '10:00',
            'end_time': '11:00',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_different_date_no_conflict(self):
        """Same teacher, same time, but different date → no conflict."""
        response = self.client.post(self.lessons_url, {
            'group': self.group2.pk,
            'subject': self.subject.pk,
            'teacher': self.teacher.pk,
            'date': '2026-06-21',
            'start_time': '10:00',
            'end_time': '11:00',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class StudentConflictTests(BaseTestDataMixin, TestCase):
    """Tests that student schedule conflicts are properly detected."""

    def setUp(self):
        self._create_base_data()
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)
        self.lessons_url = '/api/lessons/'

        # Existing lesson for group containing self.student: 14:00–15:00
        self.existing_lesson = Lesson.objects.create(
            group=self.group,
            subject=self.subject,
            teacher=self.teacher,
            date=datetime.date(2026, 6, 25),
            start_time=datetime.time(14, 0),
            end_time=datetime.time(15, 0),
        )

        # Put the same student into group2 for cross-group conflict test
        self.group2.students.add(self.student)

    def test_student_overlap_rejected(self):
        """
        Student is in group1 (14:00–15:00) and group2.
        Creating a lesson for group2 at 14:30–15:30 must be rejected
        because the student has a conflicting lesson.
        """
        response = self.client.post(self.lessons_url, {
            'group': self.group2.pk,
            'subject': self.subject.pk,
            'teacher': self.teacher2.pk,  # different teacher, no teacher conflict
            'date': '2026-06-25',
            'start_time': '14:30',
            'end_time': '15:30',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertIn('schedule_conflict', data)

    def test_student_back_to_back_allowed(self):
        """
        Student's group1 lesson ends at 15:00,
        group2 lesson starts at 15:00 → no conflict.
        """
        response = self.client.post(self.lessons_url, {
            'group': self.group2.pk,
            'subject': self.subject.pk,
            'teacher': self.teacher2.pk,
            'date': '2026-06-25',
            'start_time': '15:00',
            'end_time': '16:00',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_no_conflict_when_different_students(self):
        """
        group2 has only student2 (not student).
        A lesson at the same time should NOT conflict.
        """
        # Remove the shared student from group2
        self.group2.students.remove(self.student)

        response = self.client.post(self.lessons_url, {
            'group': self.group2.pk,
            'subject': self.subject.pk,
            'teacher': self.teacher2.pk,
            'date': '2026-06-25',
            'start_time': '14:00',
            'end_time': '15:00',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class LessonValidationTests(BaseTestDataMixin, TestCase):
    """Tests for other lesson validation rules."""

    def setUp(self):
        self._create_base_data()
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)
        self.lessons_url = '/api/lessons/'

    def test_end_time_before_start_time_rejected(self):
        """end_time must be strictly after start_time."""
        response = self.client.post(self.lessons_url, {
            'group': self.group.pk,
            'subject': self.subject.pk,
            'teacher': self.teacher.pk,
            'date': '2026-06-15',
            'start_time': '11:00',
            'end_time': '10:00',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('end_time', response.json())

    def test_same_start_and_end_time_rejected(self):
        """start_time == end_time is invalid."""
        response = self.client.post(self.lessons_url, {
            'group': self.group.pk,
            'subject': self.subject.pk,
            'teacher': self.teacher.pk,
            'date': '2026-06-15',
            'start_time': '10:00',
            'end_time': '10:00',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# ===========================================================================
#  3. Attendance Marking
# ===========================================================================

class AttendanceMarkingTests(BaseTestDataMixin, TestCase):
    """Tests for the mark_attendance action and attendance CRUD."""

    def setUp(self):
        self._create_base_data()
        self.client = APIClient()

        # Lesson assigned to self.teacher
        self.lesson = Lesson.objects.create(
            group=self.group,
            subject=self.subject,
            teacher=self.teacher,
            date=datetime.date(2026, 6, 15),
            start_time=datetime.time(10, 0),
            end_time=datetime.time(11, 0),
        )
        self.mark_url = f'/api/lessons/{self.lesson.pk}/mark_attendance/'

    def test_teacher_can_mark_attendance(self):
        """
        Authorized teacher (assigned to the lesson) can mark attendance
        for a student in the group.
        """
        self.client.force_authenticate(user=self.teacher)

        response = self.client.post(self.mark_url, {
            'records': [
                {
                    'student': self.student.pk,
                    'status': Attendance.Status.PRESENT,
                    'note': '',
                },
            ],
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data['created']), 1)
        self.assertEqual(len(data['errors']), 0)

        # Verify in DB
        att = Attendance.objects.get(
            lesson=self.lesson,
            student=self.student,
        )
        self.assertEqual(att.status, Attendance.Status.PRESENT)

    def test_teacher_mark_multiple_statuses(self):
        """Teacher marks one student present, another absent."""
        # Add student2 to the lesson's group
        self.group.students.add(self.student2)

        self.client.force_authenticate(user=self.teacher)

        response = self.client.post(self.mark_url, {
            'records': [
                {'student': self.student.pk, 'status': 'present'},
                {'student': self.student2.pk, 'status': 'absent', 'note': 'хвороба'},
            ],
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['created']), 2)

        att2 = Attendance.objects.get(lesson=self.lesson, student=self.student2)
        self.assertEqual(att2.status, Attendance.Status.ABSENT)
        self.assertEqual(att2.note, 'хвороба')

    def test_other_teacher_cannot_mark_attendance(self):
        """A teacher NOT assigned to the lesson is forbidden."""
        self.client.force_authenticate(user=self.teacher2)

        response = self.client.post(self.mark_url, {
            'records': [
                {'student': self.student.pk, 'status': 'present'},
            ],
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_mark_attendance(self):
        """Admin can mark attendance on any lesson."""
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(self.mark_url, {
            'records': [
                {'student': self.student.pk, 'status': 'present'},
            ],
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_student_not_in_group_rejected(self):
        """Marking attendance for a student NOT in the group returns error."""
        self.client.force_authenticate(user=self.teacher)

        response = self.client.post(self.mark_url, {
            'records': [
                {'student': self.student2.pk, 'status': 'present'},
            ],
        }, format='json')

        # Request succeeds but with errors in the response
        data = response.json()
        self.assertEqual(len(data['errors']), 1)
        self.assertEqual(len(data['created']), 0)

    def test_mark_attendance_on_cancelled_lesson_rejected(self):
        """Cannot mark attendance on a cancelled lesson."""
        self.lesson.status = Lesson.Status.CANCELLED
        self.lesson.save(update_fields=['status'])

        self.client.force_authenticate(user=self.teacher)

        response = self.client.post(self.mark_url, {
            'records': [
                {'student': self.student.pk, 'status': 'present'},
            ],
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_attendance_updates_existing(self):
        """Marking attendance twice for the same student updates, not duplicates."""
        self.client.force_authenticate(user=self.teacher)

        # First mark — creates
        self.client.post(self.mark_url, {
            'records': [
                {'student': self.student.pk, 'status': 'present'},
            ],
        }, format='json')

        # Second mark — updates
        response = self.client.post(self.mark_url, {
            'records': [
                {'student': self.student.pk, 'status': 'late', 'note': 'запізнився'},
            ],
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data['updated']), 1)
        self.assertEqual(len(data['created']), 0)

        att = Attendance.objects.get(lesson=self.lesson, student=self.student)
        self.assertEqual(att.status, Attendance.Status.LATE)


class LessonCompletionTests(BaseTestDataMixin, TestCase):
    """Tests for the lesson complete action."""

    def setUp(self):
        self._create_base_data()
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

        self.lesson = Lesson.objects.create(
            group=self.group,
            subject=self.subject,
            teacher=self.teacher,
            date=datetime.date(2026, 6, 15),
            start_time=datetime.time(10, 0),
            end_time=datetime.time(11, 0),
        )
        self.complete_url = f'/api/lessons/{self.lesson.pk}/complete/'

    def test_complete_scheduled_lesson(self):
        """Admin can complete a SCHEDULED lesson → status becomes COMPLETED."""
        response = self.client.post(self.complete_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.status, Lesson.Status.COMPLETED)

    def test_complete_already_completed_rejected(self):
        """Cannot complete a lesson that is already COMPLETED."""
        self.lesson.status = Lesson.Status.COMPLETED
        self.lesson.save(update_fields=['status'])

        response = self.client.post(self.complete_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_complete_cancelled_lesson_rejected(self):
        """Cannot complete a CANCELLED lesson."""
        self.lesson.status = Lesson.Status.CANCELLED
        self.lesson.save(update_fields=['status'])

        response = self.client.post(self.complete_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_full_flow_mark_attendance_then_complete(self):
        """
        Full workflow: teacher marks attendance, then admin completes lesson.
        Verifies both attendance records and lesson status.
        """
        # 1. Teacher marks attendance
        self.client.force_authenticate(user=self.teacher)
        mark_url = f'/api/lessons/{self.lesson.pk}/mark_attendance/'
        response = self.client.post(mark_url, {
            'records': [
                {'student': self.student.pk, 'status': 'present'},
            ],
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 2. Admin completes the lesson
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.complete_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 3. Verify final state
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.status, Lesson.Status.COMPLETED)

        att = Attendance.objects.get(lesson=self.lesson, student=self.student)
        self.assertEqual(att.status, Attendance.Status.PRESENT)
