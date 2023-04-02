import csv
import os
from dataclasses import dataclass

from models.interface import CategoryRepo, ImageCategoryRelationRepo, ImageRepo


@dataclass
class FileLoader:
    path: str
    image_repo: ImageRepo
    category_repo: CategoryRepo
    image_category_relation_repo: ImageCategoryRelationRepo

    def read(self, file_name: str):
        path = self._get_path(file_name)
        with open(path, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            for line in reader:
                self._save_info(line)

    def _save_info(self, line):
        image_url, needed_shows, *categories = line
        new_image = self.image_repo.add(image_url, needed_shows)
        for category in categories:
            new_category = self.category_repo.add(category)
            self.image_category_relation_repo.add(new_image.id, new_category.id)

    def _get_path(self, name: str) -> str:
        return os.path.join(self.path, name)
