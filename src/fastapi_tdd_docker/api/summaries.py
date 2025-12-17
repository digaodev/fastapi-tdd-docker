"""Summary API endpoints."""

import logging
from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, status

from fastapi_tdd_docker.api import crud
from fastapi_tdd_docker.dependencies import SessionDep
from fastapi_tdd_docker.logging_config import log_message
from fastapi_tdd_docker.models.schemas import (
    SummaryPayloadSchema,
    SummaryResponseSchema,
    SummaryUpdateSchema,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=SummaryResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_summary(
    payload: SummaryPayloadSchema, session: SessionDep
) -> SummaryResponseSchema:
    """Create a new text summary.

    Args:
        payload: The summary creation payload containing the URL
        session: Database session (injected)

    Returns:
        The created summary with ID
    """
    logger.info(log_message("Creating summary", url=str(payload.url)))

    summary = await crud.create_summary(session, payload)

    return SummaryResponseSchema.model_validate(summary)


@router.get("/{summary_id}", response_model=SummaryResponseSchema)
async def get_summary(
    summary_id: Annotated[int, Path(gt=0)], session: SessionDep
) -> SummaryResponseSchema:
    """Get a single summary by ID.

    Args:
        summary_id: The ID of the summary to retrieve (must be > 0)
        session: Database session (injected)

    Returns:
        The requested summary

    Raises:
        HTTPException: 404 if summary not found
        HTTPException: 422 if summary_id <= 0
    """
    summary = await crud.get_summary(session, summary_id)

    if not summary:
        logger.warning(log_message("Summary not found", summary_id=summary_id))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Summary not found")

    return SummaryResponseSchema.model_validate(summary)


@router.get("/", response_model=list[SummaryResponseSchema])
async def get_all_summaries(session: SessionDep) -> list[SummaryResponseSchema]:
    """Get all summaries.

    Args:
        session: Database session (injected)

    Returns:
        List of all summaries
    """
    summaries = await crud.get_all_summaries(session)

    return [SummaryResponseSchema.model_validate(s) for s in summaries]


@router.put("/{summary_id}", response_model=SummaryResponseSchema)
async def update_summary(
    payload: SummaryUpdateSchema,
    summary_id: Annotated[int, Path(gt=0)],
    session: SessionDep,
) -> SummaryResponseSchema:
    """Update an existing summary.

    Args:
        payload: The summary update payload (URL and summary text)
        summary_id: The ID of the summary to update (must be > 0)
        session: Database session (injected)

    Returns:
        The updated summary

    Raises:
        HTTPException: 404 if summary not found
        HTTPException: 422 if summary_id <= 0 or invalid URL
    """
    logger.info(log_message("Updating summary", summary_id=summary_id, url=str(payload.url)))

    summary = await crud.update_summary(session, summary_id, payload)

    if not summary:
        logger.warning(log_message("Summary not found for update", summary_id=summary_id))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Summary not found")

    return SummaryResponseSchema.model_validate(summary)


@router.delete("/{summary_id}", response_model=SummaryResponseSchema)
async def delete_summary(
    summary_id: Annotated[int, Path(gt=0)], session: SessionDep
) -> SummaryResponseSchema:
    """Delete a summary.

    Args:
        summary_id: The ID of the summary to delete (must be > 0)
        session: Database session (injected)

    Returns:
        The deleted summary

    Raises:
        HTTPException: 404 if summary not found
        HTTPException: 422 if summary_id <= 0
    """
    logger.info(log_message("Deleting summary", summary_id=summary_id))

    summary = await crud.delete_summary(session, summary_id)

    if not summary:
        logger.warning(log_message("Summary not found for deletion", summary_id=summary_id))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Summary not found")

    return SummaryResponseSchema.model_validate(summary)
