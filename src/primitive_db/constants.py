META_FILE = "db_meta.json"
DATA_DIR = "data"
ID_COLUMN = "ID"
ID_TYPE = "int"
VALID_TYPES = ("int", "str", "bool")
TABLE_COMMANDS = ("create_table", "list_tables", "drop_table")
DATA_COMMANDS = ("insert", "select", "update", "delete", "info")

HELP_TEXT = """
***База данных***

create_table <имя_таблицы> <столбец:тип> ... - создать таблицу
list_tables - показать список всех таблиц
drop_table <имя_таблицы> - удалить таблицу
insert into <имя_таблицы> values (<значение1>, ...) - создать запись
select from <имя_таблицы> [where <столбец> = <значение>] - прочитать записи
update <имя_таблицы> set <столбец> = <значение> where <столбец> = <значение>
delete from <имя_таблицы> where <столбец> = <значение> - удалить записи
info <имя_таблицы> - информация о таблице
help - справочная информация
exit - выход из программы
"""
