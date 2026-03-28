"""Azure AI Search index schema — create and manage the 'contracts' index."""

import logging

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
    SimpleField,
)

from app.config import settings

logger = logging.getLogger(__name__)


def _get_index_client() -> SearchIndexClient:
    return SearchIndexClient(
        endpoint=settings.azure_search_endpoint,
        credential=AzureKeyCredential(settings.azure_search_key),
    )


def get_index_definition() -> SearchIndex:
    """Build the index schema for procurement documents."""
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True, filterable=True),
        SearchableField(name="title", type=SearchFieldDataType.String),
        SearchableField(name="vendor_name", type=SearchFieldDataType.String, filterable=True, sortable=True, facetable=True),
        SimpleField(name="document_type", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SimpleField(name="status", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SearchableField(name="primary_department", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SearchField(name="department_tags", type=SearchFieldDataType.Collection(SearchFieldDataType.String), searchable=True, filterable=True, facetable=True),
        SimpleField(name="total_amount", type=SearchFieldDataType.Double, filterable=True, sortable=True),
        SearchableField(name="scope_summary", type=SearchFieldDataType.String),
        SearchableField(name="ocr_text", type=SearchFieldDataType.String),
        SimpleField(name="effective_date", type=SearchFieldDataType.DateTimeOffset, filterable=True, sortable=True),
        SimpleField(name="expiration_date", type=SearchFieldDataType.DateTimeOffset, filterable=True, sortable=True),
        SimpleField(name="procurement_method", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SimpleField(name="mbe_wbe_required", type=SearchFieldDataType.Boolean, filterable=True, facetable=True),
        SimpleField(name="federal_funding", type=SearchFieldDataType.Boolean, filterable=True, facetable=True),
        SearchField(name="compliance_flags", type=SearchFieldDataType.Collection(SearchFieldDataType.String), searchable=True, filterable=True, facetable=True),
        SimpleField(name="source", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SimpleField(name="upload_date", type=SearchFieldDataType.DateTimeOffset, filterable=True, sortable=True),
        # Extra fields for richer context in search results
        SearchableField(name="issuing_department", type=SearchFieldDataType.String, filterable=True),
        SearchableField(name="contract_type", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="document_number", type=SearchFieldDataType.String, filterable=True),
        SearchableField(name="renewal_clause", type=SearchFieldDataType.String),
        # Document intelligence fields (from AI analysis)
        SearchableField(name="executive_summary", type=SearchFieldDataType.String),
        SearchableField(name="risk_assessment_summary", type=SearchFieldDataType.String),
        SimpleField(name="overall_risk_level", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SearchableField(name="key_clauses_summary", type=SearchFieldDataType.String),
        SearchableField(name="financial_intelligence_summary", type=SearchFieldDataType.String),
    ]

    semantic_config = SemanticConfiguration(
        name="procurement-semantic",
        prioritized_fields=SemanticPrioritizedFields(
            title_field=SemanticField(field_name="title"),
            content_fields=[
                SemanticField(field_name="scope_summary"),
                SemanticField(field_name="executive_summary"),
                SemanticField(field_name="ocr_text"),
            ],
            keywords_fields=[
                SemanticField(field_name="vendor_name"),
                SemanticField(field_name="primary_department"),
            ],
        ),
    )

    semantic_search = SemanticSearch(configurations=[semantic_config])

    return SearchIndex(
        name=settings.azure_search_index,
        fields=fields,
        semantic_search=semantic_search,
    )


def create_or_update_index() -> str:
    """Create or update the search index. Returns the index name."""
    client = _get_index_client()
    index = get_index_definition()
    result = client.create_or_update_index(index)
    logger.info("Search index '%s' created/updated", result.name)
    return result.name


def delete_index() -> None:
    """Delete the search index (for full reindex scenarios)."""
    client = _get_index_client()
    client.delete_index(settings.azure_search_index)
    logger.info("Search index '%s' deleted", settings.azure_search_index)
