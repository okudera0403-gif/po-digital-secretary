import json
import logging
from typing import List, Optional


from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from services.estimate_items import Estimate_itemsService
from dependencies.auth import get_current_user
from schemas.auth import UserResponse

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/entities/estimate_items", tags=["estimate_items"])


# ---------- Pydantic Schemas ----------
class Estimate_itemsData(BaseModel):
    """Entity data schema (for create/update)"""
    estimate_id: int
    item_group: str = None
    item_name: str = None
    item_type: str = None
    unit_price: int = None
    quantity: int = None
    amount: int = None
    remarks: str = None


class Estimate_itemsUpdateData(BaseModel):
    """Update entity data (partial updates allowed)"""
    estimate_id: Optional[int] = None
    item_group: Optional[str] = None
    item_name: Optional[str] = None
    item_type: Optional[str] = None
    unit_price: Optional[int] = None
    quantity: Optional[int] = None
    amount: Optional[int] = None
    remarks: Optional[str] = None


class Estimate_itemsResponse(BaseModel):
    """Entity response schema"""
    id: int
    user_id: str
    estimate_id: int
    item_group: Optional[str] = None
    item_name: Optional[str] = None
    item_type: Optional[str] = None
    unit_price: Optional[int] = None
    quantity: Optional[int] = None
    amount: Optional[int] = None
    remarks: Optional[str] = None

    class Config:
        from_attributes = True


class Estimate_itemsListResponse(BaseModel):
    """List response schema"""
    items: List[Estimate_itemsResponse]
    total: int
    skip: int
    limit: int


class Estimate_itemsBatchCreateRequest(BaseModel):
    """Batch create request"""
    items: List[Estimate_itemsData]


class Estimate_itemsBatchUpdateItem(BaseModel):
    """Batch update item"""
    id: int
    updates: Estimate_itemsUpdateData


class Estimate_itemsBatchUpdateRequest(BaseModel):
    """Batch update request"""
    items: List[Estimate_itemsBatchUpdateItem]


class Estimate_itemsBatchDeleteRequest(BaseModel):
    """Batch delete request"""
    ids: List[int]


# ---------- Routes ----------
@router.get("", response_model=Estimate_itemsListResponse)
async def query_estimate_itemss(
    query: str = Query(None, description="Query conditions (JSON string)"),
    sort: str = Query(None, description="Sort field (prefix with '-' for descending)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=2000, description="Max number of records to return"),
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Query estimate_itemss with filtering, sorting, and pagination (user can only see their own records)"""
    logger.debug(f"Querying estimate_itemss: query={query}, sort={sort}, skip={skip}, limit={limit}, fields={fields}")
    
    service = Estimate_itemsService(db)
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
        logger.debug(f"Found {result['total']} estimate_itemss")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying estimate_itemss: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/all", response_model=Estimate_itemsListResponse)
async def query_estimate_itemss_all(
    query: str = Query(None, description="Query conditions (JSON string)"),
    sort: str = Query(None, description="Sort field (prefix with '-' for descending)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=2000, description="Max number of records to return"),
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: AsyncSession = Depends(get_db),
):
    # Query estimate_itemss with filtering, sorting, and pagination without user limitation
    logger.debug(f"Querying estimate_itemss: query={query}, sort={sort}, skip={skip}, limit={limit}, fields={fields}")

    service = Estimate_itemsService(db)
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
        logger.debug(f"Found {result['total']} estimate_itemss")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying estimate_itemss: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{id}", response_model=Estimate_itemsResponse)
async def get_estimate_items(
    id: int,
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single estimate_items by ID (user can only see their own records)"""
    logger.debug(f"Fetching estimate_items with id: {id}, fields={fields}")
    
    service = Estimate_itemsService(db)
    try:
        result = await service.get_by_id(id, user_id=str(current_user.id))
        if not result:
            logger.warning(f"Estimate_items with id {id} not found")
            raise HTTPException(status_code=404, detail="Estimate_items not found")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching estimate_items {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("", response_model=Estimate_itemsResponse, status_code=201)
async def create_estimate_items(
    data: Estimate_itemsData,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new estimate_items"""
    logger.debug(f"Creating new estimate_items with data: {data}")
    
    service = Estimate_itemsService(db)
    try:
        result = await service.create(data.model_dump(), user_id=str(current_user.id))
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create estimate_items")
        
        logger.info(f"Estimate_items created successfully with id: {result.id}")
        return result
    except ValueError as e:
        logger.error(f"Validation error creating estimate_items: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating estimate_items: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/batch", response_model=List[Estimate_itemsResponse], status_code=201)
async def create_estimate_itemss_batch(
    request: Estimate_itemsBatchCreateRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create multiple estimate_itemss in a single request"""
    logger.debug(f"Batch creating {len(request.items)} estimate_itemss")
    
    service = Estimate_itemsService(db)
    results = []
    
    try:
        for item_data in request.items:
            result = await service.create(item_data.model_dump(), user_id=str(current_user.id))
            if result:
                results.append(result)
        
        logger.info(f"Batch created {len(results)} estimate_itemss successfully")
        return results
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch create: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch create failed: {str(e)}")


@router.put("/batch", response_model=List[Estimate_itemsResponse])
async def update_estimate_itemss_batch(
    request: Estimate_itemsBatchUpdateRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update multiple estimate_itemss in a single request (requires ownership)"""
    logger.debug(f"Batch updating {len(request.items)} estimate_itemss")
    
    service = Estimate_itemsService(db)
    results = []
    
    try:
        for item in request.items:
            # Only include non-None values for partial updates
            update_dict = {k: v for k, v in item.updates.model_dump().items() if v is not None}
            result = await service.update(item.id, update_dict, user_id=str(current_user.id))
            if result:
                results.append(result)
        
        logger.info(f"Batch updated {len(results)} estimate_itemss successfully")
        return results
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch update: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch update failed: {str(e)}")


@router.put("/{id}", response_model=Estimate_itemsResponse)
async def update_estimate_items(
    id: int,
    data: Estimate_itemsUpdateData,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update an existing estimate_items (requires ownership)"""
    logger.debug(f"Updating estimate_items {id} with data: {data}")

    service = Estimate_itemsService(db)
    try:
        # Only include non-None values for partial updates
        update_dict = {k: v for k, v in data.model_dump().items() if v is not None}
        result = await service.update(id, update_dict, user_id=str(current_user.id))
        if not result:
            logger.warning(f"Estimate_items with id {id} not found for update")
            raise HTTPException(status_code=404, detail="Estimate_items not found")
        
        logger.info(f"Estimate_items {id} updated successfully")
        return result
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error updating estimate_items {id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating estimate_items {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/batch")
async def delete_estimate_itemss_batch(
    request: Estimate_itemsBatchDeleteRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete multiple estimate_itemss by their IDs (requires ownership)"""
    logger.debug(f"Batch deleting {len(request.ids)} estimate_itemss")
    
    service = Estimate_itemsService(db)
    deleted_count = 0
    
    try:
        for item_id in request.ids:
            success = await service.delete(item_id, user_id=str(current_user.id))
            if success:
                deleted_count += 1
        
        logger.info(f"Batch deleted {deleted_count} estimate_itemss successfully")
        return {"message": f"Successfully deleted {deleted_count} estimate_itemss", "deleted_count": deleted_count}
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch delete: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch delete failed: {str(e)}")


@router.delete("/{id}")
async def delete_estimate_items(
    id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a single estimate_items by ID (requires ownership)"""
    logger.debug(f"Deleting estimate_items with id: {id}")
    
    service = Estimate_itemsService(db)
    try:
        success = await service.delete(id, user_id=str(current_user.id))
        if not success:
            logger.warning(f"Estimate_items with id {id} not found for deletion")
            raise HTTPException(status_code=404, detail="Estimate_items not found")
        
        logger.info(f"Estimate_items {id} deleted successfully")
        return {"message": "Estimate_items deleted successfully", "id": id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting estimate_items {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")