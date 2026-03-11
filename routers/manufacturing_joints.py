import json
import logging
from typing import List, Optional


from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from services.manufacturing_joints import Manufacturing_jointsService

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/entities/manufacturing_joints", tags=["manufacturing_joints"])


# ---------- Pydantic Schemas ----------
class Manufacturing_jointsData(BaseModel):
    """Entity data schema (for create/update)"""
    name: str
    unit: str = None
    price: int
    source_page: int = None


class Manufacturing_jointsUpdateData(BaseModel):
    """Update entity data (partial updates allowed)"""
    name: Optional[str] = None
    unit: Optional[str] = None
    price: Optional[int] = None
    source_page: Optional[int] = None


class Manufacturing_jointsResponse(BaseModel):
    """Entity response schema"""
    id: int
    name: str
    unit: Optional[str] = None
    price: int
    source_page: Optional[int] = None

    class Config:
        from_attributes = True


class Manufacturing_jointsListResponse(BaseModel):
    """List response schema"""
    items: List[Manufacturing_jointsResponse]
    total: int
    skip: int
    limit: int


class Manufacturing_jointsBatchCreateRequest(BaseModel):
    """Batch create request"""
    items: List[Manufacturing_jointsData]


class Manufacturing_jointsBatchUpdateItem(BaseModel):
    """Batch update item"""
    id: int
    updates: Manufacturing_jointsUpdateData


class Manufacturing_jointsBatchUpdateRequest(BaseModel):
    """Batch update request"""
    items: List[Manufacturing_jointsBatchUpdateItem]


class Manufacturing_jointsBatchDeleteRequest(BaseModel):
    """Batch delete request"""
    ids: List[int]


# ---------- Routes ----------
@router.get("", response_model=Manufacturing_jointsListResponse)
async def query_manufacturing_jointss(
    query: str = Query(None, description="Query conditions (JSON string)"),
    sort: str = Query(None, description="Sort field (prefix with '-' for descending)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=2000, description="Max number of records to return"),
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: AsyncSession = Depends(get_db),
):
    """Query manufacturing_jointss with filtering, sorting, and pagination"""
    logger.debug(f"Querying manufacturing_jointss: query={query}, sort={sort}, skip={skip}, limit={limit}, fields={fields}")
    
    service = Manufacturing_jointsService(db)
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
        logger.debug(f"Found {result['total']} manufacturing_jointss")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying manufacturing_jointss: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/all", response_model=Manufacturing_jointsListResponse)
async def query_manufacturing_jointss_all(
    query: str = Query(None, description="Query conditions (JSON string)"),
    sort: str = Query(None, description="Sort field (prefix with '-' for descending)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=2000, description="Max number of records to return"),
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: AsyncSession = Depends(get_db),
):
    # Query manufacturing_jointss with filtering, sorting, and pagination without user limitation
    logger.debug(f"Querying manufacturing_jointss: query={query}, sort={sort}, skip={skip}, limit={limit}, fields={fields}")

    service = Manufacturing_jointsService(db)
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
        logger.debug(f"Found {result['total']} manufacturing_jointss")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying manufacturing_jointss: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{id}", response_model=Manufacturing_jointsResponse)
async def get_manufacturing_joints(
    id: int,
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: AsyncSession = Depends(get_db),
):
    """Get a single manufacturing_joints by ID"""
    logger.debug(f"Fetching manufacturing_joints with id: {id}, fields={fields}")
    
    service = Manufacturing_jointsService(db)
    try:
        result = await service.get_by_id(id)
        if not result:
            logger.warning(f"Manufacturing_joints with id {id} not found")
            raise HTTPException(status_code=404, detail="Manufacturing_joints not found")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching manufacturing_joints {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("", response_model=Manufacturing_jointsResponse, status_code=201)
async def create_manufacturing_joints(
    data: Manufacturing_jointsData,
    db: AsyncSession = Depends(get_db),
):
    """Create a new manufacturing_joints"""
    logger.debug(f"Creating new manufacturing_joints with data: {data}")
    
    service = Manufacturing_jointsService(db)
    try:
        result = await service.create(data.model_dump())
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create manufacturing_joints")
        
        logger.info(f"Manufacturing_joints created successfully with id: {result.id}")
        return result
    except ValueError as e:
        logger.error(f"Validation error creating manufacturing_joints: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating manufacturing_joints: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/batch", response_model=List[Manufacturing_jointsResponse], status_code=201)
async def create_manufacturing_jointss_batch(
    request: Manufacturing_jointsBatchCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create multiple manufacturing_jointss in a single request"""
    logger.debug(f"Batch creating {len(request.items)} manufacturing_jointss")
    
    service = Manufacturing_jointsService(db)
    results = []
    
    try:
        for item_data in request.items:
            result = await service.create(item_data.model_dump())
            if result:
                results.append(result)
        
        logger.info(f"Batch created {len(results)} manufacturing_jointss successfully")
        return results
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch create: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch create failed: {str(e)}")


@router.put("/batch", response_model=List[Manufacturing_jointsResponse])
async def update_manufacturing_jointss_batch(
    request: Manufacturing_jointsBatchUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Update multiple manufacturing_jointss in a single request"""
    logger.debug(f"Batch updating {len(request.items)} manufacturing_jointss")
    
    service = Manufacturing_jointsService(db)
    results = []
    
    try:
        for item in request.items:
            # Only include non-None values for partial updates
            update_dict = {k: v for k, v in item.updates.model_dump().items() if v is not None}
            result = await service.update(item.id, update_dict)
            if result:
                results.append(result)
        
        logger.info(f"Batch updated {len(results)} manufacturing_jointss successfully")
        return results
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch update: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch update failed: {str(e)}")


@router.put("/{id}", response_model=Manufacturing_jointsResponse)
async def update_manufacturing_joints(
    id: int,
    data: Manufacturing_jointsUpdateData,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing manufacturing_joints"""
    logger.debug(f"Updating manufacturing_joints {id} with data: {data}")

    service = Manufacturing_jointsService(db)
    try:
        # Only include non-None values for partial updates
        update_dict = {k: v for k, v in data.model_dump().items() if v is not None}
        result = await service.update(id, update_dict)
        if not result:
            logger.warning(f"Manufacturing_joints with id {id} not found for update")
            raise HTTPException(status_code=404, detail="Manufacturing_joints not found")
        
        logger.info(f"Manufacturing_joints {id} updated successfully")
        return result
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error updating manufacturing_joints {id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating manufacturing_joints {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/batch")
async def delete_manufacturing_jointss_batch(
    request: Manufacturing_jointsBatchDeleteRequest,
    db: AsyncSession = Depends(get_db),
):
    """Delete multiple manufacturing_jointss by their IDs"""
    logger.debug(f"Batch deleting {len(request.ids)} manufacturing_jointss")
    
    service = Manufacturing_jointsService(db)
    deleted_count = 0
    
    try:
        for item_id in request.ids:
            success = await service.delete(item_id)
            if success:
                deleted_count += 1
        
        logger.info(f"Batch deleted {deleted_count} manufacturing_jointss successfully")
        return {"message": f"Successfully deleted {deleted_count} manufacturing_jointss", "deleted_count": deleted_count}
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch delete: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch delete failed: {str(e)}")


@router.delete("/{id}")
async def delete_manufacturing_joints(
    id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a single manufacturing_joints by ID"""
    logger.debug(f"Deleting manufacturing_joints with id: {id}")
    
    service = Manufacturing_jointsService(db)
    try:
        success = await service.delete(id)
        if not success:
            logger.warning(f"Manufacturing_joints with id {id} not found for deletion")
            raise HTTPException(status_code=404, detail="Manufacturing_joints not found")
        
        logger.info(f"Manufacturing_joints {id} deleted successfully")
        return {"message": "Manufacturing_joints deleted successfully", "id": id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting manufacturing_joints {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")