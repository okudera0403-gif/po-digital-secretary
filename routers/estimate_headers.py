import json
import logging
from typing import List, Optional

from datetime import datetime, date

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from services.estimate_headers import Estimate_headersService
from dependencies.auth import get_current_user
from schemas.auth import UserResponse

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/entities/estimate_headers", tags=["estimate_headers"])


# ---------- Pydantic Schemas ----------
class Estimate_headersData(BaseModel):
    """Entity data schema (for create/update)"""
    case_id: int = None
    category_name: str = None
    product_name: str = None
    product_code: str = None
    type_name: str = None
    side: str = None
    insurance_name: str = None
    base_price: int = None
    joint_total: int = None
    support_total: int = None
    foot_total: int = None
    addon_total: int = None
    parts_total: int = None
    grand_total: int = None
    notes: str = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Estimate_headersUpdateData(BaseModel):
    """Update entity data (partial updates allowed)"""
    case_id: Optional[int] = None
    category_name: Optional[str] = None
    product_name: Optional[str] = None
    product_code: Optional[str] = None
    type_name: Optional[str] = None
    side: Optional[str] = None
    insurance_name: Optional[str] = None
    base_price: Optional[int] = None
    joint_total: Optional[int] = None
    support_total: Optional[int] = None
    foot_total: Optional[int] = None
    addon_total: Optional[int] = None
    parts_total: Optional[int] = None
    grand_total: Optional[int] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Estimate_headersResponse(BaseModel):
    """Entity response schema"""
    id: int
    user_id: str
    case_id: Optional[int] = None
    category_name: Optional[str] = None
    product_name: Optional[str] = None
    product_code: Optional[str] = None
    type_name: Optional[str] = None
    side: Optional[str] = None
    insurance_name: Optional[str] = None
    base_price: Optional[int] = None
    joint_total: Optional[int] = None
    support_total: Optional[int] = None
    foot_total: Optional[int] = None
    addon_total: Optional[int] = None
    parts_total: Optional[int] = None
    grand_total: Optional[int] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Estimate_headersListResponse(BaseModel):
    """List response schema"""
    items: List[Estimate_headersResponse]
    total: int
    skip: int
    limit: int


class Estimate_headersBatchCreateRequest(BaseModel):
    """Batch create request"""
    items: List[Estimate_headersData]


class Estimate_headersBatchUpdateItem(BaseModel):
    """Batch update item"""
    id: int
    updates: Estimate_headersUpdateData


class Estimate_headersBatchUpdateRequest(BaseModel):
    """Batch update request"""
    items: List[Estimate_headersBatchUpdateItem]


class Estimate_headersBatchDeleteRequest(BaseModel):
    """Batch delete request"""
    ids: List[int]


# ---------- Routes ----------
@router.get("", response_model=Estimate_headersListResponse)
async def query_estimate_headerss(
    query: str = Query(None, description="Query conditions (JSON string)"),
    sort: str = Query(None, description="Sort field (prefix with '-' for descending)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=2000, description="Max number of records to return"),
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Query estimate_headerss with filtering, sorting, and pagination (user can only see their own records)"""
    logger.debug(f"Querying estimate_headerss: query={query}, sort={sort}, skip={skip}, limit={limit}, fields={fields}")
    
    service = Estimate_headersService(db)
    try:
        # Parse query JSON if provided
        query_dict = None
        if query:
            try:
                query_dict = json.loads(query)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid query JSON format")
        
        result = await service.get_list(
            skip=skip, 
            limit=limit,
            query_dict=query_dict,
            sort=sort,
            user_id=str(current_user.id),
        )
        logger.debug(f"Found {result['total']} estimate_headerss")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying estimate_headerss: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/all", response_model=Estimate_headersListResponse)
async def query_estimate_headerss_all(
    query: str = Query(None, description="Query conditions (JSON string)"),
    sort: str = Query(None, description="Sort field (prefix with '-' for descending)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=2000, description="Max number of records to return"),
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: AsyncSession = Depends(get_db),
):
    # Query estimate_headerss with filtering, sorting, and pagination without user limitation
    logger.debug(f"Querying estimate_headerss: query={query}, sort={sort}, skip={skip}, limit={limit}, fields={fields}")

    service = Estimate_headersService(db)
    try:
        # Parse query JSON if provided
        query_dict = None
        if query:
            try:
                query_dict = json.loads(query)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid query JSON format")

        result = await service.get_list(
            skip=skip,
            limit=limit,
            query_dict=query_dict,
            sort=sort
        )
        logger.debug(f"Found {result['total']} estimate_headerss")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying estimate_headerss: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{id}", response_model=Estimate_headersResponse)
async def get_estimate_headers(
    id: int,
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single estimate_headers by ID (user can only see their own records)"""
    logger.debug(f"Fetching estimate_headers with id: {id}, fields={fields}")
    
    service = Estimate_headersService(db)
    try:
        result = await service.get_by_id(id, user_id=str(current_user.id))
        if not result:
            logger.warning(f"Estimate_headers with id {id} not found")
            raise HTTPException(status_code=404, detail="Estimate_headers not found")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching estimate_headers {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("", response_model=Estimate_headersResponse, status_code=201)
async def create_estimate_headers(
    data: Estimate_headersData,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new estimate_headers"""
    logger.debug(f"Creating new estimate_headers with data: {data}")
    
    service = Estimate_headersService(db)
    try:
        result = await service.create(data.model_dump(), user_id=str(current_user.id))
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create estimate_headers")
        
        logger.info(f"Estimate_headers created successfully with id: {result.id}")
        return result
    except ValueError as e:
        logger.error(f"Validation error creating estimate_headers: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating estimate_headers: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/batch", response_model=List[Estimate_headersResponse], status_code=201)
async def create_estimate_headerss_batch(
    request: Estimate_headersBatchCreateRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create multiple estimate_headerss in a single request"""
    logger.debug(f"Batch creating {len(request.items)} estimate_headerss")
    
    service = Estimate_headersService(db)
    results = []
    
    try:
        for item_data in request.items:
            result = await service.create(item_data.model_dump(), user_id=str(current_user.id))
            if result:
                results.append(result)
        
        logger.info(f"Batch created {len(results)} estimate_headerss successfully")
        return results
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch create: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch create failed: {str(e)}")


@router.put("/batch", response_model=List[Estimate_headersResponse])
async def update_estimate_headerss_batch(
    request: Estimate_headersBatchUpdateRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update multiple estimate_headerss in a single request (requires ownership)"""
    logger.debug(f"Batch updating {len(request.items)} estimate_headerss")
    
    service = Estimate_headersService(db)
    results = []
    
    try:
        for item in request.items:
            # Only include non-None values for partial updates
            update_dict = {k: v for k, v in item.updates.model_dump().items() if v is not None}
            result = await service.update(item.id, update_dict, user_id=str(current_user.id))
            if result:
                results.append(result)
        
        logger.info(f"Batch updated {len(results)} estimate_headerss successfully")
        return results
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch update: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch update failed: {str(e)}")


@router.put("/{id}", response_model=Estimate_headersResponse)
async def update_estimate_headers(
    id: int,
    data: Estimate_headersUpdateData,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update an existing estimate_headers (requires ownership)"""
    logger.debug(f"Updating estimate_headers {id} with data: {data}")

    service = Estimate_headersService(db)
    try:
        # Only include non-None values for partial updates
        update_dict = {k: v for k, v in data.model_dump().items() if v is not None}
        result = await service.update(id, update_dict, user_id=str(current_user.id))
        if not result:
            logger.warning(f"Estimate_headers with id {id} not found for update")
            raise HTTPException(status_code=404, detail="Estimate_headers not found")
        
        logger.info(f"Estimate_headers {id} updated successfully")
        return result
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error updating estimate_headers {id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating estimate_headers {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/batch")
async def delete_estimate_headerss_batch(
    request: Estimate_headersBatchDeleteRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete multiple estimate_headerss by their IDs (requires ownership)"""
    logger.debug(f"Batch deleting {len(request.ids)} estimate_headerss")
    
    service = Estimate_headersService(db)
    deleted_count = 0
    
    try:
        for item_id in request.ids:
            success = await service.delete(item_id, user_id=str(current_user.id))
            if success:
                deleted_count += 1
        
        logger.info(f"Batch deleted {deleted_count} estimate_headerss successfully")
        return {"message": f"Successfully deleted {deleted_count} estimate_headerss", "deleted_count": deleted_count}
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch delete: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch delete failed: {str(e)}")


@router.delete("/{id}")
async def delete_estimate_headers(
    id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a single estimate_headers by ID (requires ownership)"""
    logger.debug(f"Deleting estimate_headers with id: {id}")
    
    service = Estimate_headersService(db)
    try:
        success = await service.delete(id, user_id=str(current_user.id))
        if not success:
            logger.warning(f"Estimate_headers with id {id} not found for deletion")
            raise HTTPException(status_code=404, detail="Estimate_headers not found")
        
        logger.info(f"Estimate_headers {id} deleted successfully")
        return {"message": "Estimate_headers deleted successfully", "id": id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting estimate_headers {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")