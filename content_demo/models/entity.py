from dataclasses import dataclass
from typing import Optional


@dataclass
class Category:
    name: str
    id: Optional[int] = None


@dataclass
class Image:
    url: str
    shows: int
    id: Optional[int] = None


@dataclass
class ImageCategoryRelation:
    image_id: int
    category_id: int
    id: Optional[int] = None
