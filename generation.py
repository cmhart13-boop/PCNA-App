from __future__ import annotations

import base64
import mimetypes
from typing import Iterable

from openai import OpenAI


def _data_url(data: bytes, filename: str, mime: str | None = None) -> str:
    mime = mime or mimetypes.guess_type(filename)[0] or "application/octet-stream"
    encoded = base64.b64encode(data).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def _upload_content(upload) -> dict | None:
    if upload is None:
        return None
    name = getattr(upload, "name", "reference")
    data = upload.getvalue()
    mime = getattr(upload, "type", None) or mimetypes.guess_type(name)[0] or "application/octet-stream"
    lower = name.lower()
    if mime.startswith("image/") or lower.endswith((".png", ".jpg", ".jpeg", ".webp")):
        return {"type": "input_image", "image_url": _data_url(data, name, mime), "detail": "high"}
    if mime == "application/pdf" or lower.endswith(".pdf"):
        return {
            "type": "input_file",
            "filename": name,
            "file_data": _data_url(data, name, mime),
        }
    return None


def generate_concepts(
    *,
    api_key: str,
    prompt: str,
    uploads: Iterable | None = None,
    count: int = 1,
) -> list[bytes]:
    """Generate concept images through the Responses API image_generation tool."""
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not configured.")

    client = OpenAI(api_key=api_key)
    reference_content = [x for x in (_upload_content(u) for u in (uploads or [])) if x]
    images: list[bytes] = []

    for index in range(max(1, min(int(count), 8))):
        variation_prompt = (
            f"{prompt}\n\n"
            f"Create concept {index + 1} of {count}. Make this concept visually distinct from the other requested concepts while preserving all supplied logos, product details, decoration placement, and brand instructions. "
            "Do not invent brand marks, product names, product colors, decoration methods, packaging structures, or text that was not requested. Produce a polished commercial promotional-product virtual suitable for client presentation."
        )
        content = [{"type": "input_text", "text": variation_prompt}, *reference_content]
        response = client.responses.create(
            model="gpt-5",
            input=[{"role": "user", "content": content}],
            tools=[
                {
                    "type": "image_generation",
                    "model": "gpt-image-1",
                    "quality": "high",
                    "size": "1024x1024",
                    "output_format": "png",
                    "input_fidelity": "high",
                }
            ],
            tool_choice={"type": "image_generation"},
        )
        generated = [item for item in response.output if getattr(item, "type", "") == "image_generation_call"]
        if not generated or not getattr(generated[-1], "result", None):
            raise RuntimeError("Image generation completed without an image result.")
        images.append(base64.b64decode(generated[-1].result))

    return images
