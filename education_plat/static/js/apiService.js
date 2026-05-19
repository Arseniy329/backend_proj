/**
 * apiService.js — клієнтський модуль для взаємодії з REST API Phase 2.
 *
 * Забезпечує:
 *  1. Безпечне збереження JWT-токенів (access + refresh).
 *  2. Автоматичне додавання заголовка Authorization: Bearer <token>.
 *  3. Автоматичне оновлення access-токена при отриманні 401.
 *  4. Парсинг помилок DRF (400) у зрозумілий для UI формат.
 *  5. Готові методи для роботи з Phase 2 ендпоінтами.
 */

// ──────────────────────────────────────────────
//  Конфігурація
// ──────────────────────────────────────────────

const API_BASE_URL = '/api';

const ENDPOINTS = {
    // Аутентифікація
    LOGIN:   `${API_BASE_URL}/auth/login/`,
    REFRESH: `${API_BASE_URL}/auth/refresh/`,
    LOGOUT:  `${API_BASE_URL}/auth/logout/`,

    // Phase 2 ресурси
    BRANCHES:          `${API_BASE_URL}/branches/`,
    SUBJECTS:          `${API_BASE_URL}/subjects/`,
    GROUPS:            `${API_BASE_URL}/groups/`,
    SUBSCRIPTION_PLANS:`${API_BASE_URL}/subscription-plans/`,
    LESSONS:           `${API_BASE_URL}/lessons/`,
    ATTENDANCES:       `${API_BASE_URL}/attendances/`,
    STUDENTS:          `${API_BASE_URL}/students/`,
    USERS:             `${API_BASE_URL}/users/`,
};


// ──────────────────────────────────────────────
//  1. JWT Storage & Management
// ──────────────────────────────────────────────

const TokenStorage = {
    ACCESS_KEY:  'edu_access_token',
    REFRESH_KEY: 'edu_refresh_token',
    USER_KEY:    'edu_user',

    /** Зберегти обидва токени після логіну. */
    saveTokens(access, refresh) {
        localStorage.setItem(this.ACCESS_KEY, access);
        localStorage.setItem(this.REFRESH_KEY, refresh);
    },

    /** Зберегти дані поточного користувача (id, phone, role, full_name). */
    saveUser(user) {
        localStorage.setItem(this.USER_KEY, JSON.stringify(user));
    },

    getAccessToken()  { return localStorage.getItem(this.ACCESS_KEY); },
    getRefreshToken() { return localStorage.getItem(this.REFRESH_KEY); },
    getUser()         {
        const raw = localStorage.getItem(this.USER_KEY);
        return raw ? JSON.parse(raw) : null;
    },

    /** Повне очищення — виклик при logout або при неможливості оновити токен. */
    clear() {
        localStorage.removeItem(this.ACCESS_KEY);
        localStorage.removeItem(this.REFRESH_KEY);
        localStorage.removeItem(this.USER_KEY);
    },

    /** Перевірка: чи є збережений access-токен. */
    isAuthenticated() {
        return Boolean(this.getAccessToken());
    },
};


// ──────────────────────────────────────────────
//  2. Парсинг помилок DRF → зрозумілий UI формат
// ──────────────────────────────────────────────

/**
 * Перетворює відповідь DRF (400/403/422) у плаский масив рядків,
 * який можна одразу показати користувачу.
 *
 * DRF повертає помилки у різних форматах:
 *   { "field": ["msg1", "msg2"] }
 *   { "detail": "string" }
 *   { "error": "string" }
 *   { "non_field_errors": ["msg"] }
 *
 * Ця функція зводить усе до: ["field: msg1", "field: msg2", ...].
 */
function parseValidationErrors(data) {
    const messages = [];

    if (!data || typeof data !== 'object') {
        return ['Невідома помилка сервера.'];
    }

    // Проста рядкова помилка
    if (typeof data === 'string') {
        return [data];
    }

    // { "detail": "..." } — стандартна помилка DRF
    if (data.detail) {
        return [String(data.detail)];
    }

    // { "error": "..." } — наш кастомний формат
    if (data.error) {
        return [String(data.error)];
    }

    // Перебираємо поля
    for (const [field, errors] of Object.entries(data)) {
        if (Array.isArray(errors)) {
            errors.forEach((err) => {
                const msg = typeof err === 'object' ? JSON.stringify(err) : String(err);
                messages.push(field === 'non_field_errors' ? msg : `${field}: ${msg}`);
            });
        } else if (typeof errors === 'string') {
            messages.push(field === 'non_field_errors' ? errors : `${field}: ${errors}`);
        } else if (typeof errors === 'object') {
            // Вкладені об'єкти (напр. schedule_conflict)
            messages.push(`${field}: ${JSON.stringify(errors)}`);
        }
    }

    return messages.length ? messages : ['Невідома помилка валідації.'];
}


// ──────────────────────────────────────────────
//  3. Base API Client (з auto-refresh)
// ──────────────────────────────────────────────

/** Прапорець: чи ми зараз у процесі оновлення токена. */
let isRefreshing = false;
/** Черга запитів, які чекають на оновлений токен. */
let refreshQueue = [];

/**
 * Спробувати оновити access-токен за допомогою refresh-токена.
 * Повертає новий access-токен або null (якщо refresh теж протух).
 */
async function refreshAccessToken() {
    const refreshToken = TokenStorage.getRefreshToken();
    if (!refreshToken) return null;

    try {
        const res = await fetch(ENDPOINTS.REFRESH, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh: refreshToken }),
        });

        if (!res.ok) {
            // Refresh-токен протух — повний logout
            TokenStorage.clear();
            return null;
        }

        const data = await res.json();
        // Сервер повертає новий access + (опційно) новий refresh
        TokenStorage.saveTokens(data.access, data.refresh || refreshToken);
        return data.access;
    } catch {
        TokenStorage.clear();
        return null;
    }
}

/**
 * Основна функція для виконання запитів до API.
 * Автоматично додає Bearer-токен та обробляє 401/400.
 *
 * @param {string}  url       — URL ендпоінта
 * @param {object}  options   — стандартні fetch options (method, body, headers...)
 * @returns {Promise<object>} — розпарсена відповідь або кидає ApiError
 */
async function apiRequest(url, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    // Додаємо токен, якщо є
    const token = TokenStorage.getAccessToken();
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    let response;
    try {
        response = await fetch(url, { ...options, headers });
    } catch (networkError) {
        throw new ApiError(
            0,
            ['Помилка мережі. Перевірте підключення до інтернету.'],
            null,
        );
    }

    // ── 204 No Content (soft delete / cancel) ──
    if (response.status === 204) {
        return null;
    }

    // ── 401 Unauthorized → спроба refresh ──
    if (response.status === 401) {
        // Якщо вже оновлюємо — ставимо запит у чергу
        if (isRefreshing) {
            return new Promise((resolve, reject) => {
                refreshQueue.push({ resolve, reject, url, options });
            });
        }

        isRefreshing = true;
        const newToken = await refreshAccessToken();
        isRefreshing = false;

        if (newToken) {
            // Повторюємо оригінальний запит з новим токеном
            headers['Authorization'] = `Bearer ${newToken}`;
            const retryResponse = await fetch(url, { ...options, headers });

            // Обробляємо чергу запитів, що чекали
            refreshQueue.forEach(({ resolve, reject, url: qUrl, options: qOpts }) => {
                apiRequest(qUrl, qOpts).then(resolve).catch(reject);
            });
            refreshQueue = [];

            if (retryResponse.status === 204) return null;
            if (!retryResponse.ok) {
                const errData = await retryResponse.json().catch(() => null);
                throw new ApiError(retryResponse.status, parseValidationErrors(errData), errData);
            }
            return retryResponse.json();
        }

        // Refresh не вдався — logout
        refreshQueue = [];
        TokenStorage.clear();
        window.location.href = '/login/';
        throw new ApiError(401, ['Сесія закінчилася. Виконайте вхід знову.'], null);
    }

    // ── 400 / 403 / 404 / 5xx — обробка помилок ──
    if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new ApiError(response.status, parseValidationErrors(errorData), errorData);
    }

    // ── Успішна відповідь ──
    return response.json();
}


// ──────────────────────────────────────────────
//  ApiError — структурований об'єкт помилки
// ──────────────────────────────────────────────

class ApiError extends Error {
    /**
     * @param {number}   status   — HTTP-статус
     * @param {string[]} messages — масив людиночитабельних повідомлень
     * @param {object}   raw      — оригінальне тіло відповіді від DRF
     */
    constructor(status, messages, raw) {
        super(messages.join('; '));
        this.name     = 'ApiError';
        this.status   = status;
        this.messages = messages;
        this.raw      = raw;
    }
}


// ──────────────────────────────────────────────
//  4. Аутентифікація
// ──────────────────────────────────────────────

/**
 * Вхід користувача за номером телефону та паролем.
 *
 * @param {string} phone    — номер телефону
 * @param {string} password — пароль
 * @returns {Promise<object>} — { access, refresh, user }
 */
async function login(phone, password) {
    const data = await apiRequest(ENDPOINTS.LOGIN, {
        method: 'POST',
        body: JSON.stringify({ phone, password }),
    });

    TokenStorage.saveTokens(data.access, data.refresh);
    TokenStorage.saveUser(data.user);
    return data;
}

/**
 * Вихід з системи (blacklist refresh-токена на сервері).
 */
async function logout() {
    const refresh = TokenStorage.getRefreshToken();
    try {
        if (refresh) {
            await apiRequest(ENDPOINTS.LOGOUT, {
                method: 'POST',
                body: JSON.stringify({ refresh }),
            });
        }
    } finally {
        TokenStorage.clear();
        window.location.href = '/login/';
    }
}


// ──────────────────────────────────────────────
//  5. Phase 2 — Service Methods
// ──────────────────────────────────────────────

// ── Branches ──

async function fetchBranches() {
    return apiRequest(ENDPOINTS.BRANCHES);
}

async function createBranch(data) {
    return apiRequest(ENDPOINTS.BRANCHES, {
        method: 'POST',
        body: JSON.stringify(data),
    });
}

async function restoreBranch(branchId) {
    return apiRequest(`${ENDPOINTS.BRANCHES}${branchId}/restore/`, {
        method: 'POST',
    });
}

// ── Subjects ──

async function fetchSubjects() {
    return apiRequest(ENDPOINTS.SUBJECTS);
}

// ── Groups ──

async function fetchGroups(filters = {}) {
    const params = new URLSearchParams(filters).toString();
    const url = params ? `${ENDPOINTS.GROUPS}?${params}` : ENDPOINTS.GROUPS;
    return apiRequest(url);
}

async function activateGroup(groupId) {
    return apiRequest(`${ENDPOINTS.GROUPS}${groupId}/activate/`, {
        method: 'POST',
    });
}

// ── Subscription Plans ──

async function fetchSubscriptionPlans(filters = {}) {
    const params = new URLSearchParams(filters).toString();
    const url = params ? `${ENDPOINTS.SUBSCRIPTION_PLANS}?${params}` : ENDPOINTS.SUBSCRIPTION_PLANS;
    return apiRequest(url);
}

// ── Lessons ──

/**
 * Отримати список занять з опціональною фільтрацією.
 *
 * @param {object} filters — { group, teacher, status, date, search }
 * @returns {Promise<object[]>} — масив занять
 *
 * Приклади:
 *   fetchLessons()                             — всі заняття
 *   fetchLessons({ status: 'scheduled' })      — лише заплановані
 *   fetchLessons({ date: '2026-05-10' })       — за конкретну дату
 *   fetchLessons({ teacher: 5 })               — заняття конкретного викладача
 */
async function fetchLessons(filters = {}) {
    const params = new URLSearchParams(filters).toString();
    const url = params ? `${ENDPOINTS.LESSONS}?${params}` : ENDPOINTS.LESSONS;
    return apiRequest(url);
}

/**
 * Отримати деталі одного заняття.
 * @param {number} lessonId
 */
async function fetchLesson(lessonId) {
    return apiRequest(`${ENDPOINTS.LESSONS}${lessonId}/`);
}

/**
 * Завершити заняття (scheduled → completed).
 * @param {number} lessonId
 */
async function completeLesson(lessonId) {
    return apiRequest(`${ENDPOINTS.LESSONS}${lessonId}/complete/`, {
        method: 'POST',
    });
}

/**
 * Масова відмітка відвідуваності для заняття.
 *
 * @param {number} lessonId       — ID заняття
 * @param {Array}  attendanceData — масив записів:
 *   [
 *     { student: 1, status: 'present', note: '' },
 *     { student: 2, status: 'absent',  note: 'хвороба' },
 *     { student: 3, status: 'late',    note: '' },
 *   ]
 *
 * @returns {Promise<{ created: [], updated: [], errors: [] }>}
 */
async function markAttendance(lessonId, attendanceData) {
    return apiRequest(`${ENDPOINTS.LESSONS}${lessonId}/mark_attendance/`, {
        method: 'POST',
        body: JSON.stringify({ records: attendanceData }),
    });
}

// ── Attendance (CRUD) ──

async function fetchAttendances(filters = {}) {
    const params = new URLSearchParams(filters).toString();
    const url = params ? `${ENDPOINTS.ATTENDANCES}?${params}` : ENDPOINTS.ATTENDANCES;
    return apiRequest(url);
}

async function updateAttendance(attendanceId, data) {
    return apiRequest(`${ENDPOINTS.ATTENDANCES}${attendanceId}/`, {
        method: 'PATCH',
        body: JSON.stringify(data),
    });
}

// ── Students ──

async function fetchStudents(filters = {}) {
    const params = new URLSearchParams(filters).toString();
    const url = params ? `${ENDPOINTS.STUDENTS}?${params}` : ENDPOINTS.STUDENTS;
    return apiRequest(url);
}


// ──────────────────────────────────────────────
//  6. UI Helpers
// ──────────────────────────────────────────────

/**
 * Відображає масив помилок ApiError у вказаному DOM-контейнері.
 * Якщо контейнер не вказано — показує alert.
 *
 * @param {ApiError} error        — об'єкт помилки
 * @param {string}   containerId  — ID DOM-елемента для відображення
 */
function showErrors(error, containerId = null) {
    const messages = error instanceof ApiError ? error.messages : [String(error)];

    if (containerId) {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = messages
                .map((msg) => `<li class="error-message">${msg}</li>`)
                .join('');
            container.style.display = 'block';
            return;
        }
    }

    // Fallback: alert
    alert(messages.join('\n'));
}

/**
 * Очищає контейнер помилок.
 * @param {string} containerId — ID DOM-елемента
 */
function clearErrors(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = '';
        container.style.display = 'none';
    }
}
