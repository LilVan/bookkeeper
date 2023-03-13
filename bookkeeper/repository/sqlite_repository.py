import sqlite3

from inspect import get_annotations
from bookkeeper.repository.abstract_repository import AbstractRepository, T
from typing import Any


def model_make(cls: Any, fields: dict[Any, Any], values: str) -> Any:
    res = object.__new__(cls)
    if values is None:
        return None
    for attr, val in zip(fields.keys(), values[1:]):
        setattr(res, attr, val)
    setattr(res, 'pk', values[0])
    return res


class SQLiteRepository(AbstractRepository[T]):
    def __init__(self, db_file: str, cls: type) -> None:
        self.db_file = db_file
        self.table_name = cls.__name__.lower()
        self.cls = cls
        self.fields = get_annotations(cls, eval_str=True)
        self.fields.pop('pk')
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            res = cur.execute('SELECT name FROM sqlite_master')
            db_tables = [t[0].lower() for t in res.fetchall()]
            if self.table_name not in db_tables:
                col_names = ', '.join(self.fields.keys())
                q = f'CREATE TABLE {self.table_name} (' \
                    f'"pk" INTEGER PRIMARY KEY AUTOINCREMENT, {col_names})'
                cur.execute(q)
        con.close()

    def add(self, obj: T) -> int:
        if getattr(obj, 'pk', None) != 0:
            raise ValueError(f'trying to add object {obj} with filled `pk` attribute')
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

    def update(self, obj: T) -> T:
        """ Обновить данные об объекте. Объект должен содержать поле pk. """
        if not hasattr(obj, 'pk'):
            raise ValueError(f'The object must contain the pk field')
        if obj.pk == 0:
            raise ValueError('attempt to update object with unknown primary key')
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            p = []
            for attr, value in dict(zip(self.fields, [getattr(obj, f) for f in self.fields])).items():
                if type(value) == str:
                    value = f"'{value}'"
                p.append(" = ".join([attr, str(value)]))
            p = ", ".join(p)
            cur.execute(f"UPDATE {self.table_name} SET {p} WHERE pk = {getattr(obj, 'pk')}")
            con.commit()
        con.close()
        return obj

    def delete(self, pk: int) -> None:
        """ Удалить запись """
        with sqlite3.connect(self.db_file) as con:
            if self.count(con.cursor(), pk) == 0:
                raise KeyError(f'No row with pk = {pk}')
            cur = con.cursor()
            cur.execute(f'DELETE FROM {self.table_name} WHERE rowid = {pk}')
        con.close()

    def count(self, cur: Any, pk: int) -> int:
        """ Считает, сколько объектов с данным pk"""
        res = cur.execute(f'SELECT count(*) FROM {self.table_name} WHERE pk = {pk}').fetchone()
        return res[0]


"""
r = SQLiteRepository('test.sqlite', Test)
o = Test('Hello')
r.add(o)
"""