import logging
import sys
from datetime import datetime

from logger_confi import logger, safe_params
from validator import validate_credentials


def input_password(prompt: str = "Пароль: ", show_stars: bool = True) -> str:
    """
    Ввод пароля с маскировкой.
    show_stars=True  — отображает звёздочки (для пароля).
    show_stars=False — не отображает ничего (для подтверждения).
    """
    logger.debug(f"Запрошен ввод пароля: prompt='{prompt}', show_stars={show_stars}")

    if not sys.stdin.isatty():
        logger.debug("Неинтерактивный ввод, используется fallback input()")
        return input(prompt)

    try:
        import msvcrt  #
        use_msvcrt = True
    except ImportError:
        use_msvcrt = False

    if use_msvcrt:
        sys.stdout.write(prompt)
        sys.stdout.flush()
        chars = []
        while True:
            ch = msvcrt.getwch()
            if ch in ("\r", "\n"):
                sys.stdout.write("\n")
                sys.stdout.flush()
                break
            elif ch == "\x08":  # Backspace
                if chars:
                    chars.pop()
                    if show_stars:
                        sys.stdout.write("\b \b")
                        sys.stdout.flush()
            elif ch == "\x03":  # Ctrl+C
                logger.warning("Ввод пароля прерван пользователем (Ctrl+C)")
                raise KeyboardInterrupt
            else:
                chars.append(ch)
                if show_stars:
                    sys.stdout.write("*")
                    sys.stdout.flush()
        return "".join(chars)
    else:
        import termios
        import tty

        sys.stdout.write(prompt)
        sys.stdout.flush()
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        chars = []
        try:
            tty.setraw(fd)
            while True:
                ch = sys.stdin.read(1)
                if ch in ("\r", "\n"):
                    sys.stdout.write("\n")
                    sys.stdout.flush()
                    break
                elif ch == "\x7f":  # Backspace
                    if chars:
                        chars.pop()
                        if show_stars:
                            sys.stdout.write("\b \b")
                            sys.stdout.flush()
                elif ch == "\x03":  # Ctrl+C
                    logger.warning("Ввод пароля прерван пользователем (Ctrl+C)")
                    raise KeyboardInterrupt
                else:
                    chars.append(ch)
                    if show_stars:
                        sys.stdout.write("*")
                        sys.stdout.flush()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return "".join(chars)


def main():

    try:
        import logging.handlers
        if not logging.getLogger().handlers:
            print("CRITICAL: логгер не сконфигурирован", file=sys.stderr)
            sys.exit(1)
    except Exception as ex:
        print(f"CRITICAL: не удалось инициализировать логирование: {ex}", file=sys.stderr)
        sys.exit(1)

    logger.info("=" * 60)
    logger.info("Логгер успешно сконфигурирован")
    logger.info("Приложение запущено")

    login = ""
    password = ""
    confirm = ""
    request_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        logger.debug("Запрос логина у пользователя")
        login = input("Логин: ")
        logger.debug(f"Получен логин: '{login}' (длина={len(login)})")

        logger.debug("Запрос пароля у пользователя (с маскировкой звёздочками)")
        password = input_password("Пароль: ", show_stars=True)
        logger.debug(f"Пароль получен, длина={len(password)}")

        logger.debug("Запрос подтверждения пароля (без отображения символов)")
        confirm = input_password("Подтверждение пароля: ", show_stars=False)
        logger.debug(f"Подтверждение получено, длина={len(confirm)}")


        logger.info(
            f"Обработка запроса регистрации | time={request_time} | "
            f"params={safe_params(login, password, confirm)}"
        )

        success, message = validate_credentials(login, password, confirm)

        if success:

            logger.info(
                f"Успешный запрос | time={request_time} | "
                f"params={safe_params(login, password, confirm)} | "
                f"result=True | message=''"
            )
            print("True")
            print("")
        else:

            logger.warning(
                f"Неуспешный запрос | time={request_time} | "
                f"params={safe_params(login, password, confirm)} | "
                f"result=False | error='{message}'"
            )
            print("False")
            print(message)

    except KeyboardInterrupt:

        logger.critical(
            f"Критическое событие: работа программы прервана пользователем (Ctrl+C) | "
            f"time={request_time}"
        )
        print("False")
        print("Работа программы прервана пользователем")
        sys.exit(130)

    except Exception as ex:

        logger.error(
            f"Неуспешный запрос | time={request_time} | "
            f"params={safe_params(login, password, confirm)} | "
            f"error='{ex}'"
        )
        logger.exception("Заход в блок обработки исключения:")
        print("False")
        print(f"Внутренняя ошибка: {ex}")

    finally:
        logger.info("Приложение завершило работу")
        logger.info("=" * 60)


if __name__ == "__main__":
    main()