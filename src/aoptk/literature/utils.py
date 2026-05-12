import asyncio
import time
from pathlib import Path
from PIL import Image
from aoptk.literature.id import ID


class AsyncRequestLimiter:
    """Asynchronous request limiter to control the rate of API calls."""

    def __init__(self, requests_per_second: int):
        self.min_interval = 1.0 / requests_per_second
        self._lock = asyncio.Lock()
        self._next_allowed = 0.0

    async def wait_turn(self) -> None:
        """Wait until it's the turn for the next request based on the rate limit."""
        async with self._lock:
            now = time.monotonic()
            if now < self._next_allowed:
                await asyncio.sleep(self._next_allowed - now)
                now = time.monotonic()
            self._next_allowed = now + self.min_interval


def is_europepmc_id(publication_id: ID) -> bool:
    """Check if the given publication ID is a EuropePMC ID."""
    return bool(str(publication_id).startswith("PMC"))


def convert_image_format(images_to_convert_path: list[Path], target_format: str = "png") -> list[Path]:
    """Convert every image in a list to the specified format.

    Args:
        images_to_convert_path: The images to convert.
        target_format: The desired image format (e.g., 'png', 'jpg').
    """
    converted_images: list[Path] = []

    for image_path in images_to_convert_path:
        if _image_in_this_format_already_exists(target_format, image_path):
            converted_images.append(image_path)
        else:
            converted_image_path = image_path.with_suffix(f".{target_format}")
            with Image.open(image_path) as img:
                img.save(converted_image_path)
            converted_images.append(converted_image_path)
            image_path.unlink()

    return sorted(converted_images)


def _image_in_this_format_already_exists(target_format: str, image_path: Path) -> bool:
    """Check if the image is already in the target format.

    Args:
        target_format: The desired image format (e.g., 'png', 'jpg').
        image_path: The path of the image to check.
    """
    return image_path.suffix.lower() == f".{target_format}"
