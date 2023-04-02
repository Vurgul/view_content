from sqlalchemy import Column, ForeignKey, Integer, MetaData, String, Table

metadata = MetaData()

images = Table(
    'images',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('url', String, nullable=False),
    Column('shows', Integer, nullable=False),
    comment='Картинки'
)

categories = Table(
    'categories',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String, nullable=False),
    comment='Категории'
)

image_category_relations = Table(
    'image_category_relations',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('image_id', ForeignKey('images.id')),
    Column('category_id', ForeignKey('categories.id')),
    comment='Таблица связей картинок и категорий'
)
