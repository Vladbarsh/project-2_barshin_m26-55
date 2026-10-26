from primitive_db.constants import VALID_TYPES
from primitive_db.decorators import confirm_action, handle_db_errors, log_time


def validate_name(name):
    """Проверяет имя таблицы или столбца до использования в базе."""
    if not name.isidentifier():
        raise ValueError(f"Некорректное имя: {name}.")


def table_exists(metadata, table_name):
    """Проверяет таблицу и сообщает об ожидаемой ошибке."""
    validate_name(table_name)
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return False
    return True


@handle_db_errors
def create_table(metadata, table_name, columns):
    """Создаёт схему таблицы с целочисленным ID в начале."""
    validate_name(table_name)
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return None
    if not columns:
        raise ValueError("Укажите столбцы и их типы.")
    schema = {"ID": "int"}
    names = set()
    for column in columns:
        parts = column.split(":")
        if len(parts) != 2:
            raise ValueError(f"Некорректное значение: {column}. Попробуйте снова.")
        name, data_type = parts
        validate_name(name)
        if data_type not in VALID_TYPES:
            raise ValueError(f"Некорректное значение: {data_type}. Попробуйте снова.")
        if name in names:
            raise ValueError(f"Столбец {name} указан повторно.")
        names.add(name)
        if name == "ID" and data_type != "int":
            raise ValueError("Столбец ID должен иметь тип int.")
        schema[name] = data_type
    return {**metadata, table_name: schema}


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    """Возвращает метаданные без указанной таблицы."""
    if not table_exists(metadata, table_name):
        return None
    return {name: schema for name, schema in metadata.items() if name != table_name}


def validate_fields(schema, fields, allow_id=True):
    """Проверяет названия полей и точное соответствие типов схеме."""
    for name, value in fields.items():
        if name not in schema:
            raise ValueError(f'Ошибка: Столбец "{name}" не существует.')
        if name == "ID" and not allow_id:
            raise ValueError("Изменять ID нельзя.")
        if type(value).__name__ != schema[name]:
            raise ValueError(f"Некорректное значение: {value}. Попробуйте снова.")


@handle_db_errors
@log_time
def insert(metadata, table_name, table_data, values):
    """Проверяет новую запись и возвращает данные с добавленным ID."""
    if not table_exists(metadata, table_name):
        return None
    schema = metadata[table_name]
    columns = [name for name in schema if name != "ID"]
    if len(values) != len(columns):
        raise ValueError(f"Нужно значений: {len(columns)}, получено: {len(values)}.")
    fields = dict(zip(columns, values))
    validate_fields(schema, fields)
    next_id = max((row["ID"] for row in table_data), default=0) + 1
    record = {"ID": next_id, **fields}
    return [row.copy() for row in table_data] + [record]


def matches(row, where_clause):
    """Проверяет условие равенства, различая int и bool."""
    return all(
        name in row and type(row[name]) is type(value) and row[name] == value
        for name, value in where_clause.items()
    )


@handle_db_errors
@log_time
def select(table_data, where_clause=None):
    """Возвращает копии всех записей или записей по условию."""
    return [row.copy() for row in table_data if matches(row, where_clause or {})]


@handle_db_errors
def update(table_data, set_clause, where_clause):
    """Возвращает полную таблицу с изменениями, не трогая исходные записи."""
    return [
        {**row, **set_clause} if matches(row, where_clause) else row.copy()
        for row in table_data
    ]


@handle_db_errors
@confirm_action("удаление записей")
def delete(table_data, where_clause):
    """Возвращает таблицу без подходящих под условие записей."""
    return [row.copy() for row in table_data if not matches(row, where_clause)]
