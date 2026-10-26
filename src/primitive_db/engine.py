import prompt

from primitive_db import core
from primitive_db.constants import HELP_TEXT, META_FILE
from primitive_db.parser import parse_command
from primitive_db.utils import delete_table_file, load_metadata, save_metadata


def print_help():
    """Показывает все доступные команды."""
    print(HELP_TEXT)


def welcome():
    """Показывает справку при старте."""
    print_help()


def run_table_command(command, args, metadata):
    """Выполняет команду управления таблицами."""
    if command == "list_tables":
        if args:
            raise ValueError("У list_tables нет аргументов.")
        for name in metadata:
            print(f"- {name}")
        if not metadata:
            print("Таблиц пока нет.")
    elif command == "create_table":
        if len(args) < 2:
            raise ValueError("Укажите имя таблицы и столбцы.")
        table_name = args[0]
        updated = core.create_table(metadata, table_name, args[1:])
        if updated is not None:
            save_metadata(META_FILE, updated)
            columns = ", ".join(
                f"{name}:{kind}" for name, kind in updated[table_name].items()
            )
            print(f'Таблица "{table_name}" успешно создана со столбцами: {columns}')
    elif command == "drop_table":
        if len(args) != 1:
            raise ValueError("Укажите имя одной таблицы.")
        table_name = args[0]
        updated = core.drop_table(metadata, table_name)
        if updated is not None:
            delete_table_file(table_name)
            save_metadata(META_FILE, updated)
            print(f'Таблица "{table_name}" успешно удалена.')
    else:
        print(f"Функции {command} нет. Попробуйте снова.")


def run():
    """Читает команды до выхода из программы."""
    welcome()
    while True:
        try:
            text = prompt.string("Введите команду: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        try:
            command, args = parse_command(text)
            if command == "exit" and not args:
                break
            if command == "help" and not args:
                print_help()
            elif command:
                run_table_command(command, args, load_metadata(META_FILE))
        except (ValueError, KeyError, OSError) as error:
            print(f"Ошибка: {error}")
