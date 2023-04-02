from typing import Optional

import attr


@attr.dataclass
class Category:
    name: str
    id: Optional[int] = None


@attr.dataclass
class Image:
    url: str
    shows: int
    id: Optional[int] = None


@attr.dataclass
class ImageCategoryRelation:
    image_id: int
    category_id: int
    id: Optional[int] = None
