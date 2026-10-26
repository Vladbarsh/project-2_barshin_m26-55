from primitive_db.constants import VALID_TYPES


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


def drop_table(metadata, table_name):
    """Возвращает метаданные без указанной таблицы."""
    if not table_exists(metadata, table_name):
        return None
    return {name: schema for name, schema in metadata.items() if name != table_name}
