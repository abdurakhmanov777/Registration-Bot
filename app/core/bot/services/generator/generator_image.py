"""
Модуль для работы с изображениями.

Содержит функции для создания изображений с текстом поверх
фонового изображения.
"""

from io import BytesIO
from typing import Literal

from PIL import Image, ImageDraw, ImageFont
from PIL.ImageFile import ImageFile

from app.config import BACKGROUND_PATH, FONT_PATH


async def generate_image(
    text: str,
) -> BytesIO:
    """
    Создает изображение с текстом поверх фонового изображения.

    Аргументы:
        text (str): Текст, который будет добавлен на изображение.

    Возвращает:
        BytesIO: Буфер с PNG-изображением.
    """
    # Загружаем фоновое изображение
    image: ImageFile = Image.open(BACKGROUND_PATH)
    draw: ImageDraw.ImageDraw = ImageDraw.Draw(image)

    # Подбираем размер шрифта относительно высоты изображения
    font_size = int(image.height * 0.4)
    font: ImageFont.FreeTypeFont = ImageFont.truetype(
        FONT_PATH,
        size=font_size
    )

    # Вычисляем координаты для центрирования текста
    bbox: tuple[float, float, float, float] = draw.textbbox(
        (0, 0),
        text,
        font=font
    )
    text_width: float = bbox[2] - bbox[0]
    text_height: float = bbox[3] - bbox[1]
    text_x: float = (image.width - text_width) / 2
    text_y: float = (image.height - text_height) * 0.4

    # Цвет текста (белый)
    font_color: tuple[Literal[255], Literal[255], Literal[255]] = (
        255, 255, 255
    )
    draw.text(
        (text_x, text_y),
        text,
        font=font,
        fill=font_color
    )

    # Сохраняем изображение в буфер и возвращаем
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer
