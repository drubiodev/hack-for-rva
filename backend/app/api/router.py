from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.conversation import Conversation, Message
from app.models.service_request import ServiceRequest
from app.schemas import (
    AnalyticsSummaryOut,
    AnalyticsTrendOut,
    ServiceRequestDetailOut,
    ServiceRequestListOut,
    ServiceRequestOut,
    TrendPointOut,
)

router = APIRouter(prefix="/api/v1")


@router.get(
    "/requests",
    response_model=ServiceRequestListOut,
    tags=["Requests"],
    summary="List service requests",
)
async def list_requests(
    status: str | None = Query(None),
    category: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> ServiceRequestListOut:
    query = select(ServiceRequest)
    count_query = select(func.count(ServiceRequest.id))

    if status:
        query = query.where(ServiceRequest.status == status)
        count_query = count_query.where(ServiceRequest.status == status)
    if category:
        query = query.where(ServiceRequest.category == category)
        count_query = count_query.where(ServiceRequest.category == category)

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    query = query.order_by(ServiceRequest.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    rows = result.scalars().all()

    return ServiceRequestListOut(
        items=[ServiceRequestOut.model_validate(r) for r in rows],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/requests/{request_id}",
    response_model=ServiceRequestDetailOut,
    tags=["Requests"],
    summary="Get a single service request",
)
async def get_request(
    request_id: int,
    db: AsyncSession = Depends(get_db),
) -> ServiceRequestDetailOut:
    result = await db.execute(
        select(ServiceRequest).where(ServiceRequest.id == request_id)
    )
    sr = result.scalar_one_or_none()
    if not sr:
        raise HTTPException(status_code=404, detail="Service request not found")

    conv_result = await db.execute(
        select(Conversation)
        .where(Conversation.service_request_id == request_id)
        .options(selectinload(Conversation.messages))
    )
    conversations = conv_result.scalars().all()

    all_messages = []
    for conv in conversations:
        for msg in conv.messages:
            all_messages.append(msg)
    all_messages.sort(key=lambda m: m.created_at)

    sr_data = ServiceRequestOut.model_validate(sr).model_dump()
    sr_data["messages"] = all_messages
    return ServiceRequestDetailOut.model_validate(sr_data)


@router.get(
    "/analytics/summary",
    response_model=AnalyticsSummaryOut,
    tags=["Analytics"],
    summary="Analytics KPI summary",
)
async def get_analytics_summary(
    db: AsyncSession = Depends(get_db),
) -> AnalyticsSummaryOut:
    total_result = await db.execute(select(func.count(ServiceRequest.id)))
    total = total_result.scalar_one()

    status_result = await db.execute(
        select(ServiceRequest.status, func.count(ServiceRequest.id)).group_by(
            ServiceRequest.status
        )
    )
    by_status = {row[0]: row[1] for row in status_result.all()}

    category_result = await db.execute(
        select(ServiceRequest.category, func.count(ServiceRequest.id)).group_by(
            ServiceRequest.category
        )
    )
    by_category = {row[0]: row[1] for row in category_result.all()}

    return AnalyticsSummaryOut(
        total_requests=total,
        by_status=by_status,
        by_category=by_category,
    )


@router.get(
    "/analytics/trend",
    response_model=AnalyticsTrendOut,
    tags=["Analytics"],
    summary="Daily request trend",
)
async def get_analytics_trend(
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
) -> AnalyticsTrendOut:
    today = date.today()
    start_date = today - timedelta(days=days - 1)
    start_dt = datetime(start_date.year, start_date.month, start_date.day, tzinfo=timezone.utc)

    result = await db.execute(
        select(
            func.date(ServiceRequest.created_at).label("day"),
            func.count(ServiceRequest.id).label("cnt"),
        )
        .where(ServiceRequest.created_at >= start_dt)
        .group_by(func.date(ServiceRequest.created_at))
    )
    counts_by_day = {row[0]: row[1] for row in result.all()}

    data = []
    for i in range(days):
        d = start_date + timedelta(days=i)
        count = counts_by_day.get(d, 0)
        data.append(TrendPointOut(date=d, count=count))

    return AnalyticsTrendOut(days=days, data=data)
