"""
rag.py  –  Retrieval-Augmented Generation layer
Supports two LLM providers, selected via LLM_PROVIDER env var:

  LLM_PROVIDER=ollama   →  Local Ollama  (default, no API key needed)
  LLM_PROVIDER=gemini   →  Google Gemini (requires GEMINI_API_KEY)

No provider name or model name is hardcoded in logic — all values come
from environment variables.
"""
from __future__ import annotations

import json
import logging
import os
import re
import urllib.request
import urllib.error

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
#  Config — all from environment, zero hardcoding
# ─────────────────────────────────────────────────────────────────────────────
def _provider() -> str:
    return os.environ.get("LLM_PROVIDER", "ollama").lower().strip()

# Ollama
_OLLAMA_BASE = lambda: os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/api").rstrip("/")
_OLLAMA_MODEL = lambda: os.environ.get("OLLAMA_MODEL", "gemma4:e4b")

# Gemini
_GEMINI_API_KEY   = lambda: os.environ.get("GEMINI_API_KEY", "")
_GEMINI_MODEL     = lambda: os.environ.get("GEMINI_MODEL", "gemini-3-flash-preview")
_GEMINI_API_BASE  = "https://generativelanguage.googleapis.com/v1beta"

# gemma4 chain-of-thought
_GEMMA4_OPTIONS = {"temperature": 1.0, "top_p": 0.95, "top_k": 64}
_THINK_RE = re.compile(r"<\|channel>thought\n.*?<channel\|>", re.DOTALL)


# ─────────────────────────────────────────────────────────────────────────────
#  Shared helpers
# ─────────────────────────────────────────────────────────────────────────────
def _build_context(chunks: list[dict]) -> str:
    return "\n\n---\n\n".join(
        f"[Chunk {i+1}]\n{c['chunk_data']}" for i, c in enumerate(chunks)
    )


def _system_prompt(model: str = "") -> str:
    think = "<|think|>\n" if model.startswith("gemma4") else ""
    return (
        f"{think}"
        "You are a knowledgeable assistant. "
        "Answer the user's question using ONLY the context provided below. "
        "If the context does not contain enough information, say so clearly. "
        "Be concise and cite relevant chunk numbers when appropriate."
    )


def _strip_thinking(text: str) -> str:
    return _THINK_RE.sub("", text).strip()


# ─────────────────────────────────────────────────────────────────────────────
#  OLLAMA provider
# ─────────────────────────────────────────────────────────────────────────────
def _ollama_available() -> bool:
    try:
        url = f"{_OLLAMA_BASE()}/tags"
        with urllib.request.urlopen(url, timeout=2) as r:
            data = json.loads(r.read())
            return bool(data.get("models"))
    except Exception:
        return False


def _ollama_models() -> list[str]:
    try:
        url = f"{_OLLAMA_BASE()}/tags"
        with urllib.request.urlopen(url, timeout=3) as r:
            data = json.loads(r.read())
            return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []


def _ollama_generate(query: str, chunks: list[dict], model: str) -> str:
    context = _build_context(chunks)
    options = _GEMMA4_OPTIONS if model.startswith("gemma4") else {}
    payload = json.dumps({
        "model":   model,
        "stream":  False,
        "options": options,
        "messages": [
            {"role": "system", "content": _system_prompt(model)},
            {"role": "user",   "content": f"Context:\n{context}\n\nQuestion: {query}"},
        ],
    }).encode()

    req = urllib.request.Request(
        f"{_OLLAMA_BASE()}/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=80) as r:
            content = json.loads(r.read())["message"]["content"]
            return _strip_thinking(content) if model.startswith("gemma4") else content
    except urllib.error.URLError as e:
        raise RuntimeError(
            f"Could not reach Ollama at {_OLLAMA_BASE()}. "
            "Is it running?  Start with: ollama serve"
        ) from e


# ─────────────────────────────────────────────────────────────────────────────
#  GEMINI provider  (uses REST — no SDK dependency)
#  Falls back to google-genai SDK if available for streaming support
# ─────────────────────────────────────────────────────────────────────────────
def _gemini_available() -> bool:
    return bool(_GEMINI_API_KEY())


def _gemini_models() -> list[str]:
    """
    Fetch available Gemini models from the API and filter to generative ones.
    Falls back to the configured default if the API call fails.
    """
    key = _GEMINI_API_KEY()
    if not key:
        return []
    try:
        url = f"{_GEMINI_API_BASE}/models?key={key}"
        with urllib.request.urlopen(url, timeout=5) as r:
            data = json.loads(r.read())
        models = [
            m["name"].replace("models/", "")
            for m in data.get("models", [])
            if "generateContent" in m.get("supportedGenerationMethods", [])
        ]
        return sorted(models) if models else [_GEMINI_MODEL()]
    except Exception:
        return [_GEMINI_MODEL()]


def _gemini_generate(query: str, chunks: list[dict], model: str) -> str:
    """
    Call Gemini via google-genai SDK (google.genai) with REST fallback.
    Never imports the deprecated google.generativeai package.
    All config values read from environment — nothing hardcoded.
    """
    key     = _GEMINI_API_KEY()
    context = _build_context(chunks)
    prompt  = (
        f"{_system_prompt()}\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {query}"
    )
    gen_cfg = {
        "temperature":       float(os.environ.get("GEMINI_TEMPERATURE", "0.7")),
        "max_output_tokens": int(os.environ.get("GEMINI_MAX_TOKENS",    "1024")),
    }

    # ── current SDK: google-genai (google.genai) ──────────────────────────────
    try:
        from google import genai                        # type: ignore
        from google.genai import types as genai_types  # type: ignore
        client   = genai.Client(api_key=key)
        response = client.models.generate_content(
            model    = model,
            contents = prompt,
            config   = genai_types.GenerateContentConfig(
                temperature       = gen_cfg["temperature"],
                max_output_tokens = gen_cfg["max_output_tokens"],
            ),
        )
        return response.text
    except ImportError:
        pass  # SDK not installed — fall through to REST

    # ── REST fallback — stdlib urllib, zero extra deps ────────────────────────
    url     = f"{_GEMINI_API_BASE}/models/{model}:generateContent?key={key}"
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature":     gen_cfg["temperature"],
            "maxOutputTokens": gen_cfg["max_output_tokens"],
        },
    }).encode()
    req = urllib.request.Request(
        url, data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read())
            return data["candidates"][0]["content"]["parts"][0]["text"]
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Gemini API error {e.code}: {body}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Could not reach Gemini API: {e}") from e

# ─────────────────────────────────────────────────────────────────────────────
#  Public API  —  used by app.py
# ─────────────────────────────────────────────────────────────────────────────
def is_rag_available() -> bool:
    """True if the active provider is reachable and configured."""
    if _provider() == "gemini":
        return _gemini_available()
    return _ollama_available()


def list_models() -> list[str]:
    """Return available models for the active provider."""
    if _provider() == "gemini":
        return _gemini_models()
    return _ollama_models()


def default_model() -> str:
    """Return the configured default model for the active provider."""
    if _provider() == "gemini":
        return _GEMINI_MODEL()
    return _OLLAMA_MODEL()


def generate_answer(
    query: str,
    chunks: list[dict],
    model: str | None = None,
) -> str:
    """
    Generate a RAG answer using the active provider.
    Provider is selected by LLM_PROVIDER env var (ollama | gemini).
    Model defaults to the provider's configured default if not specified.
    """
    if not chunks:
        return "No relevant context was found in the knowledge base."

    prov  = _provider()
    model = model or default_model()

    logger.info("RAG  provider=%s  model=%s  chunks=%d", prov, model, len(chunks))

    if prov == "gemini":
        return _gemini_generate(query, chunks, model)
    return _ollama_generate(query, chunks, model)
