import prompt
from prettytable import PrettyTable

from primitive_db import core
from primitive_db.constants import DATA_COMMANDS, HELP_TEXT, META_FILE, TABLE_COMMANDS
from primitive_db.parser import parse_command, parse_data_command
from primitive_db.utils import (
    delete_table_file,
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


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
            return True
    elif command == "drop_table":
        if len(args) != 1:
            raise ValueError("Укажите имя одной таблицы.")
        table_name = args[0]
        updated = core.drop_table(metadata, table_name)
        if updated is not None:
            delete_table_file(table_name)
            save_metadata(META_FILE, updated)
            print(f'Таблица "{table_name}" успешно удалена.')
            return True
    return False


def print_rows(schema, rows):
    """Печатает выборку с заголовками из схемы, даже если строк нет."""
    table = PrettyTable()
    table.field_names = list(schema)
    for row in rows:
        table.add_row([row[name] for name in schema])
    print(table)


def run_data_command(command, args, metadata):
    """Загружает данные, выполняет CRUD и сохраняет успешные изменения."""
    parsed = parse_data_command(command, args)
    table_name = parsed["table_name"]
    if not core.table_exists(metadata, table_name):
        return False
    schema = metadata[table_name]
    data = load_table_data(table_name)
    if command == "info":
        print(f"Таблица: {table_name}")
        print(
            "Столбцы: " + ", ".join(f"{name}:{kind}" for name, kind in schema.items())
        )
        print(f"Количество записей: {len(data)}")
        return False
    if command == "insert":
        updated = core.insert(metadata, table_name, data, parsed["values"])
        if updated is None:
            return False
        save_table_data(table_name, updated)
        record_id = updated[-1]["ID"]
        print(f'Запись с ID={record_id} успешно добавлена в таблицу "{table_name}".')
        return True
    where = parsed["where"]
    core.validate_fields(schema, where or {})
    if command == "select":
        rows = core.select(data, where)
        if rows is not None:
            print_rows(schema, rows)
        return False
    if command == "update":
        core.validate_fields(schema, parsed["set"], allow_id=False)
    affected = core.select(data, where)
    if affected is None:
        return False
    if not affected:
        print("Записи не найдены.")
        return False
    if command == "update":
        updated = core.update(data, parsed["set"], where)
    else:
        updated = core.delete(data, where)
    if updated is None:
        return False
    save_table_data(table_name, updated)
    for row in affected:
        if command == "update":
            print(
                f'Запись с ID={row["ID"]} в таблице "{table_name}" успешно обновлена.'
            )
        else:
            print(f'Запись с ID={row["ID"]} успешно удалена из таблицы "{table_name}".')
    return True


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
            if command in ("help", "exit"):
                if args:
                    raise ValueError(f"У {command} нет аргументов.")
                if command == "exit":
                    break
                print_help()
            elif command in TABLE_COMMANDS:
                run_table_command(command, args, load_metadata(META_FILE))
            elif command in DATA_COMMANDS:
                run_data_command(command, args, load_metadata(META_FILE))
            elif command:
                print(f"Функции {command} нет. Попробуйте снова.")
        except (ValueError, KeyError, OSError) as error:
            print(error)
