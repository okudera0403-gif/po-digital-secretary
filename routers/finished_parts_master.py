import json
import logging
from typing import List, Optional


from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from services.finished_parts_master import Finished_parts_masterService

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/entities/finished_parts_master", tags=["finished_parts_master"])


# ---------- Pydantic Schemas ----------
class Finished_parts_masterData(BaseModel):
    """Entity data schema (for create/update)"""
    section: str
    subcategory: str = None
    name: str
    part_number: str = None
    price: int
    source_page: int = None
    manual_confirm: str = None
    estimate_use: str = None
    notes: str = None


class Finished_parts_masterUpdateData(BaseModel):
    """Update entity data (partial updates allowed)"""
    section: Optional[str] = None
    subcategory: Optional[str] = None
    name: Optional[str] = None
    part_number: Optional[str] = None
    price: Optional[int] = None
    source_page: Optional[int] = None
    manual_confirm: Optional[str] = None
    estimate_use: Optional[str] = None
    notes: Optional[str] = None


class Finished_parts_masterResponse(BaseModel):
    """Entity response schema"""
    id: int
    section: str
    subcategory: Optional[str] = None
    name: str
    part_number: Optional[str] = None
    price: int
    source_page: Optional[int] = None
    manual_confirm: Optional[str] = None
    estimate_use: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class Finished_parts_masterListResponse(BaseModel):
    """List response schema"""
    items: List[Finished_parts_masterResponse]
    total: int
    skip: int
    limit: int


class Finished_parts_masterBatchCreateRequest(BaseModel):
    """Batch create request"""
    items: List[Finished_parts_masterData]


class Finished_parts_masterBatchUpdateItem(BaseModel):
    """Batch update item"""
    id: int
    updates: Finished_parts_masterUpdateData


class Finished_parts_masterBatchUpdateRequest(BaseModel):
    """Batch update request"""
    items: List[Finished_parts_masterBatchUpdateItem]


class Finished_parts_masterBatchDeleteRequest(BaseModel):
    """Batch delete request"""
    ids: List[int]


# ---------- Routes ----------
@router.get("", response_model=Finished_parts_masterListResponse)
async def query_finished_parts_masters(
    query: str = Query(None, description="Query conditions (JSON string)"),
    sort: str = Query(None, description="Sort field (prefix with '-' for descending)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=2000, description="Max number of records to return"),
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: AsyncSession = Depends(get_db),
):
    """Query finished_parts_masters with filtering, sorting, and pagination"""
    logger.debug(f"Querying finished_parts_masters: query={query}, sort={sort}, skip={skip}, limit={limit}, fields={fields}")
    
    service = Finished_parts_masterService(db)
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
        )
        logger.debug(f"Found {result['total']} finished_parts_masters")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying finished_parts_masters: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/all", response_model=Finished_parts_masterListResponse)
async def query_finished_parts_masters_all(
    query: str = Query(None, description="Query conditions (JSON string)"),
    sort: str = Query(None, description="Sort field (prefix with '-' for descending)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=2000, description="Max number of records to return"),
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: AsyncSession = Depends(get_db),
):
    # Query finished_parts_masters with filtering, sorting, and pagination without user limitation
    logger.debug(f"Querying finished_parts_masters: query={query}, sort={sort}, skip={skip}, limit={limit}, fields={fields}")

    service = Finished_parts_masterService(db)
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
        logger.debug(f"Found {result['total']} finished_parts_masters")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying finished_parts_masters: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{id}", response_model=Finished_parts_masterResponse)
async def get_finished_parts_master(
    id: int,
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: AsyncSession = Depends(get_db),
):
    """Get a single finished_parts_master by ID"""
    logger.debug(f"Fetching finished_parts_master with id: {id}, fields={fields}")
    
    service = Finished_parts_masterService(db)
    try:
        result = await service.get_by_id(id)
        if not result:
            logger.warning(f"Finished_parts_master with id {id} not found")
            raise HTTPException(status_code=404, detail="Finished_parts_master not found")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching finished_parts_master {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("", response_model=Finished_parts_masterResponse, status_code=201)
async def create_finished_parts_master(
    data: Finished_parts_masterData,
    db: AsyncSession = Depends(get_db),
):
    """Create a new finished_parts_master"""
    logger.debug(f"Creating new finished_parts_master with data: {data}")
    
    service = Finished_parts_masterService(db)
    try:
        result = await service.create(data.model_dump())
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create finished_parts_master")
        
        logger.info(f"Finished_parts_master created successfully with id: {result.id}")
        return result
    except ValueError as e:
        logger.error(f"Validation error creating finished_parts_master: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating finished_parts_master: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/batch", response_model=List[Finished_parts_masterResponse], status_code=201)
async def create_finished_parts_masters_batch(
    request: Finished_parts_masterBatchCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create multiple finished_parts_masters in a single request"""
    logger.debug(f"Batch creating {len(request.items)} finished_parts_masters")
    
    service = Finished_parts_masterService(db)
    results = []
    
    try:
        for item_data in request.items:
            result = await service.create(item_data.model_dump())
            if result:
                results.append(result)
        
        logger.info(f"Batch created {len(results)} finished_parts_masters successfully")
        return results
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch create: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch create failed: {str(e)}")


@router.put("/batch", response_model=List[Finished_parts_masterResponse])
async def update_finished_parts_masters_batch(
    request: Finished_parts_masterBatchUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Update multiple finished_parts_masters in a single request"""
    logger.debug(f"Batch updating {len(request.items)} finished_parts_masters")
    
    service = Finished_parts_masterService(db)
    results = []
    
    try:
        for item in request.items:
            # Only include non-None values for partial updates
            update_dict = {k: v for k, v in item.updates.model_dump().items() if v is not None}
            result = await service.update(item.id, update_dict)
            if result:
                results.append(result)
        
        logger.info(f"Batch updated {len(results)} finished_parts_masters successfully")
        return results
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch update: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch update failed: {str(e)}")


@router.put("/{id}", response_model=Finished_parts_masterResponse)
async def update_finished_parts_master(
    id: int,
    data: Finished_parts_masterUpdateData,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing finished_parts_master"""
    logger.debug(f"Updating finished_parts_master {id} with data: {data}")

    service = Finished_parts_masterService(db)
    try:
        # Only include non-None values for partial updates
        update_dict = {k: v for k, v in data.model_dump().items() if v is not None}
        result = await service.update(id, update_dict)
        if not result:
            logger.warning(f"Finished_parts_master with id {id} not found for update")
            raise HTTPException(status_code=404, detail="Finished_parts_master not found")
        
        logger.info(f"Finished_parts_master {id} updated successfully")
        return result
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error updating finished_parts_master {id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating finished_parts_master {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/batch")
async def delete_finished_parts_masters_batch(
    request: Finished_parts_masterBatchDeleteRequest,
    db: AsyncSession = Depends(get_db),
):
    """Delete multiple finished_parts_masters by their IDs"""
    logger.debug(f"Batch deleting {len(request.ids)} finished_parts_masters")
    
    service = Finished_parts_masterService(db)
    deleted_count = 0
    
    try:
        for item_id in request.ids:
            success = await service.delete(item_id)
            if success:
                deleted_count += 1
        
        logger.info(f"Batch deleted {deleted_count} finished_parts_masters successfully")
        return {"message": f"Successfully deleted {deleted_count} finished_parts_masters", "deleted_count": deleted_count}
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch delete: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch delete failed: {str(e)}")


@router.delete("/{id}")
async def delete_finished_parts_master(
    id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a single finished_parts_master by ID"""
    logger.debug(f"Deleting finished_parts_master with id: {id}")
    
    service = Finished_parts_masterService(db)
    try:
        success = await service.delete(id)
        if not success:
            logger.warning(f"Finished_parts_master with id {id} not found for deletion")
            raise HTTPException(status_code=404, detail="Finished_parts_master not found")
        
        logger.info(f"Finished_parts_master {id} deleted successfully")
        return {"message": "Finished_parts_master deleted successfully", "id": id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting finished_parts_master {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")