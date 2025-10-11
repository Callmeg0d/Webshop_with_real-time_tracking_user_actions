import aiofiles
from fastapi import APIRouter, UploadFile

router = APIRouter(
    prefix="/images",
    tags=["Загрузка картинок"]
)


@router.post("/products")
async def add_image(name: int, file: UploadFile):
    async with aiofiles.open(f"app/static/images/{name}.webp", "wb+") as file_object:
        file = await file.read()
        await file_object.write(file)