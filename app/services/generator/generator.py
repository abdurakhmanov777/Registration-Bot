from io import BytesIO
from typing import Literal

from PIL import Image, ImageDraw, ImageFont
from PIL.ImageFile import ImageFile

from app.config import FONT_PATH, IMAGE_PATH


async def create_text_image(
    text: str,
) -> BytesIO:
    """
    Создает изображение с текстом поверх фонового изображения.

    Args:
        text (str): Текст, который будет добавлен на изображение.

    Returns:
        BytesIO: Буфер с PNG-изображением.
    """
    # Открываем фоновое изображение
    image: ImageFile = Image.open(IMAGE_PATH)
    draw: ImageDraw.ImageDraw = ImageDraw.Draw(image)

    # Подбираем размер шрифта относительно высоты изображения
    font_size = int(image.height * 0.5)
    font: ImageFont.FreeTypeFont = ImageFont.truetype(
        FONT_PATH,
        size=font_size
    )

    # Вычисляем координаты для центрирования текста
    bbox: tuple[float, float, float, float] = draw.textbbox(
        (0, 0), text, font=font
    )
    text_x: float = (image.width - (bbox[2] - bbox[0])) / 2
    text_y: float = (image.height - (bbox[3] - bbox[1])) * 0.4

    # Цвет текста (белый)
    font_color: tuple[Literal[255], Literal[255], Literal[255]] = (
        255, 255, 255
    )
    draw.text((text_x, text_y), text, font=font, fill=font_color)

    # Сохраняем изображение в буфер
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer

