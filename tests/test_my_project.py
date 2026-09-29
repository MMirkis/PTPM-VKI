import unittest

from src.validator import (
    validate_login,
    validate_password,
    validate_credentials,
)
from src.logger_confi import mask_password


# ============ ТЕСТЫ ЛОГИНА ============

class TestValidateLogin(unittest.TestCase):

    def test_login_accepts_valid_alphanumeric_string(self):
        ok, msg = validate_login("ivan_99")
        self.assertTrue(ok, f"Ожидался успех, получено: {msg}")
        self.assertEqual(msg, "")

    def test_login_rejects_empty_string(self):
        ok, msg = validate_login("")
        self.assertFalse(ok)
        self.assertEqual(msg, "Логин не может быть пустым")

    def test_login_rejects_string_shorter_than_five_chars(self):
        ok, msg = validate_login("ab12")
        self.assertFalse(ok)
        self.assertIn("минимум 5 символов", msg)

    def test_login_rejects_string_with_cyrillic(self):
        ok, msg = validate_login("иван_99")
        self.assertFalse(ok)
        self.assertIn("латиницу", msg)

    def test_login_rejects_string_with_special_chars(self):
        ok, msg = validate_login("ivan-99")
        self.assertFalse(ok)
        self.assertIn("латиницу", msg)

    def test_login_accepts_valid_phone(self):
        ok, msg = validate_login("+7-495-123-4567")
        self.assertTrue(ok, f"Ожидался успех, получено: {msg}")

    def test_login_rejects_invalid_phone_format(self):
        ok, msg = validate_login("+7-495-12345")
        self.assertFalse(ok)
        self.assertIn("телефон", msg.lower())

    def test_login_accepts_valid_email(self):
        ok, msg = validate_login("user@example.com")
        self.assertTrue(ok, f"Ожидался успех, получено: {msg}")

    def test_login_rejects_invalid_email_without_at(self):
        ok, msg = validate_login("user.example.com")
        self.assertFalse(ok)

    def test_login_rejects_blacklisted_admin(self):
        ok, msg = validate_login("admin")
        self.assertFalse(ok)
        self.assertIn("чёрном списке", msg)

    def test_login_rejects_blacklisted_root_in_uppercase(self):
        ok, msg = validate_login("ROOT")
        self.assertFalse(ok)
        self.assertIn("чёрном списке", msg)

    def test_login_rejects_blacklisted_user(self):
        ok, msg = validate_login("user")
        self.assertFalse(ok)


# ============ ТЕСТЫ ПАРОЛЯ ============

class TestValidatePassword(unittest.TestCase):

    def test_password_accepts_valid_password(self):
        ok, msg = validate_password("Пароль1!", "Пароль1!")
        self.assertTrue(ok, f"Ожидался успех, получено: {msg}")

    def test_password_rejects_empty(self):
        ok, msg = validate_password("", "")
        self.assertFalse(ok)
        self.assertEqual(msg, "Пароль не может быть пустым")

    def test_password_rejects_too_short(self):
        ok, msg = validate_password("Пар1!", "Пар1!")
        self.assertFalse(ok)
        self.assertIn("минимум 7 символов", msg)

    def test_password_rejects_without_uppercase(self):
        ok, msg = validate_password("пароль1!", "пароль1!")
        self.assertFalse(ok)
        self.assertIn("заглавную", msg)

    def test_password_rejects_without_lowercase(self):
        ok, msg = validate_password("ПАРОЛЬ1!", "ПАРОЛЬ1!")
        self.assertFalse(ok)
        self.assertIn("строчную", msg)

    def test_password_rejects_without_digit(self):
        ok, msg = validate_password("Пароль!!", "Пароль!!")
        self.assertFalse(ok)
        self.assertIn("цифру", msg)

    def test_password_rejects_without_special_char(self):
        ok, msg = validate_password("Пароль12", "Пароль12")
        self.assertFalse(ok)
        self.assertIn("спецсимвол", msg)

    def test_password_rejects_latin_letters(self):
        ok, msg = validate_password("Password1!", "Password1!")
        self.assertFalse(ok)
        self.assertIn("кириллицу", msg)

    def test_password_rejects_mismatched_confirmation(self):
        ok, msg = validate_password("Пароль1!", "Пароль2!")
        self.assertFalse(ok)
        self.assertIn("не совпадают", msg)


# ============ ТЕСТЫ КОМПЛЕКСНОЙ ВАЛИДАЦИИ ============

class TestValidateCredentials(unittest.TestCase):

    def test_credentials_accepts_valid_pair(self):
        ok, msg = validate_credentials("ivan_99", "Пароль1!", "Пароль1!")
        self.assertTrue(ok, f"Ожидался успех, получено: {msg}")
        self.assertEqual(msg, "")

    def test_credentials_rejects_when_login_invalid(self):
        ok, msg = validate_credentials("ab", "Пароль1!", "Пароль1!")
        self.assertFalse(ok)
        self.assertIn("минимум 5 символов", msg)

    def test_credentials_rejects_when_password_invalid(self):
        ok, msg = validate_credentials("ivan_99", "short", "short")
        self.assertFalse(ok)
        self.assertIn("минимум 7 символов", msg)


# ============ ТЕСТЫ МАСКИРОВАНИЯ ============

class TestMaskPassword(unittest.TestCase):

    def test_mask_returns_same_result_for_same_password(self):
        self.assertEqual(mask_password("Пароль1!"), mask_password("Пароль1!"))

    def test_mask_returns_different_result_for_different_passwords(self):
        self.assertNotEqual(mask_password("Пароль1!"), mask_password("Пароль2!"))

    def test_mask_does_not_contain_original_password(self):
        masked = mask_password("Секрет123!")
        self.assertNotIn("Секрет123!", masked)

    def test_mask_of_empty_password(self):
        self.assertEqual(mask_password(""), "<empty>")


if __name__ == "__main__":
    unittest.main()