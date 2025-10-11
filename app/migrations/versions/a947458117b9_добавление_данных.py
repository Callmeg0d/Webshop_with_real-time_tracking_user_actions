"""Добавление данных

Revision ID: a947458117b9
Revises: 04aaa7a8bf76
Create Date: 2025-03-14 20:49:27.820245

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a947458117b9'
down_revision: Union[str, None] = '04aaa7a8bf76'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Добавляем категории товаров
    op.execute("""
        INSERT INTO categories (category_name) VALUES
        ('Телефоны'),
        ('Ноутбуки'),
        ('Планшеты'),
        ('Наушники'),
        ('Фитнес-трекеры'),
        ('Фотоаппараты');
    """)

    # Добавляем продукты
    op.execute("""
        INSERT INTO products (name, description, price, product_quantity, features, category_name) VALUES
        ('iPhone 13', 'Новый смартфон от Apple с A15 Bionic и 128 ГБ памяти.', 79990, 10, '{"Память": "128 ГБ", "Вес": "173 г", "Размеры": "146.7 x 71.5 x 7.65 мм"}', 'Телефоны'),
        ('Samsung Galaxy S22', 'Мощный смартфон с камерой 108 Мп и Snapdragon 8 Gen 2.', 84990, 8, '{"Память": "256 ГБ", "Вес": "175 г", "Размеры": "151.7 x 71.2 x 7.9 мм"}', 'Телефоны'),
        ('MacBook Pro 2021', 'Новый ноутбук с M1 Pro и 14-дюймовым экраном.', 139990, 5, '{"Память": "512 ГБ SSD", "Вес": "1.4 кг", "Размеры": "355 x 248 x 16.8 мм"}', 'Ноутбуки'),
        ('Dell XPS 15', 'Мощный ноутбук с 11-м поколением процессора Intel Core.', 109990, 7, '{"Память": "1 ТБ SSD", "Вес": "1.83 кг", "Размеры": "344.72 x 230.14 x 18 мм"}', 'Ноутбуки'),
        ('iPad Air', 'Планшет с 10.9-дюймовым Liquid Retina дисплеем.', 52990, 12, '{"Память": "256 ГБ", "Вес": "458 г", "Размеры": "247.6 x 178.5 x 6.1 мм"}', 'Планшеты'),
        ('Samsung Galaxy Tab S7', 'Планшет с AMOLED-экраном и поддержкой S Pen.', 49990, 9, '{"Память": "128 ГБ", "Вес": "500 г", "Размеры": "253.8 x 165.3 x 6.3 мм"}', 'Планшеты'),
        ('AirPods Pro', 'Беспроводные наушники с функцией активного шумоподавления.', 21990, 15, '{"Вес": "5.4 г (каждая наушника)", "Размеры": "30.9 x 21.8 x 24 мм (каждая наушника)"}', 'Наушники'),
        ('Sony WH-1000XM4', 'Шумоподавляющие наушники с поддержкой LDAC и DSEE Extreme.', 31990, 10, '{"Вес": "254 г", "Размеры": "170 x 200 x 83 мм"}', 'Наушники'),
        ('Fitbit Charge 5', 'Умный фитнес-трекер с функцией отслеживания сна и стресса.', 14990, 20, '{"Вес": "30 г", "Размеры": "36.4 x 22.7 x 11.5 мм"}', 'Фитнес-трекеры'),
        ('Garmin Forerunner 945', 'GPS-часы с функцией измерения VO2 max и пульса на запястье.', 59990, 8, '{"Вес": "50.5 г", "Размеры": "47 x 47 x 13.7 мм"}', 'Фитнес-трекеры');
    """)

    # ### end Alembic commands ###


def downgrade():
    # Удаляем добавленные записи
    op.execute("DELETE FROM products;")
    op.execute("DELETE FROM categories;")
    # ### end Alembic commands ###
