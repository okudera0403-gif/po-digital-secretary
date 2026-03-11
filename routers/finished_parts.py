import json
import logging
from typing import List, Optional


from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from services.finished_parts import Finished_partsService

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/entities/finished_parts", tags=["finished_parts"])


# ---------- Pydantic Schemas ----------
class Finished_partsData(BaseModel):
    """Entity data schema (for create/update)"""
    part_group: str = None
    part_category: str = None
    part_type: str = None
    manufacturer: str = None
    model_no: str = None
    upper_price: int = None
    old_price: int = None
    unit_note: str = None
    remarks: str = None
    source: str = None


class Finished_partsUpdateData(BaseModel):
    """Update entity data (partial updates allowed)"""
    part_group: Optional[str] = None
    part_category: Optional[str] = None
    part_type: Optional[str] = None
    manufacturer: Optional[str] = None
    model_no: Optional[str] = None
    upper_price: Optional[int] = None
    old_price: Optional[int] = None
    unit_note: Optional[str] = None
    remarks: Optional[str] = None
    source: Optional[str] = None


class Finished_partsResponse(BaseModel):
    """Entity response schema"""
    id: int
    part_group: Optional[str] = None
    part_category: Optional[str] = None
    part_type: Optional[str] = None
    manufacturer: Optional[str] = None
    model_no: Optional[str] = None
    upper_price: Optional[int] = None
    old_price: Optional[int] = None
    unit_note: Optional[str] = None
    remarks: Optional[str] = None
    source: Optional[str] = None

    class Config:
        from_attributes = True


class Finished_partsListResponse(BaseModel):
    """List response schema"""
    items: List[Finished_partsResponse]
    total: int
    skip: int
    limit: int


class Finished_partsBatchCreateRequest(BaseModel):
    """Batch create request"""
    items: List[Finished_partsData]


class Finished_partsBatchUpdateItem(BaseModel):
    """Batch update item"""
    id: int
    updates: Finished_partsUpdateData


class Finished_partsBatchUpdateRequest(BaseModel):
    """Batch update request"""
    items: List[Finished_partsBatchUpdateItem]


class Finished_partsBatchDeleteRequest(BaseModel):
    """Batch delete request"""
    ids: List[int]


# ---------- Routes ----------
@router.get("", response_model=Finished_partsListResponse)
async def query_finished_partss(
    query: str = Query(None, description="Query conditions (JSON string)"),
    sort: str = Query(None, description="Sort field (prefix with '-' for descending)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=2000, description="Max number of records to return"),
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: AsyncSession = Depends(get_db),
):
    """Query finished_partss with filtering, sorting, and pagination"""
    logger.debug(f"Querying finished_partss: query={query}, sort={sort}, skip={skip}, limit={limit}, fields={fields}")
    
    service = Finished_partsService(db)
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
        logger.debug(f"Found {result['total']} finished_partss")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying finished_partss: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/all", response_model=Finished_partsListResponse)
async def query_finished_partss_all(
    query: str = Query(None, description="Query conditions (JSON string)"),
    sort: str = Query(None, description="Sort field (prefix with '-' for descending)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=2000, description="Max number of records to return"),
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: AsyncSession = Depends(get_db),
):
    # Query finished_partss with filtering, sorting, and pagination without user limitation
    logger.debug(f"Querying finished_partss: query={query}, sort={sort}, skip={skip}, limit={limit}, fields={fields}")

    service = Finished_partsService(db)
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
        logger.debug(f"Found {result['total']} finished_partss")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying finished_partss: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{id}", response_model=Finished_partsResponse)
async def get_finished_parts(
    id: int,
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: AsyncSession = Depends(get_db),
):
    """Get a single finished_parts by ID"""
    logger.debug(f"Fetching finished_parts with id: {id}, fields={fields}")
    
    service = Finished_partsService(db)
    try:
        result = await service.get_by_id(id)
        if not result:
            logger.warning(f"Finished_parts with id {id} not found")
            raise HTTPException(status_code=404, detail="Finished_parts not found")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching finished_parts {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("", response_model=Finished_partsResponse, status_code=201)
async def create_finished_parts(
    data: Finished_partsData,
    db: AsyncSession = Depends(get_db),
):
    """Create a new finished_parts"""
    logger.debug(f"Creating new finished_parts with data: {data}")
    
    service = Finished_partsService(db)
    try:
        result = await service.create(data.model_dump())
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create finished_parts")
        
        logger.info(f"Finished_parts created successfully with id: {result.id}")
        return result
    except ValueError as e:
        logger.error(f"Validation error creating finished_parts: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating finished_parts: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/batch", response_model=List[Finished_partsResponse], status_code=201)
async def create_finished_partss_batch(
    request: Finished_partsBatchCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create multiple finished_partss in a single request"""
    logger.debug(f"Batch creating {len(request.items)} finished_partss")
    
    service = Finished_partsService(db)
    results = []
    
    try:
        for item_data in request.items:
            result = await service.create(item_data.model_dump())
            if result:
                results.append(result)
        
        logger.info(f"Batch created {len(results)} finished_partss successfully")
        return results
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch create: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch create failed: {str(e)}")


@router.put("/batch", response_model=List[Finished_partsResponse])
async def update_finished_partss_batch(
    request: Finished_partsBatchUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Update multiple finished_partss in a single request"""
    logger.debug(f"Batch updating {len(request.items)} finished_partss")
    
    service = Finished_partsService(db)
    results = []
    
    try:
        for item in request.items:
            # Only include non-None values for partial updates
            update_dict = {k: v for k, v in item.updates.model_dump().items() if v is not None}
            result = await service.update(item.id, update_dict)
            if result:
                results.append(result)
        
        logger.info(f"Batch updated {len(results)} finished_partss successfully")
        return results
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch update: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch update failed: {str(e)}")


@router.put("/{id}", response_model=Finished_partsResponse)
async def update_finished_parts(
    id: int,
    data: Finished_partsUpdateData,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing finished_parts"""
    logger.debug(f"Updating finished_parts {id} with data: {data}")

    service = Finished_partsService(db)
    try:
        # Only include non-None values for partial updates
        update_dict = {k: v for k, v in data.model_dump().items() if v is not None}
        result = await service.update(id, update_dict)
        if not result:
            logger.warning(f"Finished_parts with id {id} not found for update")
            raise HTTPException(status_code=404, detail="Finished_parts not found")
        
        logger.info(f"Finished_parts {id} updated successfully")
        return result
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error updating finished_parts {id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating finished_parts {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/batch")
async def delete_finished_partss_batch(
    request: Finished_partsBatchDeleteRequest,
    db: AsyncSession = Depends(get_db),
):
    """Delete multiple finished_partss by their IDs"""
    logger.debug(f"Batch deleting {len(request.ids)} finished_partss")
    
    service = Finished_partsService(db)
    deleted_count = 0
    
    try:
        for item_id in request.ids:
            success = await service.delete(item_id)
            if success:
                deleted_count += 1
        
        logger.info(f"Batch deleted {deleted_count} finished_partss successfully")
        return {"message": f"Successfully deleted {deleted_count} finished_partss", "deleted_count": deleted_count}
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch delete: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch delete failed: {str(e)}")


@router.delete("/{id}")
async def delete_finished_parts(
    id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a single finished_parts by ID"""
    logger.debug(f"Deleting finished_parts with id: {id}")
    
    service = Finished_partsService(db)
    try:
        success = await service.delete(id)
        if not success:
            logger.warning(f"Finished_parts with id {id} not found for deletion")
            raise HTTPException(status_code=404, detail="Finished_parts not found")
        
        logger.info(f"Finished_parts {id} deleted successfully")
        return {"message": "Finished_parts deleted successfully", "id": id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting finished_parts {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")