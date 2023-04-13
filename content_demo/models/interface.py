from abc import ABC, abstractmethod
from typing import List

from models.entity import Category, Image, ImageCategoryRelation


class ImageRepo(ABC):

    @abstractmethod
    async def get_by_id(self, id_: int) -> Image:
        ...

    @abstractmethod
    async def get_by_url(self, url: str):
        ...

    @abstractmethod
    async def add(self, url: str, shows: int) -> Image:
        ...

    @abstractmethod
    async def change_shows(self, id_: int):
        ...

    @abstractmethod
    async def get_random(self) -> Image:
        ...


class CategoryRepo(ABC):
    @abstractmethod
    async def get_by_name(self, name: str) -> Category:
        ...

    @abstractmethod
    async def add(self, name: str) -> Category:
        ...


class ImageCategoryRelationRepo(ABC):

    @abstractmethod
    async def get_by_relation(
            self,
            image_id: int,
            category_id: int
    ) -> ImageCategoryRelation:
        ...

    @abstractmethod
    async def get_by_category_id(self, category_id: int) -> List[ImageCategoryRelation]:
        ...

    @abstractmethod
    async def add(self, image_id: int, category_id: int):
        ...
