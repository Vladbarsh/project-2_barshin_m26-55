import json
import shlex


def tokenize(text):
    """Отделяет знаки команды, сохраняя строки вместе с кавычками."""
    tokens = []
    index = 0
    while index < len(text):
        char = text[index]
        if char.isspace():
            index += 1
            continue
        start = index
        if char in "(),=":
            index += 1
        elif char in "\"'":
            quote = char
            index += 1
            while index < len(text) and text[index] != quote:
                if text[index] == "\\" and quote == '"':
                    index += 1
                index += 1
            if index >= len(text):
                raise ValueError("Не закрыты кавычки в строке.")
            index += 1
        else:
            while index < len(text):
                if text[index].isspace() or text[index] in "(),=\"'":
                    break
                index += 1
        tokens.append(text[start:index])
    return tokens


def parse_command(text):
    """Разделяет команду и аргументы, не теряя тип строковых значений."""
    parts = tokenize(text)
    if not parts:
        return "", []
    return parts[0].lower(), parts[1:]


def parse_value(token):
    """Преобразует одно значение в str, int или bool."""
    if token.startswith('"'):
        return json.loads(token)
    if token.startswith("'"):
        return shlex.split(token)[0]
    if token.lower() in ("true", "false"):
        return token.lower() == "true"
    try:
        return int(token)
    except ValueError:
        raise ValueError(
            f"Некорректное значение: {token}. Попробуйте снова. "
            "Строки заключайте в кавычки."
        ) from None


def parse_values(tokens):
    """Разбирает список значений в круглых скобках."""
    if len(tokens) < 2 or tokens[0] != "(" or tokens[-1] != ")":
        raise ValueError("После values нужны значения в круглых скобках.")
    items = tokens[1:-1]
    if not items:
        return []
    if len(items) % 2 == 0 or any(token != "," for token in items[1::2]):
        raise ValueError("Разделяйте значения запятыми.")
    return [parse_value(token) for token in items[::2]]


def parse_where(tokens):
    """Разбирает одно условие вида age = 28."""
    if len(tokens) != 3 or tokens[1] != "=":
        raise ValueError("Условие задаётся в виде <столбец> = <значение>.")
    return {tokens[0]: parse_value(tokens[2])}


def parse_set(tokens):
    """Разбирает присваивания в set, разделённые запятыми."""
    if not tokens or len(tokens) % 4 != 3:
        raise ValueError("После set укажите <столбец> = <значение>.")
    values = {}
    for index in range(0, len(tokens), 4):
        if index and tokens[index - 1] != ",":
            raise ValueError("Разделяйте присваивания запятыми.")
        assignment = parse_where(tokens[index : index + 3])
        name = tokens[index]
        if name in values:
            raise ValueError(f"Столбец {name} указан повторно.")
        values.update(assignment)
    return values


def parse_data_command(command, args):
    """Возвращает имя таблицы и разобранные части CRUD-команды."""
    if command == "info" and len(args) == 1:
        return {"table_name": args[0]}
    if command == "insert" and len(args) >= 5:
        if args[0].lower() == "into" and args[2].lower() == "values":
            return {"table_name": args[1], "values": parse_values(args[3:])}
    if command in ("select", "delete") and len(args) >= 2:
        if args[0].lower() == "from":
            where = None
            if len(args) > 2:
                if args[2].lower() != "where":
                    raise ValueError("После имени таблицы ожидается where.")
                where = parse_where(args[3:])
            if command == "delete" and where is None:
                raise ValueError("Для delete нужно условие where.")
            return {"table_name": args[1], "where": where}
    if command == "update" and len(args) >= 9 and args[1].lower() == "set":
        where_index = next(
            (
                index
                for index in range(5, len(args))
                if args[index].lower() == "where" and args[index - 1] not in (",", "=")
            ),
            None,
        )
        if where_index is not None:
            return {
                "table_name": args[0],
                "set": parse_set(args[2:where_index]),
                "where": parse_where(args[where_index + 1 :]),
            }
    raise ValueError("Некорректная команда. Посмотрите примеры в help.")
