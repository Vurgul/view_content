import os
from dataclasses import dataclass

import aiocsv
import aiofiles

from models.interface import CategoryRepo, ImageCategoryRelationRepo, ImageRepo


@dataclass
class FileLoader:
    path: str
    image_repo: ImageRepo
    category_repo: CategoryRepo
    image_category_relation_repo: ImageCategoryRelationRepo

    async def read(self, file_name: str):
        path = self._get_path(file_name)
        async with aiofiles.open(path, newline='') as csvfile:
            reader = aiocsv.AsyncReader(csvfile, delimiter=';')
            async for line in reader:
                await self._save_info(line)

    async def _save_info(self, line: list):
        image_url, needed_shows, *categories = line
        new_image = await self.image_repo.add(image_url, needed_shows)
        for category in categories:
            new_category = await self.category_repo.add(category)
            await self.image_category_relation_repo.add(new_image.id, new_category.id)

    def _get_path(self, name: str) -> str:
        return os.path.join(self.path, name)
