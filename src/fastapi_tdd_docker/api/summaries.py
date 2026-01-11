"""Summary API endpoints."""

import logging
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, HTTPException, Path, status

from fastapi_tdd_docker.api import crud
from fastapi_tdd_docker.dependencies import SessionDep
from fastapi_tdd_docker.logging_config import log_message
from fastapi_tdd_docker.models.schemas import (
    SummaryPayloadSchema,
    SummaryResponseSchema,
    SummaryUpdateSchema,
)
from fastapi_tdd_docker.summarizer import generate_summary_task

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=SummaryResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_summary(
    payload: SummaryPayloadSchema,
    session: SessionDep,
    background_tasks: BackgroundTasks,
) -> SummaryResponseSchema:
    """Create a new text summary and start background summarization.

    The summary is created immediately with status='pending' and an empty summary.
    A background task is scheduled to fetch the article and generate the summary.
    The client can poll GET /summaries/{id} to check the status.

    Args:
        payload: The summary creation payload containing the URL
        session: Database session (injected)
        background_tasks: FastAPI background tasks (injected)

    Returns:
        The created summary with ID and status='pending'
    """
    logger.info(log_message("Creating summary", url=str(payload.url)))

    summary = await crud.create_summary(session, payload)

    # Mypy type narrowing: summary.id is guaranteed to exist after database commit
    assert summary.id is not None, "Summary ID should exist after database commit"

    # Schedule background task to generate summary
    background_tasks.add_task(generate_summary_task, summary.id, str(payload.url))

    logger.info(
        log_message("Scheduled summarization task", summary_id=summary.id, url=str(payload.url))
    )

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
