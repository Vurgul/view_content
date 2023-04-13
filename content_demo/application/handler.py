from typing import List, Optional

from fastapi import HTTPException

from models.entity import Image
from models.interface import CategoryRepo, ImageCategoryRelationRepo, ImageRepo


class ImageHandler:
    _cache_image_url: Optional[str] = None

    def __init__(
            self,
            image_repo: ImageRepo,
            category_repo: CategoryRepo,
            image_category_relation_repo: ImageCategoryRelationRepo,
    ):
        self.image_repo = image_repo
        self.category_repo = category_repo
        self.image_category_relation_repo = image_category_relation_repo

    async def get_by_categories(self, categories: Optional[List[str]]) -> str:
        if categories:
            image = await self._get_image(categories)
            print(f'{image=}')
            if image:
                await self.image_repo.change_shows(image.id)
                return image.url
            raise HTTPException(
                status_code=400,
                detail='Для заданных категорий картинки закончились'
            )
        image = await self._get_random_image()
        if image:
            await self.image_repo.change_shows(image.id)
            return image.url
        raise HTTPException(status_code=400, detail='Картинки закончились')

    async def _get_image(self, categories: List[str]) -> Image:
        temp_relations = []
        temp_images = []
        for category in categories:
            record = await self.category_repo.get_by_name(category)
            if record:
                temp_relations.extend(
                    await self.image_category_relation_repo.get_by_category_id(record.id)
                )
        for temp_relation in temp_relations:
            temp_image = await self.image_repo.get_by_id(temp_relation.image_id)
            if temp_image.shows != 0:
                temp_images.append(temp_image)

        image = self._check_cache(temp_images)
        return image

    def _check_cache(self, images: List[Image]) -> Image:
        if len(images) == 1:
            self._cache_image_url = images[0].url
            return images[0]
        temp_max = 0
        temp_image = None
        for image in images:
            if image.shows >= temp_max and image.url != self._cache_image_url:
                temp_max = image.shows
                temp_image = image
                self._cache_image_url = image.url
        return temp_image

    async def _get_random_image(self) -> Image:
        image = await self.image_repo.get_random()
        if image:
            self._cache_image_url = image.url
        return image
