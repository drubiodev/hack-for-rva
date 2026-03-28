"""Search client — semantic search, query routing, and SQL intelligence queries."""

import json
import logging
from datetime import date, datetime, timedelta, timezone

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from openai import AsyncOpenAI
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.document import Document, ExtractedFields

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Query Router — classifies user intent via LLM
# ---------------------------------------------------------------------------

ROUTER_SYSTEM_PROMPT = """You are a query classifier for a City of Richmond procurement document system.
Given a user question, output JSON with:
{
  "intent": one of ["semantic_search", "aggregation", "filter_list", "compliance_check",
                     "expiration_alert", "vendor_lookup", "comparison", "general_knowledge"],
  "search_query": string or null (natural language query for semantic search),
  "sql_filters": {
    "department": string or null,
    "vendor": string or null,
    "document_type": string or null,
    "min_amount": number or null,
    "max_amount": number or null,
    "procurement_method": string or null
  },
  "aggregation": string or null ("sum", "count", "avg", "max", "min"),
  "aggregation_field": string or null ("total_amount", "document_count"),
  "group_by": string or null ("primary_department", "vendor_name", "document_type", "procurement_method"),
  "days_ahead": number or null (for expiration queries, e.g. 90)
}

Document types: rfp, rfq, contract, purchase_order, invoice, amendment, cooperative, other
Procurement methods: COMPETITIVE_BID, RFP, COOPERATIVE_PURCHASE, SOLE_SOURCE, EMERGENCY
Departments: DPU, DPW, Finance, IT, Parks, Police, Fire, General Services, etc.

Always output valid JSON only. No extra text."""


async def classify_intent(question: str) -> dict:
    """Use LLM to classify the user's question into an intent + parameters."""
    try:
        client = AsyncOpenAI(
            base_url=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_key,
        )
        response = await client.chat.completions.create(
            model=settings.azure_openai_deployment,
            messages=[
                {"role": "system", "content": ROUTER_SYSTEM_PROMPT},
                {"role": "user", "content": question},
            ],
            max_completion_tokens=300,
            temperature=0.0,
        )
        content = response.choices[0].message.content or "{}"
        # Strip markdown fences if present
        content = content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1] if "\n" in content else content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
        return json.loads(content)
    except Exception:
        logger.exception("Query classification failed, defaulting to semantic_search")
        return {"intent": "semantic_search", "search_query": question}


# ---------------------------------------------------------------------------
# Azure AI Search — semantic search
# ---------------------------------------------------------------------------

def _get_search_client() -> SearchClient:
    return SearchClient(
        endpoint=settings.azure_search_endpoint,
        index_name=settings.azure_search_index,
        credential=AzureKeyCredential(settings.azure_search_key),
    )


def _build_odata_filter(sql_filters: dict | None) -> str | None:
    """Build an OData filter string from the router's sql_filters."""
    if not sql_filters:
        return None

    parts = []
    if sql_filters.get("department"):
        dept = sql_filters["department"].replace("'", "''")
        parts.append(f"primary_department eq '{dept}'")
    if sql_filters.get("vendor"):
        vendor = sql_filters["vendor"].replace("'", "''")
        parts.append(f"vendor_name eq '{vendor}'")
    if sql_filters.get("document_type"):
        dt = sql_filters["document_type"].replace("'", "''")
        parts.append(f"document_type eq '{dt}'")
    if sql_filters.get("procurement_method"):
        pm = sql_filters["procurement_method"].replace("'", "''")
        parts.append(f"procurement_method eq '{pm}'")
    if sql_filters.get("min_amount") is not None:
        parts.append(f"total_amount ge {sql_filters['min_amount']}")
    if sql_filters.get("max_amount") is not None:
        parts.append(f"total_amount le {sql_filters['max_amount']}")

    return " and ".join(parts) if parts else None


async def semantic_search(
    query: str,
    filters: dict | None = None,
    top: int = 8,
) -> list[dict]:
    """Run a semantic search against Azure AI Search and return ranked results."""
    try:
        client = _get_search_client()
        odata_filter = _build_odata_filter(filters)

        results = client.search(
            search_text=query,
            query_type="semantic",
            semantic_configuration_name="procurement-semantic",
            filter=odata_filter,
            top=top,
            select="id,title,vendor_name,document_type,primary_department,total_amount,"
                   "scope_summary,effective_date,expiration_date,procurement_method,"
                   "compliance_flags,mbe_wbe_required,federal_funding,source,document_number,"
                   "executive_summary,overall_risk_level,risk_assessment_summary,"
                   "key_clauses_summary,financial_intelligence_summary",
            query_caption="extractive",
            query_answer="extractive",
        )

        hits = []
        for result in results:
            hit = {
                "id": result["id"],
                "title": result.get("title"),
                "vendor_name": result.get("vendor_name"),
                "document_type": result.get("document_type"),
                "primary_department": result.get("primary_department"),
                "total_amount": result.get("total_amount"),
                "scope_summary": result.get("scope_summary"),
                "effective_date": result.get("effective_date"),
                "expiration_date": result.get("expiration_date"),
                "procurement_method": result.get("procurement_method"),
                "document_number": result.get("document_number"),
                "executive_summary": result.get("executive_summary"),
                "overall_risk_level": result.get("overall_risk_level"),
                "risk_assessment_summary": result.get("risk_assessment_summary"),
                "key_clauses_summary": result.get("key_clauses_summary"),
                "financial_intelligence_summary": result.get("financial_intelligence_summary"),
                "relevance_score": result.get("@search.score", 0),
                "reranker_score": result.get("@search.reranker_score", 0),
            }

            # Extract captions if available
            captions = result.get("@search.captions")
            if captions:
                hit["caption"] = captions[0].text if captions[0].text else captions[0].highlights
            hits.append(hit)

        return hits
    except Exception:
        logger.exception("Azure AI Search query failed")
        return []


# ---------------------------------------------------------------------------
# Department alias mapping — common abbreviations to DB values
# ---------------------------------------------------------------------------

DEPARTMENT_ALIASES: dict[str, str] = {
    "dpu": "PUBLIC_UTILITIES",
    "dpw": "PUBLIC_WORKS",
    "public utilities": "PUBLIC_UTILITIES",
    "public works": "PUBLIC_WORKS",
    "water": "PUBLIC_UTILITIES",
    "utilities": "PUBLIC_UTILITIES",
    "it": "INFORMATION_TECHNOLOGY",
    "info tech": "INFORMATION_TECHNOLOGY",
    "hr": "HUMAN_RESOURCES",
    "human resources": "HUMAN_RESOURCES",
    "police": "PUBLIC_SAFETY",
    "fire": "PUBLIC_SAFETY",
    "public safety": "PUBLIC_SAFETY",
    "parks": "PARKS_RECREATION",
    "parks and rec": "PARKS_RECREATION",
    "finance": "FINANCE",
    "procurement": "PROCUREMENT",
    "planning": "PLANNING_DEVELOPMENT",
    "community dev": "COMMUNITY_DEVELOPMENT",
    "general services": "GENERAL_SERVICES",
    "risk": "RISK_MANAGEMENT",
}


def _resolve_department(name: str | None) -> str | None:
    """Resolve department aliases to canonical DB names."""
    if not name:
        return None
    lower = name.lower().strip()
    return DEPARTMENT_ALIASES.get(lower, name)


# ---------------------------------------------------------------------------
# SQL Intelligence Queries
# ---------------------------------------------------------------------------

async def sql_aggregation(
    db: AsyncSession,
    aggregation: str | None,
    aggregation_field: str | None,
    group_by: str | None,
    sql_filters: dict | None = None,
) -> list[dict]:
    """Run aggregation queries against the SQL database."""
    # Map allowed fields to prevent injection
    ALLOWED_GROUP_BY = {
        "primary_department": ExtractedFields.primary_department,
        "vendor_name": ExtractedFields.vendor_name,
        "document_type": Document.document_type,
        "procurement_method": ExtractedFields.procurement_method,
    }

    group_col = ALLOWED_GROUP_BY.get(group_by or "primary_department", ExtractedFields.primary_department)

    # Build the query
    query = (
        select(
            group_col.label("group_key"),
            func.count(Document.id).label("document_count"),
            func.sum(ExtractedFields.total_amount).label("total_value"),
            func.avg(ExtractedFields.total_amount).label("avg_value"),
            func.max(ExtractedFields.total_amount).label("max_value"),
        )
        .join(ExtractedFields, Document.id == ExtractedFields.document_id)
        .where(Document.status.notin_(["failed", "processing", "uploading", "error"]))
        .group_by(group_col)
        .order_by(func.sum(ExtractedFields.total_amount).desc())
    )

    # Apply filters
    if sql_filters:
        dept = _resolve_department(sql_filters.get("department"))
        if dept:
            query = query.where(ExtractedFields.primary_department.ilike(f"%{dept}%"))
        if sql_filters.get("vendor"):
            query = query.where(ExtractedFields.vendor_name.ilike(f"%{sql_filters['vendor']}%"))
        if sql_filters.get("document_type"):
            query = query.where(Document.document_type == sql_filters["document_type"])
        if sql_filters.get("procurement_method"):
            query = query.where(ExtractedFields.procurement_method == sql_filters["procurement_method"])
        if sql_filters.get("min_amount") is not None:
            query = query.where(ExtractedFields.total_amount >= sql_filters["min_amount"])
        if sql_filters.get("max_amount") is not None:
            query = query.where(ExtractedFields.total_amount <= sql_filters["max_amount"])

    result = await db.execute(query)
    rows = result.all()

    return [
        {
            "group": row.group_key or "Unknown",
            "document_count": row.document_count,
            "total_value": float(row.total_value) if row.total_value else 0,
            "avg_value": float(row.avg_value) if row.avg_value else 0,
            "max_value": float(row.max_value) if row.max_value else 0,
        }
        for row in rows
    ]


async def sql_expiring_contracts(
    db: AsyncSession,
    days_ahead: int = 90,
) -> list[dict]:
    """Find contracts expiring within N days."""
    today = date.today()
    cutoff = today + timedelta(days=days_ahead)

    result = await db.execute(
        select(Document, ExtractedFields)
        .join(ExtractedFields, Document.id == ExtractedFields.document_id)
        .where(ExtractedFields.expiration_date.isnot(None))
        .where(ExtractedFields.expiration_date >= today)
        .where(ExtractedFields.expiration_date <= cutoff)
        .where(Document.status.notin_(["failed", "processing", "uploading", "error"]))
        .order_by(ExtractedFields.expiration_date.asc())
        .limit(20)
    )
    rows = result.all()

    return [
        {
            "id": str(doc.id),
            "title": ef.title or doc.filename,
            "vendor_name": ef.vendor_name,
            "total_amount": float(ef.total_amount) if ef.total_amount else None,
            "expiration_date": str(ef.expiration_date),
            "days_until_expiry": (ef.expiration_date - today).days,
            "primary_department": ef.primary_department,
        }
        for doc, ef in rows
    ]


async def sql_compliance_gaps(db: AsyncSession) -> list[dict]:
    """Find documents with potential compliance issues."""
    result = await db.execute(
        select(Document, ExtractedFields)
        .join(ExtractedFields, Document.id == ExtractedFields.document_id)
        .where(Document.status.notin_(["failed", "processing", "uploading", "error"]))
        .where(
            (ExtractedFields.total_amount > 50000)
            & (
                (ExtractedFields.mbe_wbe_required.is_(None))
                | (ExtractedFields.insurance_general_liability_min.is_(None))
                | (ExtractedFields.procurement_method.is_(None))
            )
        )
        .order_by(ExtractedFields.total_amount.desc())
        .limit(20)
    )
    rows = result.all()

    gaps = []
    for doc, ef in rows:
        missing = []
        if ef.mbe_wbe_required is None:
            missing.append("mbe_wbe_required")
        if ef.insurance_general_liability_min is None:
            missing.append("insurance_general_liability_min")
        if ef.procurement_method is None:
            missing.append("procurement_method")
        gaps.append({
            "id": str(doc.id),
            "title": ef.title or doc.filename,
            "vendor_name": ef.vendor_name,
            "total_amount": float(ef.total_amount) if ef.total_amount else None,
            "primary_department": ef.primary_department,
            "missing_fields": missing,
        })
    return gaps


async def sql_vendor_concentration(db: AsyncSession) -> list[dict]:
    """Identify vendors with multiple contracts (concentration risk)."""
    result = await db.execute(
        select(
            ExtractedFields.vendor_name,
            func.count(Document.id).label("contract_count"),
            func.sum(ExtractedFields.total_amount).label("total_value"),
            func.min(ExtractedFields.expiration_date).label("earliest_expiry"),
        )
        .join(ExtractedFields, Document.id == ExtractedFields.document_id)
        .where(Document.status.notin_(["failed", "processing", "uploading", "error"]))
        .where(ExtractedFields.vendor_name.isnot(None))
        .group_by(ExtractedFields.vendor_name)
        .having(func.count(Document.id) > 1)
        .order_by(func.sum(ExtractedFields.total_amount).desc())
        .limit(20)
    )
    rows = result.all()

    return [
        {
            "vendor_name": row.vendor_name,
            "contract_count": row.contract_count,
            "total_value": float(row.total_value) if row.total_value else 0,
            "earliest_expiry": str(row.earliest_expiry) if row.earliest_expiry else None,
        }
        for row in rows
    ]


async def sql_filter_list(
    db: AsyncSession,
    sql_filters: dict | None = None,
    limit: int = 10,
) -> list[dict]:
    """Filter and list documents matching criteria."""
    query = (
        select(Document, ExtractedFields)
        .join(ExtractedFields, Document.id == ExtractedFields.document_id)
        .where(Document.status.notin_(["failed", "processing", "uploading", "error"]))
    )

    if sql_filters:
        dept = _resolve_department(sql_filters.get("department"))
        if dept:
            query = query.where(ExtractedFields.primary_department.ilike(f"%{dept}%"))
        if sql_filters.get("vendor"):
            query = query.where(ExtractedFields.vendor_name.ilike(f"%{sql_filters['vendor']}%"))
        if sql_filters.get("document_type"):
            query = query.where(Document.document_type == sql_filters["document_type"])
        if sql_filters.get("procurement_method"):
            query = query.where(ExtractedFields.procurement_method == sql_filters["procurement_method"])
        if sql_filters.get("min_amount") is not None:
            query = query.where(ExtractedFields.total_amount >= sql_filters["min_amount"])
        if sql_filters.get("max_amount") is not None:
            query = query.where(ExtractedFields.total_amount <= sql_filters["max_amount"])

    query = query.order_by(ExtractedFields.total_amount.desc()).limit(limit)
    result = await db.execute(query)
    rows = result.all()

    return [
        {
            "id": str(doc.id),
            "title": ef.title or doc.filename,
            "vendor_name": ef.vendor_name,
            "document_type": doc.document_type,
            "total_amount": float(ef.total_amount) if ef.total_amount else None,
            "primary_department": ef.primary_department,
            "expiration_date": str(ef.expiration_date) if ef.expiration_date else None,
            "procurement_method": ef.procurement_method,
            "status": doc.status,
        }
        for doc, ef in rows
    ]


# ---------------------------------------------------------------------------
# Source helpers
# ---------------------------------------------------------------------------


def _doc_caption(doc: dict) -> str | None:
    """Build a one-line caption from document fields for source chips."""
    parts = []
    if doc.get("vendor_name"):
        parts.append(doc["vendor_name"])
    if doc.get("total_amount"):
        parts.append(f"${doc['total_amount']:,.0f}")
    if doc.get("primary_department"):
        parts.append(doc["primary_department"].replace("_", " ").title())
    if doc.get("expiration_date"):
        parts.append(f"exp {doc['expiration_date']}")
    if doc.get("overall_risk_level") and doc["overall_risk_level"] in ("high", "critical"):
        parts.append(f"RISK: {doc['overall_risk_level'].upper()}")
    return " — ".join(parts) if parts else None


def _deduplicate_sources(sources: list[dict], max_count: int = 8) -> list[dict]:
    """Deduplicate by document ID, keep highest relevance, cap at max_count."""
    seen: dict[str, dict] = {}
    for src in sources:
        doc_id = src.get("id")
        if not doc_id:
            continue
        existing = seen.get(doc_id)
        if not existing or src.get("relevance", 0) > existing.get("relevance", 0):
            seen[doc_id] = src
    ranked = sorted(seen.values(), key=lambda s: s.get("relevance", 0), reverse=True)
    return ranked[:max_count]


# ---------------------------------------------------------------------------
# Orchestrator — routes intent to the right execution path
# ---------------------------------------------------------------------------

async def execute_query(
    question: str,
    db: AsyncSession,
    conversation_history: list[dict] | None = None,
    document_id: str | None = None,
) -> dict:
    """Main entry point: classify intent, execute, return structured result."""
    classification = await classify_intent(question)
    intent = classification.get("intent", "semantic_search")
    sql_filters = classification.get("sql_filters")
    search_query = classification.get("search_query") or question

    logger.info("Query classified as '%s': %s", intent, json.dumps(classification, default=str))

    context_parts = []
    sources = []

    # --- Inject focused document context when user is on a specific document page ---
    if document_id:
        try:
            result = await db.execute(
                select(Document, ExtractedFields)
                .join(ExtractedFields, Document.id == ExtractedFields.document_id)
                .where(Document.id == document_id)
            )
            row = result.one_or_none()
            if row:
                doc, ef = row
                intel = (doc.ocr_metadata or {}).get("intelligence", {})
                risk = intel.get("risk_assessment", {})

                amount_str = f"${float(ef.total_amount):,.2f}" if ef.total_amount else "N/A"
                doc_context = (
                    f"=== CURRENT DOCUMENT (user is viewing this) ===\n"
                    f"Title: {ef.title or doc.filename}\n"
                    f"Vendor: {ef.vendor_name or 'N/A'}\n"
                    f"Department: {ef.primary_department or ef.issuing_department or 'N/A'}\n"
                    f"Type: {doc.document_type or 'N/A'}\n"
                    f"Amount: {amount_str}\n"
                    f"Effective: {ef.effective_date or 'N/A'} — Expires: {ef.expiration_date or 'N/A'}\n"
                    f"Status: {doc.status}\n"
                    f"Procurement Method: {ef.procurement_method or 'N/A'}\n"
                )
                if intel.get("executive_summary"):
                    doc_context += f"Executive Summary: {intel['executive_summary']}\n"
                if risk.get("overall_risk_level"):
                    doc_context += f"Risk Level: {risk['overall_risk_level']}\n"
                if risk.get("risk_factors"):
                    doc_context += f"Risk Factors: {'; '.join(risk['risk_factors'])}\n"
                if intel.get("key_clauses"):
                    clauses = intel["key_clauses"]
                    for k in ["termination_conditions", "renewal_terms", "indemnification", "force_majeure", "liquidated_damages"]:
                        if clauses.get(k):
                            doc_context += f"{k.replace('_', ' ').title()}: {clauses[k]}\n"
                if intel.get("financial_intelligence"):
                    fin = intel["financial_intelligence"]
                    for k in ["cost_breakdown", "escalation_clauses", "budget_impact"]:
                        if fin.get(k):
                            doc_context += f"{k.replace('_', ' ').title()}: {fin[k]}\n"
                if intel.get("compliance_intelligence"):
                    comp = intel["compliance_intelligence"]
                    for k in ["mbe_wbe_summary", "federal_funding_implications", "prevailing_wage"]:
                        if comp.get(k):
                            doc_context += f"{k.replace('_', ' ').title()}: {comp[k]}\n"
                if ef.scope_summary:
                    doc_context += f"Scope: {ef.scope_summary}\n"
                if ef.renewal_clause:
                    doc_context += f"Renewal Clause: {ef.renewal_clause}\n"
                doc_context += "=== END CURRENT DOCUMENT ===\n"

                context_parts.append(doc_context)
                sources.append({
                    "id": str(doc.id),
                    "title": ef.title or doc.filename,
                    "relevance": 1.0,
                    "caption": f"{ef.vendor_name or ''} — {amount_str}",
                })
        except Exception as e:
            logger.warning("Failed to load document context for %s: %s", document_id, e)

    if intent == "aggregation":
        agg_results = await sql_aggregation(
            db,
            aggregation=classification.get("aggregation"),
            aggregation_field=classification.get("aggregation_field"),
            group_by=classification.get("group_by"),
            sql_filters=sql_filters,
        )
        for row in agg_results:
            context_parts.append(
                f"{row['group']}: {row['document_count']} documents, "
                f"total ${row['total_value']:,.2f}, avg ${row['avg_value']:,.2f}"
            )

        # Fetch top backing documents so the user can drill into the data
        backing_docs = await sql_filter_list(db, sql_filters=sql_filters, limit=8)
        for doc in backing_docs:
            sources.append({
                "id": doc["id"],
                "title": doc["title"],
                "relevance": 0.9,
                "caption": _doc_caption(doc),
            })

    elif intent == "expiration_alert":
        days = classification.get("days_ahead") or 90
        expiring = await sql_expiring_contracts(db, days_ahead=days)
        for doc in expiring:
            caption = f"{doc['vendor_name'] or 'N/A'} — expires {doc['expiration_date']} ({doc['days_until_expiry']}d)"
            if doc.get("total_amount"):
                caption += f" — ${doc['total_amount']:,.0f}"
            sources.append({"id": doc["id"], "title": doc["title"], "relevance": 0.95, "caption": caption})
            context_parts.append(
                f"{doc['title']} — {doc['vendor_name'] or 'N/A'}, "
                f"expires {doc['expiration_date']} ({doc['days_until_expiry']} days), "
                f"${doc['total_amount']:,.2f}" if doc['total_amount'] else
                f"{doc['title']} — {doc['vendor_name'] or 'N/A'}, "
                f"expires {doc['expiration_date']} ({doc['days_until_expiry']} days)"
            )

    elif intent == "compliance_check":
        gaps = await sql_compliance_gaps(db)
        for doc in gaps:
            caption = f"{doc['vendor_name'] or 'N/A'} — missing: {', '.join(doc['missing_fields'])}"
            sources.append({"id": doc["id"], "title": doc["title"], "relevance": 0.9, "caption": caption})
            context_parts.append(
                f"{doc['title']} ({doc['vendor_name'] or 'N/A'}): "
                f"missing {', '.join(doc['missing_fields'])}, "
                f"amount ${doc['total_amount']:,.2f}" if doc['total_amount'] else
                f"{doc['title']} ({doc['vendor_name'] or 'N/A'}): "
                f"missing {', '.join(doc['missing_fields'])}"
            )

    elif intent == "vendor_lookup":
        # Combine SQL filter + semantic search for vendor queries
        filtered = await sql_filter_list(db, sql_filters=sql_filters, limit=10)
        for doc in filtered:
            sources.append({"id": doc["id"], "title": doc["title"], "relevance": 0.85, "caption": _doc_caption(doc)})
            amount_str = f"${doc['total_amount']:,.2f}" if doc['total_amount'] else "N/A"
            context_parts.append(
                f"{doc['title']} — {doc['vendor_name'] or 'N/A'}, "
                f"{doc['document_type'] or 'unknown'}, {amount_str}, "
                f"dept: {doc['primary_department'] or 'N/A'}"
            )

    elif intent == "filter_list":
        filtered = await sql_filter_list(db, sql_filters=sql_filters, limit=10)
        for doc in filtered:
            sources.append({"id": doc["id"], "title": doc["title"], "relevance": 0.85, "caption": _doc_caption(doc)})
            amount_str = f"${doc['total_amount']:,.2f}" if doc['total_amount'] else "N/A"
            context_parts.append(
                f"{doc['title']} — {doc['vendor_name'] or 'N/A'}, "
                f"{doc['document_type'] or 'unknown'}, {amount_str}, "
                f"expires: {doc['expiration_date'] or 'N/A'}"
            )

    elif intent == "general_knowledge":
        # No retrieval needed — LLM answers directly
        context_parts.append("(No document retrieval needed — answer from general procurement knowledge)")

    else:
        # Default: semantic_search, comparison, or unknown → Azure AI Search
        hits = await semantic_search(search_query, filters=sql_filters, top=8)
        if not hits:
            # Fallback to SQL filter
            hits_sql = await sql_filter_list(db, sql_filters=sql_filters, limit=8)
            for doc in hits_sql:
                sources.append({"id": doc["id"], "title": doc["title"], "relevance": 0.7, "caption": _doc_caption(doc)})
                amount_str = f"${doc['total_amount']:,.2f}" if doc['total_amount'] else "N/A"
                context_parts.append(
                    f"{doc['title']} — {doc['vendor_name'] or 'N/A'}, "
                    f"{amount_str}, dept: {doc['primary_department'] or 'N/A'}"
                )
        else:
            for hit in hits:
                # Use reranker score if available, otherwise search score normalized
                relevance = hit.get("reranker_score") or min(hit.get("relevance_score", 0) / 10, 1.0)
                sources.append({
                    "id": hit["id"],
                    "title": hit.get("title"),
                    "relevance": round(relevance, 3),
                    "caption": hit.get("caption"),
                })
                amount_str = f"${hit['total_amount']:,.2f}" if hit.get("total_amount") else "N/A"
                context_parts.append(
                    f"[{hit.get('title')}] Vendor: {hit.get('vendor_name') or 'N/A'}, "
                    f"Dept: {hit.get('primary_department') or 'N/A'}, "
                    f"Amount: {amount_str}, "
                    f"Type: {hit.get('document_type') or 'N/A'}, "
                    f"Method: {hit.get('procurement_method') or 'N/A'}, "
                    f"Expires: {hit.get('expiration_date') or 'N/A'}, "
                    f"Risk: {hit.get('overall_risk_level') or 'N/A'}"
                    + (f"\nSummary: {hit.get('executive_summary')}" if hit.get("executive_summary")
                       else (f"\nSummary: {hit.get('scope_summary')}" if hit.get("scope_summary") else ""))
                    + (f"\nRisk Analysis: {hit.get('risk_assessment_summary')}" if hit.get("risk_assessment_summary") else "")
                    + (f"\nKey Clauses: {hit.get('key_clauses_summary')}" if hit.get("key_clauses_summary") else "")
                    + (f"\nFinancial: {hit.get('financial_intelligence_summary')}" if hit.get("financial_intelligence_summary") else "")
                    + (f"\nCaption: {hit.get('caption')}" if hit.get("caption") else "")
                )

    return {
        "intent": intent,
        "classification": classification,
        "context": "\n\n".join(context_parts),
        "sources": _deduplicate_sources(sources),
    }
