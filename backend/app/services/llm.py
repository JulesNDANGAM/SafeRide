"""OpenRouter LLM client for the SafeRide Agentic AI layer.

Implements the *Passenger Communication* and *Predictive Analytics*
capabilities described in the SafeRide ideation PDF (section 6).

- Default model: a free OpenRouter model (e.g. ``meta-llama/llama-3.2-3b-instruct:free``)
- Free models supported on OpenRouter:
    * meta-llama/llama-3.2-3b-instruct:free
    * meta-llama/llama-3.1-8b-instruct:free
    * google/gemini-2.0-flash-exp:free
    * mistralai/mistral-7b-instruct:free
    * qwen/qwen-2-7b-instruct:free
- Configure via environment variables (see ``backend/.env.example``).
- If no API key is provided, the agent falls back to deterministic
  bilingual templates so the prototype keeps working offline.

Reference: https://openrouter.ai/docs
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass

import httpx

from ..config import settings


logger = logging.getLogger("saferide.llm")


@dataclass
class LLMExplanation:
    message_fr: str
    message_en: str
    recommendation: str  # accept | review | reject
    model: str
    used_llm: bool


def _system_prompt() -> str:
    return (
        "You are SafeRide's Trust Agent. SafeRide computes a Network Trust Score "
        "(0-100) for ride-hailing drivers in Sub-Saharan Africa using CAMARA APIs "
        "via Nokia Network-as-Code. You explain the trust decision in 1 sentence "
        "to passengers. Always respond with strict JSON of the form: "
        "{\"message_fr\": \"...\", \"message_en\": \"...\", \"recommendation\": \"accept|review|reject\"}. "
        "Tone: clear, calm, factual. Do not invent data. If the score is high, "
        "be reassuring; if low, be cautious and protective."
    )


def _user_prompt(snapshot_dict: dict) -> str:
    return (
        "Driver snapshot (JSON):\n"
        + json.dumps(snapshot_dict, ensure_ascii=False)
        + "\n\nWrite the bilingual passenger message and the recommendation."
    )


_JSON_FENCE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL | re.IGNORECASE)


def _extract_json(content: str) -> dict | None:
    """Tolerant JSON extractor: strips markdown fences if any."""
    if not content:
        return None
    text = content.strip()
    try:
        return json.loads(text)
    except ValueError:
        pass
    fence = _JSON_FENCE.search(text)
    if fence:
        try:
            return json.loads(fence.group(1))
        except ValueError:
            pass
    # Last resort: find first {...} block
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except ValueError:
            return None
    return None


def _fallback(snapshot_dict: dict) -> LLMExplanation:
    score = snapshot_dict.get("trust_score", 0)
    name = snapshot_dict.get("driver_name", "your driver")
    if score >= 70:
        rec = "accept"
        msg_en = (
            f"{name} passes all SafeRide checks (score {score}/100). "
            "Network signals confirm identity and connectivity."
        )
        msg_fr = (
            f"{name} passe tous les contrôles SafeRide (score {score}/100). "
            "Les signaux réseau confirment l'identité et la connectivité."
        )
    elif score >= 40:
        rec = "review"
        msg_en = (
            f"{name} has some warnings (score {score}/100). "
            "Review the trust details before confirming the ride."
        )
        msg_fr = (
            f"{name} présente des avertissements (score {score}/100). "
            "Vérifiez les détails de confiance avant de valider la course."
        )
    else:
        rec = "reject"
        msg_en = (
            f"{name} is blocked by the trust engine (score {score}/100) "
            "due to network anomalies. SafeRide team is being notified."
        )
        msg_fr = (
            f"{name} est bloqué par le moteur de confiance (score {score}/100) "
            "en raison d'anomalies réseau. L'équipe SafeRide est alertée."
        )
    return LLMExplanation(
        message_fr=msg_fr, message_en=msg_en, recommendation=rec,
        model="fallback-template", used_llm=False,
    )


class OpenRouterAgent:
    """Thin synchronous wrapper around the OpenRouter Chat Completions API."""

    def __init__(self) -> None:
        self.api_key = settings.openrouter_api_key
        self.model = settings.openrouter_model
        self.base_url = settings.openrouter_base_url.rstrip("/")
        self.timeout = settings.openrouter_timeout_s
        self.referer = settings.openrouter_referer
        self.app_name = settings.openrouter_app_name

    @property
    def configured(self) -> bool:
        return bool(self.api_key)

    def explain(self, snapshot_dict: dict) -> LLMExplanation:
        if not self.configured:
            return _fallback(snapshot_dict)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.referer,
            "X-Title": self.app_name,
        }
        body = {
            "model": self.model,
            "temperature": 0.2,
            "max_tokens": 220,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": _system_prompt()},
                {"role": "user", "content": _user_prompt(snapshot_dict)},
            ],
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=body,
                )
                response.raise_for_status()
                data = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            logger.warning("OpenRouter call failed (%s) – falling back to template", exc)
            fb = _fallback(snapshot_dict)
            fb.model = f"fallback-after-error:{exc.__class__.__name__}"
            return fb

        try:
            content = data["choices"][0]["message"]["content"] or ""
            parsed = _extract_json(content)
            if parsed is None:
                logger.warning("OpenRouter returned non-JSON content: %r", content[:200])
                return _fallback(snapshot_dict)
            return LLMExplanation(
                message_fr=str(parsed.get("message_fr", "")).strip() or _fallback(snapshot_dict).message_fr,
                message_en=str(parsed.get("message_en", "")).strip() or _fallback(snapshot_dict).message_en,
                recommendation=str(parsed.get("recommendation", "review")).strip().lower(),
                model=self.model,
                used_llm=True,
            )
        except (KeyError, IndexError, ValueError, TypeError) as exc:
            logger.warning("OpenRouter response parsing failed (%s) – fallback", exc)
            return _fallback(snapshot_dict)


agent = OpenRouterAgent()
