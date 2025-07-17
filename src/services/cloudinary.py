import cloudinary
import cloudinary.uploader
import cloudinary.api
from decouple import config


cloudinary.config(
    cloud_name=config("CLOUDINARY_CLOUD_NAME"),
    api_key=config("CLOUDINARY_API_KEY"),
    api_secret=config("CLOUDINARY_API_SECRET"),
    secure=True
)


async def upload_avatar(image_path: str, public_id: str = None):
    result = cloudinary.uploader.upload(
        image_path,
        folder="avatars",
        public_id=public_id,
        overwrite=True,
        transformation=[{"width": 250, "height": 250, "crop": "fill"}]
    )
    return result.get("secure_url")
