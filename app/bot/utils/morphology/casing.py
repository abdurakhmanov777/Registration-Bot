import re
from typing import List

# Шаблон для поиска слов, пробелов и пунктуации
WORD_PATTERN: re.Pattern = re.compile(r'\w+|\s+|[^\w\s]', re.UNICODE)

# Шаблон для поиска конца предложения (., !, ?)
SENTENCE_ENDINGS_PATTERN: re.Pattern = re.compile(r'([.!?])(\s+|$)')


async def lower_words(
    text: str,
    capitalize_first: bool = True
) -> str:
    """
    Преобразует текст в нижний регистр, кроме аббревиатур.
    Опционально делает первую букву каждого предложения заглавной.

    Args:
        text: Исходный текст.
        capitalize_first: Если True, первая буква предложения
                          будет заглавной.

    Returns:
        Преобразованный текст.
    """
    def is_abbr(
        word: str
    ) -> bool:
        """Проверяет, является ли слово аббревиатурой."""
        return word.isupper() and len(word) > 1

    def format_word(
        word: str
    ) -> str:
        """Делает слово нижним регистром, если это не аббревиатура."""
        return word if is_abbr(word) else word.lower()

    # Разбиваем текст на предложения с сохранением разделителей
    parts: List[str] = SENTENCE_ENDINGS_PATTERN.split(text)
    sentences: List[str] = [
        "".join(parts[i:i + 2]) for i in range(0, len(parts), 2)
    ]

    processed_sentences: List[str] = []

    for sentence in sentences:
        tokens: List[str] = WORD_PATTERN.findall(sentence)
        result: List[str] = []
        capitalize_next: bool = capitalize_first

        for token in tokens:
            if token.strip() and token.isalpha():
                word: str = format_word(token)
                if capitalize_next and not is_abbr(word):
                    word = word.capitalize()
                result.append(word)
                capitalize_next = False
            else:
                result.append(token)
                if token in '.!?':
                    capitalize_next = capitalize_first

        processed_sentences.append(''.join(result))

    return ''.join(processed_sentences)


def cap_words(
    text: str
) -> str:
    """
    Делает первую букву каждого слова заглавной, кроме аббревиатур.

    Args:
        text: Исходный текст.

    Returns:
        Текст с заглавными буквами в словах, кроме аббревиатур.
    """
    def is_abbr(word: str) -> bool:
        """Проверяет, является ли слово аббревиатурой."""
        return word.isupper() and len(word) > 1

    def process_token(token: str) -> str:
        """Делает первую букву токена заглавной, если не аббревиатура."""
        if token.isalpha():
            return token if is_abbr(token) else token.capitalize()
        return token

    tokens: List[str] = WORD_PATTERN.findall(text)
    processed: List[str] = [process_token(token) for token in tokens]

    return ''.join(processed)
