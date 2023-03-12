import sqlite3

from inspect import get_annotations
from bookkeeper.repository.abstract_repository import AbstractRepository, T
from typing import Any


def model_make(cls: Any, fields: dict[Any, Any], values: str) -> Any:
    res = object.__new__(cls)
    if values is None:
        return None
    for attr, val in zip(fields.keys(), values[1:3]):
        setattr(res, attr, val)
    setattr(res, 'pk', values[0])
    return res


class SQLiteRepository(AbstractRepository[T]):
    def __init__(self, db_file: str, cls: type) -> None:
        self.cls: type = cls
        self.db_file = db_file
        self.table_name = cls.__name__.lower()
        self.fields = get_annotations(cls, eval_str=True)
        self.fields.pop('pk')

    def add(self, obj: T) -> int:
        names = ', '.join(self.fields.keys())
        p = ', '.join("?" * len(self.fields))
        values = [getattr(obj, x) for x in self.fields]
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute('PRAGMA foreign_keys = ON')
            cur.execute(
                f'INSERT INTO {self.table_name} ({names}) VALUES ({p})',
                values
            )
            obj.pk = cur.lastrowid
        con.close()
        return obj.pk

    def get(self, pk: int) -> T | None:
        """ Получить объект по id """
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute(f"SELECT * FROM {self.table_name} WHERE rowid = {pk}")
            res = model_make(self.cls, self.fields, cur.fetchone())
        con.close()
        return res

    def get_all(self, where: dict[str, Any] | None = None) -> list[T]:
        """
        Получить все записи по некоторому условию
        where - условие в виде словаря {'название_поля': значение}
        если условие не задано (по умолчанию), вернуть все записи
        """
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            if where is None:
                cur.execute(f'SELECT * FROM {self.table_name}')
            else:
                p = []
                for attr, value in where.items():
                    if type(value) == str:
                        value = f"'{value}'"
                    p.append(" = ".join([attr, str(value)]))
                p = " AND ".join(p)
                cur.execute(f"SELECT * FROM {self.table_name} WHERE {p}")
            res = [model_make(self.cls, self.fields, val) for val in cur.fetchall()]
        con.close()
        return res

    def update(self, obj: T) -> None:
        """ Обновить данные об объекте. Объект должен содержать поле pk. """
        pass
    
    def delete(self, pk: int) -> None:
        """ Удалить запись """
        pass


"""
r = SQLiteRepository('test.sqlite', Test)
o = Test('Hello')
r.add(o)
"""