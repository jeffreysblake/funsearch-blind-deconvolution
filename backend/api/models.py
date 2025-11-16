"""Models (LLM) API endpoints."""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ModelInfo(BaseModel):
    """LLM model information."""

    id: str
    name: str
    size: str | None = None
    type: str | None = None
    loaded: bool = False


class ModelListResponse(BaseModel):
    """List of available models."""

    models: list[ModelInfo]
    provider: str
    base_url: str


@router.get("/models", response_model=ModelListResponse)
async def list_models():
    """
    List available models from LM Studio.

    If LM Studio is not available, returns mock models.
    """
    try:
        import httpx

        response = httpx.get("http://localhost:1234/v1/models", timeout=2)

        if response.status_code == 200:
            data = response.json()
            models = []

            for model in data.get("data", []):
                models.append(
                    ModelInfo(
                        id=model.get("id", "unknown"),
                        name=model.get("id", "unknown"),
                        size=None,  # LM Studio doesn't provide this
                        type="code-generation",
                        loaded=True,
                    )
                )

            return ModelListResponse(
                models=models, provider="lm_studio", base_url="http://localhost:1234/v1"
            )

    except Exception:
        pass

    # Return mock models if LM Studio not available
    return ModelListResponse(
        models=[
            ModelInfo(
                id="mock-qwen-8b",
                name="Mock Qwen 8B",
                size="8B",
                type="mock",
                loaded=True,
            ),
            ModelInfo(
                id="mock-mistral-small",
                name="Mock Mistral Small",
                size="22B",
                type="mock",
                loaded=True,
            ),
        ],
        provider="mock",
        base_url="mock://localhost",
    )
