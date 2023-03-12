from bookkeeper.repository.sqlite_repository import SQLiteRepository
from bookkeeper.models.category import Category
import pytest

repo = SQLiteRepository('test.db', Category)


def test_crud():
    """ add """
    obj1 = Category('еда', 4)
    obj2 = Category('вино', 6)
    obj3 = Category('пластинки', 1)
    pk = repo.add(obj1)
    repo.add(obj2)
    repo.add(obj3)
    assert str(obj1.name) == 'еда'
    assert obj1.parent == 4

    """ get """
    obj_get: Category = repo.get(pk)
    assert str(obj1.name) == str(obj_get.name)
    assert str(obj1.parent) == str(obj_get.parent)
    assert str(obj1.pk) == str(obj_get.pk)

    """ update """
    obj2 = Category('мясо', 2)
    obj2.pk = pk
    repo.update(obj2)
    obj_get: Category = repo.get(pk)
    obj_test: Category = Category('мясо', 2)
    obj_test.pk = pk
    assert str(obj_get.name) == str(obj_test.name)
    assert str(obj_get.parent) == str(obj_test.parent)
    assert str(obj_get.parent) == str(obj_test.parent)

    """ delete """
    repo.delete(pk)
    assert repo.get(pk) is None


def test_cannot_add_with_pk():
    obj = Category('книги', 3)
    obj.pk = 1
    with pytest.raises(ValueError):
        repo.add(obj)


def test_cannot_add_without_pk():
    with pytest.raises(ValueError):
        repo.add(12)


def test_cannot_delete_unexistent():
    with pytest.raises(KeyError):
        repo.delete(150)


def test_cannot_update_without_pk():
    obj = Category('лекарства', 13)
    with pytest.raises(ValueError):
        repo.update(obj)
