import json
import os

from primitive_db.constants import DATA_DIR


def load_metadata(filepath):
    """Читает схемы таблиц; новая база начинается с пустого словаря."""
    try:
        with open(filepath, encoding="utf-8") as file:
            metadata = json.load(file)
    except FileNotFoundError:
        return {}
    if not isinstance(metadata, dict):
        raise ValueError("Неверный формат метаданных.")
    return metadata


def save_metadata(filepath, data):
    """Сохраняет схемы таблиц в JSON."""
    save_json(filepath, data)


def save_json(filepath, data):
    """Заменяет файл только после записи всех данных."""
    temp_path = f"{filepath}.tmp"
    with open(temp_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    os.replace(temp_path, filepath)


def load_table_data(table_name):
    """Возвращает записи таблицы или пустой список до первой вставки."""
    filepath = os.path.join(DATA_DIR, f"{table_name}.json")
    try:
        with open(filepath, encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return []
    if not isinstance(data, list) or any(not isinstance(row, dict) for row in data):
        raise ValueError(f'Неверный формат данных таблицы "{table_name}".')
    return data


def save_table_data(table_name, data):
    """Сохраняет полный список записей таблицы."""
    os.makedirs(DATA_DIR, exist_ok=True)
    save_json(os.path.join(DATA_DIR, f"{table_name}.json"), data)


def delete_table_file(table_name):
    """Удаляет файл таблицы, если в неё уже добавляли записи."""
    filepath = os.path.join(DATA_DIR, f"{table_name}.json")
    try:
        os.remove(filepath)
    except FileNotFoundError:
        pass
