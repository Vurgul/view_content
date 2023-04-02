from dataclasses import dataclass
from typing import List, Optional

from models.entity import Image
from models.interface import CategoryRepo, ImageCategoryRelationRepo, ImageRepo


@dataclass
class ImageHandler:
    image_repo: ImageRepo
    category_repo: CategoryRepo
    image_category_relation_repo: ImageCategoryRelationRepo
    _hash_image_url: Optional[str] = None

    def get_by_categories(self, categories: Optional[List[str]]) -> str:
        if categories:
            image = self._get_image(categories)
            if image:
                return image.url
            return 'Для заданных категорий картинки закончились'
        image = self._get_random_image()
        if image:
            return image.url
        return 'Картинки закончились'

    def _get_image(self, categories: List[str]) -> Image:
        temp_categories = []
        temp_relations = []
        temp_images = []
        for category in categories:
            record = self.category_repo.get_by_name(category)
            if record:
                temp_relations.extend(
                    self.image_category_relation_repo.get_by_category_id(record.id)
                )
                temp_categories.append(record)
        for temp_relation in temp_relations:
            temp_image = self.image_repo.get_by_id(temp_relation.image_id)
            if temp_image.shows != 0:
                temp_images.append(temp_image)

        image = self.check_hash(temp_images)
        return image

    def check_hash(self, images: List[Image]) -> Image:
        amount_images = len(images)
        max_shows_count = max([image.shows for image in images])
        for image in images:
            if image.shows == max_shows_count:
                if image.url != self._hash_image_url or amount_images == 1:
                    self._hash_image_url = image.url
                    self.image_repo.change_shows(image.id)
                    return image
            if image.shows == max_shows_count and image.url == self._hash_image_url:
                new_images = images.copy()
                new_images.remove(image)
                new_max_shows_count = max([image.shows for image in new_images])
                for mew_image in new_images:
                    if mew_image.shows == new_max_shows_count:
                        self._hash_image_url = mew_image.url
                        self.image_repo.change_shows(mew_image.id)
                        return mew_image

    def _get_random_image(self):
        image = self.image_repo.get_random()
        if image:
            self._hash_image_url = image.url
        return image
