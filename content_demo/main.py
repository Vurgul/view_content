import asyncio
import logging
import os
from typing import List, Optional

import uvicorn
from dotenv import dotenv_values
from fastapi import Depends, FastAPI, Query, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from application.handler import ImageHandler
from db.repos import CategoryRepo, ImageCategoryRelationRepo, ImageRepo
from storage.file_loader import FileLoader

TITLE = 'ContentAPI'
DIRECTORY = 'templates'
FILE_NAME = 'config.csv'

config = dotenv_values('.env')

app = FastAPI(title=TITLE)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.ERROR)

templates = Jinja2Templates(directory=DIRECTORY)


class Loader:
    loader = FileLoader(
        path=config.get('FILE_PATH'),
        image_repo=ImageRepo(),
        category_repo=CategoryRepo(),
        image_category_relation_repo=ImageCategoryRelationRepo()
    )


class Handler:
    handler = ImageHandler(
        image_repo=ImageRepo(),
        category_repo=CategoryRepo(),
        image_category_relation_repo=ImageCategoryRelationRepo()
    )


@app.get('/', response_class=HTMLResponse)
async def show_image(
        request: Request,
        categories: Optional[List[str]] = Query(None, max_length=10),
        handler: ImageHandler = Depends(lambda: Handler.handler),

):
    url = await handler.get_by_categories(categories)

    return templates.TemplateResponse(
        "static.html",
        {
            "request": request,
            "url": url,
        }
    )


@app.get('/static/{image_name}')
async def get_image(image_name: str):
    filename = os.path.join(config.get('IMAGE_PATH'), image_name)
    return FileResponse(filename)


async def main():
    await Loader.loader.read(FILE_NAME)
    uvicorn.run(
        'main:app',
        host=config.get('APP_HOST'),
        port=int(config.get('APP_PORT')),
        reload=True
    )


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
