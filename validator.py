import re
import logging

logger = logging.getLogger("registration.validator")

BLACKLIST = ["admin", "root", "user", "test", "guest",
    "administrator", "superuser", "moderator",
    "support", "system"]

PHONE_RE = re.compile(r"^\+\d-\d{3}-\d{3}-\d{4}$")
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
STRING_RE = re.compile(r"^[A-Za-z0-9_]{5,}$")
PASSWORD_ALLOWED_RE = re.compile(
    r"^[А-Яа-яЁё0-9!@#$%^&*()_\-+=\[\]{};:'\",.<>/?\\|`~№]+$"
)


def validate_login(login: str) -> tuple[bool, str]:
    logger.debug(f"Начало валидации логина: login='{login}', длина={len(login)}")

    if not login:
        logger.warning("Валидация логина провалена: пустое значение")
        return False, "Логин не может быть пустым"

    if login.startswith("+") or PHONE_RE.match(login):
        logger.debug("Определён тип логина: телефон")
        if not PHONE_RE.match(login):
            logger.warning(f"Валидация логина провалена: неверный формат телефона '{login}'")
            return False, "Неверный формат телефона (ожидается +x-xxx-xxx-xxxx)"
        normalized = login
    elif "@" in login:
        logger.debug("Определён тип логина: email")
        if not EMAIL_RE.match(login):
            logger.warning(f"Валидация логина провалена: неверный формат email '{login}'")
            return False, "Неверный формат email"
        normalized = login
    else:
        logger.debug("Определён тип логина: обычная строка")
        if not STRING_RE.match(login):
            logger.warning(
                f"Валидация логина провалена: строка '{login}' не соответствует "
                f"маске (мин. 5 символов, латиница/цифры/_)"
            )
            return False, (
                "Логин-строка должен содержать минимум 5 символов, "
                "только латиницу, цифры и знак подчёркивания"
            )
        normalized = login

    # Проверка чёрного списка (как подстрока)
    login_lower = normalized.lower()
    for restricted_word in BLACKLIST:
        if restricted_word in login_lower:
            logger.warning(
                f"Валидация логина провалена: найден запрещённый фрагмент "
                f"'{restricted_word}' в логине '{normalized}'"
            )
            return False,"логин не успешен"
        else: return True,"логин успешен"


def validate_password(password: str, confirm: str) -> tuple[bool, str]:
    """Возвращает (успех, сообщение)."""
    logger.debug(
        f"Начало валидации пароля: длина={len(password)}, "
        f"длина подтверждения={len(confirm)}"
    )

    if not password:
        logger.warning("Валидация пароля провалена: пустое значение")
        return False, "Пароль не может быть пустым"

    if len(password) < 7:
        logger.warning(f"Валидация пароля провалена: длина {len(password)} < 7")
        return False, "Пароль должен содержать минимум 7 символов"

    logger.debug("Проверка допустимых символов пароля")
    if not PASSWORD_ALLOWED_RE.match(password):
        logger.warning("Валидация пароля провалена: содержит недопустимые символы")
        return False, (
            "Пароль может содержать только кириллицу, цифры и спецсимволы"
        )

    logger.debug("Проверка наличия заглавной буквы")
    if not re.search(r"[А-ЯЁ]", password):
        logger.warning("Валидация пароля провалена: нет заглавной буквы")
        return False, "Пароль должен содержать хотя бы одну заглавную букву"

    logger.debug("Проверка наличия строчной буквы")
    if not re.search(r"[а-яё]", password):
        logger.warning("Валидация пароля провалена: нет строчной буквы")
        return False, "Пароль должен содержать хотя бы одну строчную букву"

    logger.debug("Проверка наличия цифры")
    if not re.search(r"\d", password):
        logger.warning("Валидация пароля провалена: нет цифры")
        return False, "Пароль должен содержать хотя бы одну цифру"

    logger.debug("Проверка наличия спецсимвола")
    if not re.search(r"[!@#$%^&*()_\-+=\[\]{};:'\",.<>/?\\|`~№]", password):
        logger.warning("Валидация пароля провалена: нет спецсимвола")
        return False, "Пароль должен содержать хотя бы один спецсимвол"

    logger.debug("Проверка совпадения пароля и подтверждения")
    if password != confirm:
        logger.warning("Валидация пароля провалена: пароль и подтверждение не совпадают")
        return False, "Пароль и подтверждение пароля не совпадают"

    logger.debug("Пароль успешно прошёл все проверки")
    return True, ""


def validate_credentials(login: str, password: str, confirm: str) -> tuple[bool, str]:
    """Полная валидация учётных данных."""
    logger.info("Запуск комплексной валидации учётных данных")

    ok, msg = validate_login(login)
    if not ok:
        logger.info(f"Комплексная валидация завершена с ошибкой: {msg}")
        return False, msg

    ok, msg = validate_password(password, confirm)
    if not ok:
        logger.info(f"Комплексная валидация завершена с ошибкой: {msg}")
        return False, msg

    logger.info("Комплексная валидация успешно завершена")
    return True, ""