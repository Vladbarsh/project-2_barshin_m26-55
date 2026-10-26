# Примитивная база данных

Баршин Владислав, М26-55. Домашнее задание №2 по Python.

Консольная программа для создания таблиц и работы с записями. Данные сохраняются в JSON.

## Запуск

Нужны Python 3.12 и uv.

```console
git clone https://github.com/Vladbarsh/project-2_barshin_m26-55.git
cd project-2_barshin_m26-55
uv sync --locked
uv run database
```

Команда `uv run project` запускает ту же программу.

## Пример работы

```text
create_table users name:str age:int is_active:bool
list_tables
insert into users values ("Sergei", 28, true)
select from users where age = 28
update users set age = 29 where name = "Sergei"
delete from users where ID = 1
y
info users
drop_table users
y
```

Типы столбцов: `int`, `str`, `bool`. Поле `ID:int` добавляется автоматически и не изменяется.
Строки пишутся в кавычках, числа — без кавычек, логические значения — `true` или `false`.
Все поля обязательны; ID при вставке не передаётся.

В `where` поддерживается равенство. Изменяются или удаляются все подходящие записи.
Удаление требует ответа `y`, любой другой ответ отменяет операцию.
Команды `help` и `exit` — справка и выход. После ошибки ввода можно продолжить работу.

Схемы хранятся в `db_meta.json`, записи — в `data/`. Для работы с одной базой
запускайте программу из одной папки. Повторный `select` использует кэш,
который сбрасывается после изменения данных. Для `insert` и вычисления `select`
выводится время выполнения.

## Проверка и сборка

```powershell
uv run ruff check .
uv build
Get-ChildItem -Path dist/*.whl, dist/*.tar.gz |
    ForEach-Object { uvx twine check $_.FullName }
```

В Makefile есть `install`, `run`, `lint`, `build`, `publish`.
Команда `publish` собирает пакет и проверяет метаданные без загрузки на PyPI.

## Демонстрация

[![Демонстрация работы базы данных](https://asciinema.org/a/BFKggj0H3eIx1jkz.svg)](https://asciinema.org/a/BFKggj0H3eIx1jkz)
