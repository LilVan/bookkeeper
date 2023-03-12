"""
Простой тестовый скрипт для терминала
"""

from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense
from bookkeeper.repository.memory_repository import MemoryRepository
from bookkeeper.repository.sqlite_repository import SQLiteRepository
from bookkeeper.utils import read_tree


cat_repo = SQLiteRepository[Category]('test.db', Category)
exp_repo = SQLiteRepository[Category]('test.db', Category)

cats = '''
продукты
    мясо
        сырое мясо
        мясные продукты
    сладости
книги
одежда
'''.splitlines()

#Category.create_from_tree(read_tree(cats), cat_repo)  # TODO: не выполнять при каждом запуске

while True:
    try:
        cmd = input('$> ')
    except EOFError:
        break
    if not cmd:
        continue

    #if cmd == '2':
     #   print(*cat_repo.get(2), sep='\n')

    if cmd == 'категории':
        print(*cat_repo.get_all(), sep='\n')
    elif cmd == 'расходы':
        print(*exp_repo.get_all(), sep='\n')
    elif cmd == 'get':
        print(cat_repo.get(3), sep='\n')
    elif cmd == 'del':
        cat_repo.delete(3)
    elif cmd == 'upd':
        obj2 = Category('Meat', 2)
        obj2.pk = 2
        cat_repo.update(obj2)
    elif cmd == 'cond':
        try:
            print(cat_repo.get_all({'name': 'продукты', 'id': 1}))
        except IndexError:
            print(f'категория продукты не найдена')
            continue
#        exp = Expense(int(amount), cat.pk)
#        exp_repo.add(exp)
#        print(exp)
