from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import AzureChatOpenAI
from pydantic import BaseModel, Field

from app.ai.prompts import CLASSIFIER_SYSTEM_PROMPT, RESPONDER_SYSTEM_PROMPT
from app.config import settings


class ServiceRequest311(BaseModel):
    category: str = Field(
        description="pothole|streetlight|graffiti|trash|water|sidewalk|noise|other"
    )
    location: str = Field(
        description="Street address or intersection. Use 'unknown' if not mentioned."
    )
    description: str = Field(description="One-sentence summary of the reported issue.")
    urgency: int = Field(ge=1, le=5, description="Urgency level from 1 (low) to 5 (critical)")
    confidence: float = Field(
        ge=0.0, le=1.0, description="Classification confidence between 0.0 and 1.0"
    )


_classifier_llm = AzureChatOpenAI(
    azure_deployment=settings.azure_deployment_classifier,
    azure_endpoint=settings.azure_openai_endpoint,
    api_key=settings.azure_openai_api_key,
    api_version=settings.azure_openai_api_version,
    temperature=0,
)
classifier = _classifier_llm.with_structured_output(ServiceRequest311)

_responder_llm = AzureChatOpenAI(
    azure_deployment=settings.azure_deployment_responder,
    azure_endpoint=settings.azure_openai_endpoint,
    api_key=settings.azure_openai_api_key,
    api_version=settings.azure_openai_api_version,
    temperature=0.7,
)


async def classify_message(text: str) -> ServiceRequest311:
    result = await classifier.ainvoke(
        [SystemMessage(content=CLASSIFIER_SYSTEM_PROMPT), HumanMessage(content=text)]
    )
    return result


async def generate_response(category: str, location: str, urgency: int) -> str:
    prompt = (
        f"The citizen reported: {category} at {location} (urgency {urgency}/5). "
        "Generate a confirmation SMS."
    )
    result = await _responder_llm.ainvoke(
        [SystemMessage(content=RESPONDER_SYSTEM_PROMPT), HumanMessage(content=prompt)]
    )
    return result.content
