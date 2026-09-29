import logging
import sys
import os
import hashlib

# Создаём папку Logs, если её нет
os.makedirs("../Logs", exist_ok=True)

log_format = "%(asctime)s | [%(levelname)-8s] | %(name)s | %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"

logging.basicConfig(
    level=logging.DEBUG,
    format=log_format,
    datefmt=date_format,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("../Logs/file_txt.log", encoding="utf-8"),
    ],
)

logger = logging.getLogger("registration")


def mask_password(password: str) -> str:
    """
    Маскирование пароля.
    Одинаковый результат для совпадающих паролей, разный — для отличающихся.
    SHA-256 + первые 12 символов хеша.
    """
    if not password:
        return "<empty>"
    digest = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return f"***{digest[:12]}***"


def safe_params(login: str, password: str, confirm: str) -> dict:
    """Возвращает словарь параметров запроса с замаскированными паролями."""
    return {
        "login": login,
        "password": mask_password(password),
        "confirm": mask_password(confirm),
    }