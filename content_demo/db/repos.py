from typing import List

from dotenv import dotenv_values
from sqlalchemy import and_, create_engine
from sqlalchemy.orm import registry, relationship, sessionmaker
from sqlalchemy.sql import func
from db import table
from models import interface
from models.entity import Category, Image, ImageCategoryRelation


config = dotenv_values('.env')

# TODO: заменить на create_async_engine

engine = create_engine(
    f"postgresql://{config.get('DB_USER')}:{config.get('DB_PASS')}@"
    f"{config.get('DB_HOST')}:{config.get('DB_PORT')}/{config.get('DB_NAME')}",
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


mapper = registry()
mapper.map_imperatively(Image, table.images)
mapper.map_imperatively(Category, table.categories)
mapper.map_imperatively(
    ImageCategoryRelation,
    table.image_category_relations,
    properties={
        'image': relationship(Image, backref='image_id', uselist=False),
        'category': relationship(Category, backref='category_id', uselist=False)
    }
)


class ImageRepo(interface.ImageRepo):

    def get_by_id(self, id_: int) -> Image:
        with SessionLocal() as session:
            image = session.query(Image).where(Image.id == id_).one_or_none()
            return image

    def get_by_url(self, url: str) -> Image:
        with SessionLocal() as session:
            image = session.query(Image).where(Image.url == url).one_or_none()
            return image

    def add(self, url: str, shows: int) -> Image:
        with SessionLocal() as session:
            new_image = self.get_by_url(url)
            if not new_image:
                new_image = Image(url=url, shows=shows)
                session.add(new_image)
                session.commit()
                return self.get_by_url(url)
            return new_image

    def change_shows(self, id_: int):
        with SessionLocal() as session:
            image = session.query(Image).where(Image.id == id_).one_or_none()
            image.shows -= 1
            session.commit()

    def get_random(self) -> Image:
        with SessionLocal() as session:
            image = session.query(
                Image
            ).where(Image.shows != 0).order_by(func.random()).first()
            return image


class CategoryRepo(interface.CategoryRepo):

    def get_by_name(self, name: str) -> Category:
        with SessionLocal() as session:
            category = session.query(Category).where(Category.name == name).one_or_none()
            return category

    def add(self, name: str) -> Category:
        with SessionLocal() as session:
            new_category = self.get_by_name(name)
            if not new_category:
                new_category = Category(name=name)
                session.add(new_category)
                session.commit()
                return self.get_by_name(name)
            return new_category


class ImageCategoryRelationRepo(interface.ImageCategoryRelationRepo):

    def get_by_relation(self, image_id: int, category_id: int) -> ImageCategoryRelation:
        with SessionLocal() as session:
            relation = session.query(ImageCategoryRelation).where(
                and_(
                    ImageCategoryRelation.image_id == image_id,
                    ImageCategoryRelation.category_id == category_id
                )
            ).one_or_none()
            return relation

    def get_by_category_id(self, category_id: int) -> List[ImageCategoryRelation]:
        with SessionLocal() as session:
            relation = session.query(ImageCategoryRelation).where(
                ImageCategoryRelation.category_id == category_id
            ).all()
            return relation

    def add(self, image_id: int, category_id: int):
        with SessionLocal() as session:
            if not self.get_by_relation(image_id, category_id):
                new_relation = ImageCategoryRelation(
                    image_id=image_id,
                    category_id=category_id
                )
                session.add(new_relation)
                session.commit()
