from typing import List

from dotenv import dotenv_values
from pydantic import validate_arguments
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import registry, relationship
from sqlalchemy.sql import func

from db import table
from models import interface
from models.entity import Category, Image, ImageCategoryRelation

config = dotenv_values('.env')

# TODO: заменить на create_async_engine
DB_ULR = f"postgresql+asyncpg://{config.get('DB_USER')}:{config.get('DB_PASS')}@" \
         f"{config.get('DB_HOST')}:{config.get('DB_PORT')}/{config.get('DB_NAME')}"

engine = create_async_engine(DB_ULR)

async_session = async_sessionmaker(engine, expire_on_commit=False)


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

    @validate_arguments
    async def get_by_id(self, id_: int) -> Image:
        async with async_session() as session:
            request = select(Image).where(Image.id == id_)
            result = await session.execute(request)
            image = result.scalars().one_or_none()
            return image

    @validate_arguments
    async def get_by_url(self, url: str) -> Image:
        async with async_session() as session:
            request = select(Image).where(Image.url == url)
            result = await session.execute(request)
            image = result.scalars().one_or_none()
            return image

    @validate_arguments
    async def add(self, url: str, shows: int) -> Image:
        async with async_session() as session:
            new_image = await self.get_by_url(url)
            if not new_image:
                new_image = Image(url=url, shows=shows)
                session.add(new_image)
                await session.commit()
                image = await self.get_by_url(url)
                return image
            return new_image

    @validate_arguments
    async def change_shows(self, id_: int):
        async with async_session() as session:
            request = select(Image).where(Image.id == id_)
            result = await session.execute(request)
            image = result.scalars().one_or_none()
            image.shows -= 1
            await session.commit()

    @validate_arguments
    async def get_random(self) -> Image:
        async with async_session() as session:
            request = select(Image).where(Image.shows != 0).order_by(func.random())
            result = await session.execute(request)
            image = result.scalars().first()
            return image


class CategoryRepo(interface.CategoryRepo):

    @validate_arguments
    async def get_by_name(self, name: str) -> Category:
        async with async_session() as session:
            request = select(Category).where(Category.name == name)
            result = await session.execute(request)
            category = result.scalars().one_or_none()
            return category

    @validate_arguments
    async def add(self, name: str) -> Category:
        async with async_session() as session:
            new_category = await self.get_by_name(name)
            if not new_category:
                new_category = Category(name=name)
                session.add(new_category)
                await session.commit()
                new_category = await self.get_by_name(name)
                return new_category
            return new_category


class ImageCategoryRelationRepo(interface.ImageCategoryRelationRepo):

    @validate_arguments
    async def get_by_relation(
            self,
            image_id: int,
            category_id: int
    ) -> ImageCategoryRelation:
        async with async_session() as session:
            request = select(ImageCategoryRelation).where(
                and_(
                    ImageCategoryRelation.image_id == image_id,
                    ImageCategoryRelation.category_id == category_id
                )
            )
            result = await session.execute(request)
            relation = result.scalars().one_or_none()
            return relation

    @validate_arguments
    async def get_by_category_id(self, category_id: int) -> List[ImageCategoryRelation]:
        async with async_session() as session:
            request = select(ImageCategoryRelation).where(
                ImageCategoryRelation.category_id == category_id
            )
            result = await session.execute(request)
            relation = result.scalars().all()
            return relation

    @validate_arguments
    async def add(self, image_id: int, category_id: int):
        async with async_session() as session:
            if not await self.get_by_relation(image_id, category_id):
                new_relation = ImageCategoryRelation(
                    image_id=image_id,
                    category_id=category_id
                )
                session.add(new_relation)
                await session.commit()
