"""
Проверка предложения ученика через LLM (GenAPI, OpenAI-совместимый прокси).

Установка:
    pip install openai pydantic python-dotenv

.env:
    GENAPI_API_KEY=ваш_ключ
    GENAPI_BASE_URL=https://proxy.gen-api.ru/v1
    GENAPI_MODEL=gemini-2.5-flash-preview-04-17
"""

import json
import os
import re
from typing import Any, Dict, List

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()


# ------------------------------------------------------------------
# Клиент
# ------------------------------------------------------------------
client = OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("BASE_URL", "https://proxy.gen-api.ru/v1"),
)

MODEL = os.getenv("MODEL", "gemini-2.5-flash-preview-04-17")


# ------------------------------------------------------------------
# Схема ответа LLM
# ------------------------------------------------------------------
class SentenceError(BaseModel):
    type: str = Field(description="Тип ошибки: grammar, word_order, vocabulary, style")
    original: str = Field(description="Фрагмент с ошибкой")
    correction: str = Field(description="Исправленный фрагмент")
    explanation: str = Field(description="Объяснение на русском")


class SentenceCheckResult(BaseModel):
    corrected: str = Field(description="Исправленное предложение")
    is_correct: bool = Field(description="Верно ли предложение без ошибок")
    score: int = Field(ge=1, le=10, description="Оценка от 1 до 10")
    errors: List[SentenceError] = Field(default_factory=list)
    alternatives: List[str] = Field(default_factory=list)
    recommendation: str = Field(description="Короткая рекомендация, что повторить")


# ------------------------------------------------------------------
# Промпты
# ------------------------------------------------------------------
SYSTEM_PROMPT = """Ты — методист по английскому языку.
Проверь предложение ученика уровня A2–B1.
Верни строго JSON по схеме. Не выдумывай ошибки, если их нет.
Все объяснения — на русском языке.
Обращайся к ученику на «ты».
Не добавляй точку в конце corrected, если её не было у ученика.
Используй ТОЛЬКО имена полей из схемы:
corrected, is_correct, score, errors, alternatives, recommendation.
Для каждой ошибки: type, original, correction, explanation."""

USER_PROMPT = """Слово: {word}
Предложение ученика: {sentence}

Проверь грамматику, порядок слов, лексику и естественность.
Наличие слова {word} обязательно, иначе текст считается ошибочным.
Если предложение верное — is_correct=true, errors=[].
Если есть ошибки — перечисли их с объяснением на русском.
Дай оценку 1–10 (поле score), 1–2 альтернативы и короткую рекомендацию."""


# ------------------------------------------------------------------
# Проверка предложения
# ------------------------------------------------------------------
def check_sentence(sentence: str, word: str) -> SentenceCheckResult:
    sentence = sentence.strip()
    if not sentence:
        raise ValueError("Пустое предложение")
    if len(sentence) > 300:
        raise ValueError("Предложение слишком длинное (максимум 300 символов)")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT.format(word=word, sentence=sentence)},
    ]

    raw = _call_llm(messages, use_json_schema=True)
    if raw is None:
        raw = _call_llm(messages, use_json_schema=False)

    if raw is None:
        raise RuntimeError("LLM не вернул ответ")

    data = _extract_json(raw)
    data = _normalize(data)
    return SentenceCheckResult(**data)


def _call_llm(messages: list, use_json_schema: bool) -> str | None:
    """Пробует вызвать LLM. Возвращает сырой ответ или None при неудаче."""
    kwargs: Dict[str, Any] = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.2,
    }

    if use_json_schema:
        kwargs["response_format"] = {
            "type": "json_schema",
            "json_schema": {
                "name": "SentenceCheckResult",
                "strict": True,
                "schema": SentenceCheckResult.model_json_schema(),
            },
        }
    else:
        kwargs["response_format"] = {"type": "json_object"}

    try:
        response = client.chat.completions.create(**kwargs)
        return response.choices[0].message.content or ""
    except Exception as e:
        # Логируем причину, но не падаем — попробуем fallback
        print(f"[LLM warning] {e}")
        return None


def _extract_json(raw: str) -> dict:
    """Достаёт JSON из ответа LLM, даже если вокруг есть текст."""
    raw = raw.strip()

    # Убираем markdown-обёртку ```json ... ```
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?", "", raw).strip()
        raw = re.sub(r"```$", "", raw).strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise ValueError(f"LLM вернул не JSON: {raw[:200]}")
    return json.loads(match.group(0))


# ------------------------------------------------------------------
# Нормализация ответа LLM под нашу схему
# ------------------------------------------------------------------
_TOP_ALIASES = {
    "corrected": ["corrected", "corrected_sentence", "fixed", "correction"],
    "is_correct": ["is_correct", "correct", "is_valid", "valid"],
    "score": ["score", "grade", "mark", "rating", "points"],
    "errors": ["errors", "mistakes", "issues", "problems"],
    "alternatives": ["alternatives", "variants", "options", "other_variants"],
    "recommendation": ["recommendation", "advice", "tip", "recommendations"],
}

_ERROR_ALIASES = {
    "type": ["type", "category", "kind"],
    "original": ["original", "location", "fragment", "wrong", "incorrect", "source"],
    "correction": ["correction", "suggestion", "fix", "correct", "corrected"],
    "explanation": ["explanation", "reason", "issue", "comment", "note", "details"],
}


def _pick(d: dict, aliases: list, default=None):
    for key in aliases:
        if key in d and d[key] is not None:
            return d[key]
    return default


def _normalize(data: dict) -> dict:
    """Приводит ответ LLM к нашей схеме, прощая разные имена полей."""
    result: Dict[str, Any] = {}

    for field, aliases in _TOP_ALIASES.items():
        result[field] = _pick(data, aliases)

    # corrected: если LLM не дала — попробуем собрать из ошибок или взять исходное
    if not result.get("corrected"):
        result["corrected"] = data.get("sentence") or data.get("original") or ""

    # is_correct: если не пришло — выведем из errors
    if result.get("is_correct") is None:
        result["is_correct"] = not result.get("errors")

    # score: если не пришло — поставим дефолт
    if result.get("score") is None:
        result["score"] = 10 if result["is_correct"] else 5
    try:
        result["score"] = int(result["score"])
    except (TypeError, ValueError):
        result["score"] = 5
    result["score"] = max(1, min(10, result["score"]))

    # errors
    errors_raw = result.get("errors") or []
    if not isinstance(errors_raw, list):
        errors_raw = []
    errors: List[dict] = []
    for e in errors_raw:
        if not isinstance(e, dict):
            continue
        errors.append({
            "type": _pick(e, _ERROR_ALIASES["type"], "grammar"),
            "original": _pick(e, _ERROR_ALIASES["original"], ""),
            "correction": _pick(e, _ERROR_ALIASES["correction"], ""),
            "explanation": _pick(e, _ERROR_ALIASES["explanation"], ""),
        })
    result["errors"] = errors

    # alternatives
    alts = result.get("alternatives") or []
    if not isinstance(alts, list):
        alts = [alts]
    result["alternatives"] = [str(a) for a in alts if a]

    # recommendation
    if not result.get("recommendation"):
        result["recommendation"] = ""

    return result


# ------------------------------------------------------------------
# Форматирование ответа для ученика
# ------------------------------------------------------------------
def format_result(result: SentenceCheckResult, original: str) -> str:
    if result.is_correct:
        header = "✅ Всё верно"
    elif result.score >= 6:
        header = "🟡 Почти получилось"
    else:
        header = "🔴 Есть ошибки"

    lines = [
        header,
        "",
        f"Твоё предложение: {original}",
        f"Исправлено: {result.corrected}",
    ]

    if result.errors:
        lines.append("")
        lines.append("Ошибки:")
        for e in result.errors:
            lines.append(
                f"• «{e.original}» → «{e.correction}»\n  {e.explanation}"
            )

    lines.append("")
    lines.append(f"Оценка: {result.score}/10")

    if result.alternatives:
        lines.append("")
        lines.append("Ещё можно сказать:")
        for alt in result.alternatives:
            lines.append(f"• {alt}")

    if result.recommendation:
        lines.append("")
        lines.append(f"💡 {result.recommendation}")

    return "\n".join(lines)


# ------------------------------------------------------------------
# Пример запуска
# ------------------------------------------------------------------
if __name__ == "__main__":
    original = "I want achieve good results"
    word = "achieve"

    try:
        result = check_sentence(sentence=original, word=word)
    except Exception as e:
        print(f"Ошибка проверки: {e}")
        raise SystemExit(1)

    print(format_result(result, original))

    # Сырой JSON — для отладки
    # print(result.model_dump_json(indent=2, ensure_ascii=False))