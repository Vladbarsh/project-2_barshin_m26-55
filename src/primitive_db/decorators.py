import time

import prompt


def copy_details(wrapper, func):
    """Сохраняет имя и описание функции у её обёртки."""
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    wrapper.__wrapped__ = func
    return wrapper


def handle_db_errors(func):
    """Сообщает об ошибке операции, позволяя продолжить работу."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(
                "Ошибка: Файл данных не найден. "
                "Возможно, база данных не инициализирована."
            )
        except KeyError as error:
            print(f"Ошибка: Таблица или столбец {error.args[0]} не найден.")
        except ValueError as error:
            print(error)
        except Exception as error:
            print(f"Произошла непредвиденная ошибка: {error}")
        return None

    return copy_details(wrapper, func)


def confirm_action(action_name):
    """Запрашивает подтверждение перед удалением."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                answer = prompt.string(
                    f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: ',
                    empty=True,
                )
            except (EOFError, KeyboardInterrupt):
                answer = "n"
                print()
            if answer.strip().lower() != "y":
                print("Операция отменена.")
                return None
            return func(*args, **kwargs)

        return copy_details(wrapper, func)

    return decorator


def log_time(func):
    """Печатает время выполнения операции в секундах."""

    def wrapper(*args, **kwargs):
        start = time.monotonic()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed = time.monotonic() - start
            print(f"Функция {func.__name__} выполнилась за {elapsed:.3f} секунд.")

    return copy_details(wrapper, func)


def create_cacher():
    """Создаёт отдельный кэш для повторяющихся выборок."""
    cache = {}

    def cache_result(key, value_func):
        if key not in cache:
            result = value_func()
            if result is None:
                return None
            cache[key] = result
        return cache[key]

    return cache_result
