import json
import logging
from typing import List, Optional
from datetime import datetime, date

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from services.drafts import DraftsService
from dependencies.auth import get_current_user
from schemas.auth import UserResponse

# Set up logging
logger = logging.getLogger(__name__)

# ---------- Entity CRUD Router (auto-generated compatible) ----------
router = APIRouter(prefix="/api/v1/entities/drafts", tags=["drafts"])


# ---------- Pydantic Schemas ----------
class DraftsData(BaseModel):
    """Entity data schema (for create/update)"""
    draft_data: str = None
    case_number: str = None
    draft_status: str = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class DraftsUpdateData(BaseModel):
    """Update entity data (partial updates allowed)"""
    draft_data: Optional[str] = None
    case_number: Optional[str] = None
    draft_status: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class DraftsResponse(BaseModel):
    """Entity response schema"""
    id: int
    user_id: str
    draft_data: Optional[str] = None
    case_number: Optional[str] = None
    draft_status: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DraftsListResponse(BaseModel):
    """List response schema"""
    items: List[DraftsResponse]
    total: int
    skip: int
    limit: int


class DraftsBatchCreateRequest(BaseModel):
    """Batch create request"""
    items: List[DraftsData]


class DraftsBatchUpdateItem(BaseModel):
    """Batch update item"""
    id: int
    updates: DraftsUpdateData


class DraftsBatchUpdateRequest(BaseModel):
    """Batch update request"""
    items: List[DraftsBatchUpdateItem]


class DraftsBatchDeleteRequest(BaseModel):
    """Batch delete request"""
    ids: List[int]


# ---------- Entity CRUD Routes ----------
@router.get("", response_model=DraftsListResponse)
async def query_draftss(
    query: str = Query(None, description="Query conditions (JSON string)"),
    sort: str = Query(None, description="Sort field (prefix with '-' for descending)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=2000, description="Max number of records to return"),
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Query draftss with filtering, sorting, and pagination"""
    service = DraftsService(db)
    try:
        query_dict = None
        if query:
            try:
                query_dict = json.loads(query)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid query JSON format")
        result = await service.get_list(
            skip=skip, limit=limit, query_dict=query_dict, sort=sort,
            user_id=str(current_user.id),
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying draftss: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/all", response_model=DraftsListResponse)
async def query_draftss_all(
    query: str = Query(None, description="Query conditions (JSON string)"),
    sort: str = Query(None, description="Sort field (prefix with '-' for descending)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=2000, description="Max number of records to return"),
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: AsyncSession = Depends(get_db),
):
    service = DraftsService(db)
    try:
        query_dict = None
        if query:
            try:
                query_dict = json.loads(query)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid query JSON format")
        result = await service.get_list(skip=skip, limit=limit, query_dict=query_dict, sort=sort)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying draftss: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{id}", response_model=DraftsResponse)
async def get_drafts(
    id: int,
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = DraftsService(db)
    try:
        result = await service.get_by_id(id, user_id=str(current_user.id))
        if not result:
            raise HTTPException(status_code=404, detail="Drafts not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching drafts {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("", response_model=DraftsResponse, status_code=201)
async def create_drafts(
    data: DraftsData,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = DraftsService(db)
    try:
        result = await service.create(data.model_dump(), user_id=str(current_user.id))
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create drafts")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating drafts: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/batch", response_model=List[DraftsResponse], status_code=201)
async def create_draftss_batch(
    request: DraftsBatchCreateRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = DraftsService(db)
    results = []
    try:
        for item_data in request.items:
            result = await service.create(item_data.model_dump(), user_id=str(current_user.id))
            if result:
                results.append(result)
        return results
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch create: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch create failed: {str(e)}")


@router.put("/batch", response_model=List[DraftsResponse])
async def update_draftss_batch(
    request: DraftsBatchUpdateRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = DraftsService(db)
    results = []
    try:
        for item in request.items:
            update_dict = {k: v for k, v in item.updates.model_dump().items() if v is not None}
            result = await service.update(item.id, update_dict, user_id=str(current_user.id))
            if result:
                results.append(result)
        return results
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch update: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch update failed: {str(e)}")


@router.put("/{id}", response_model=DraftsResponse)
async def update_drafts(
    id: int,
    data: DraftsUpdateData,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = DraftsService(db)
    try:
        update_dict = {k: v for k, v in data.model_dump().items() if v is not None}
        result = await service.update(id, update_dict, user_id=str(current_user.id))
        if not result:
            raise HTTPException(status_code=404, detail="Drafts not found")
        return result
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating drafts {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/batch")
async def delete_draftss_batch(
    request: DraftsBatchDeleteRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = DraftsService(db)
    deleted_count = 0
    try:
        for item_id in request.ids:
            success = await service.delete(item_id, user_id=str(current_user.id))
            if success:
                deleted_count += 1
        return {"message": f"Successfully deleted {deleted_count} draftss", "deleted_count": deleted_count}
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch delete: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch delete failed: {str(e)}")


@router.delete("/{id}")
async def delete_drafts(
    id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = DraftsService(db)
    try:
        success = await service.delete(id, user_id=str(current_user.id))
        if not success:
            raise HTTPException(status_code=404, detail="Drafts not found")
        return {"message": "Drafts deleted successfully", "id": id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting drafts {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ==========================================================================
# Custom endpoints used by the frontend (prefix: /api/v1/drafts)
# The main.py auto-discovery picks up "router" and "admin_router" attributes.
# ==========================================================================
admin_router = APIRouter(prefix="/api/v1/drafts", tags=["drafts-custom"])


class DraftSaveRequest(BaseModel):
    draft_data: str  # JSON string of the full form state
    case_number: Optional[str] = None


class DraftCustomResponse(BaseModel):
    id: int
    draft_data: str
    case_number: Optional[str] = None
    updated_at: Optional[str] = None


@admin_router.get("/latest", response_model=Optional[DraftCustomResponse])
async def get_latest_draft(
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the latest draft for the current user"""
    try:
        result = await db.execute(
            text(
                "SELECT id, draft_data, case_number, updated_at "
                "FROM drafts "
                "WHERE user_id = :user_id AND draft_status = 'draft' "
                "ORDER BY updated_at DESC LIMIT 1"
            ),
            {"user_id": str(current_user.id)},
        )
        row = result.fetchone()
        if not row:
            return None

        return DraftCustomResponse(
            id=row[0],
            draft_data=row[1] or "{}",
            case_number=row[2],
            updated_at=str(row[3]) if row[3] else None,
        )
    except Exception as e:
        logger.error(f"Error fetching latest draft: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@admin_router.post("/save", response_model=DraftCustomResponse)
async def save_draft(
    data: DraftSaveRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Save or update a draft. Upserts the latest draft for this user."""
    try:
        now = datetime.now().isoformat()
        user_id = str(current_user.id)

        # Check if user already has a draft
        result = await db.execute(
            text(
                "SELECT id FROM drafts "
                "WHERE user_id = :user_id AND draft_status = 'draft' "
                "ORDER BY updated_at DESC LIMIT 1"
            ),
            {"user_id": user_id},
        )
        existing = result.fetchone()

        if existing:
            # Update existing draft
            draft_id = existing[0]
            await db.execute(
                text(
                    "UPDATE drafts SET draft_data = :draft_data, updated_at = :now "
                    "WHERE id = :id AND user_id = :user_id"
                ),
                {
                    "draft_data": data.draft_data,
                    "now": now,
                    "id": draft_id,
                    "user_id": user_id,
                },
            )
            await db.commit()
        else:
            # Create new draft row
            case_number = data.case_number or f"DRAFT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            await db.execute(
                text(
                    "INSERT INTO drafts (user_id, case_number, draft_status, draft_data, created_at, updated_at) "
                    "VALUES (:user_id, :case_number, 'draft', :draft_data, :now, :now)"
                ),
                {
                    "user_id": user_id,
                    "case_number": case_number,
                    "draft_data": data.draft_data,
                    "now": now,
                },
            )
            await db.commit()

            # Get the newly created draft id
            result = await db.execute(
                text(
                    "SELECT id FROM drafts "
                    "WHERE user_id = :user_id AND draft_status = 'draft' "
                    "ORDER BY updated_at DESC LIMIT 1"
                ),
                {"user_id": user_id},
            )
            row = result.fetchone()
            draft_id = row[0] if row else 0

        return DraftCustomResponse(
            id=draft_id,
            draft_data=data.draft_data,
            case_number=data.case_number,
            updated_at=now,
        )
    except Exception as e:
        logger.error(f"Error saving draft: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@admin_router.post("/finalize/{draft_id}", response_model=dict)
async def finalize_draft(
    draft_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Convert a draft to a finalized case"""
    try:
        now = datetime.now().isoformat()
        user_id = str(current_user.id)

        await db.execute(
            text(
                "UPDATE drafts SET draft_status = 'final', updated_at = :now "
                "WHERE id = :id AND user_id = :user_id AND draft_status = 'draft'"
            ),
            {"now": now, "id": draft_id, "user_id": user_id},
        )
        await db.commit()
        return {"message": "Draft finalized", "id": draft_id}
    except Exception as e:
        logger.error(f"Error finalizing draft: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@admin_router.delete("/{draft_id}")
async def delete_draft(
    draft_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a draft"""
    try:
        user_id = str(current_user.id)
        await db.execute(
            text(
                "DELETE FROM drafts WHERE id = :id AND user_id = :user_id AND draft_status = 'draft'"
            ),
            {"id": draft_id, "user_id": user_id},
        )
        await db.commit()
        return {"message": "Draft deleted", "id": draft_id}
    except Exception as e:
        logger.error(f"Error deleting draft: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))