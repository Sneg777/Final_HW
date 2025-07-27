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
    """
    Upload an avatar image to Cloudinary with automatic resizing and optimization.

    Args:
        image_path: Path to the image file to upload (can be local path or URL)
        public_id: Optional unique public identifier for the image.
                  If not provided, Cloudinary will generate one.

    Returns:
        str: Secure URL of the uploaded and transformed avatar image

    Raises:
        Exception: If the upload fails or credentials are invalid

    Example:
        >>> url = upload_avatar("user_photo.jpg", "user123@example.com")
        >>> print(url)
        "https://res.cloudinary.com/demo/image/upload/avatars/user123@example.com.jpg"
    """
    result = cloudinary.uploader.upload(
        image_path,
        folder="avatars",
        public_id=public_id,
        overwrite=True,
        transformation=[{"width": 250, "height": 250, "crop": "fill"}]
    )
    return result.get("secure_url")
