from datetime import date, datetime

from pydantic import BaseModel, computed_field, model_validator


class ServiceRequestOut(BaseModel):
    id: int
    reference_number: str
    category: str
    description: str
    location: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    urgency: int
    status: str
    phone: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def mask_phone_number(cls, data: object) -> object:
        if hasattr(data, "phone_number"):
            raw = data.phone_number or ""
            data = {
                "id": data.id,
                "reference_number": data.reference_number,
                "category": data.category,
                "description": data.description,
                "location": data.location,
                "latitude": float(data.latitude) if data.latitude is not None else None,
                "longitude": float(data.longitude) if data.longitude is not None else None,
                "urgency": data.urgency,
                "status": data.status,
                "phone": raw[:-4] + "****" if len(raw) >= 4 else "****",
                "created_at": data.created_at,
                "updated_at": data.updated_at,
            }
        return data


class MessageOut(BaseModel):
    id: int
    direction: str
    body: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ServiceRequestDetailOut(ServiceRequestOut):
    messages: list[MessageOut] = []


class ServiceRequestListOut(BaseModel):
    items: list[ServiceRequestOut]
    total: int
    limit: int
    offset: int


class AnalyticsSummaryOut(BaseModel):
    total_requests: int
    by_status: dict[str, int]
    by_category: dict[str, int]


class TrendPointOut(BaseModel):
    date: date
    count: int


class AnalyticsTrendOut(BaseModel):
    days: int
    data: list[TrendPointOut]
