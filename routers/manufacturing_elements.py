import json
import logging
from typing import List, Optional


from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from services.manufacturing_elements import Manufacturing_elementsService

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/entities/manufacturing_elements", tags=["manufacturing_elements"])


# ---------- Pydantic Schemas ----------
class Manufacturing_elementsData(BaseModel):
    """Entity data schema (for create/update)"""
    category: str = None
    element_group: str = None
    name: str = None
    spec: str = None
    price: int = None
    remarks: str = None
    source: str = None


class Manufacturing_elementsUpdateData(BaseModel):
    """Update entity data (partial updates allowed)"""
    category: Optional[str] = None
    element_group: Optional[str] = None
    name: Optional[str] = None
    spec: Optional[str] = None
    price: Optional[int] = None
    remarks: Optional[str] = None
    source: Optional[str] = None


class Manufacturing_elementsResponse(BaseModel):
    """Entity response schema"""
    id: int
    category: Optional[str] = None
    element_group: Optional[str] = None
    name: Optional[str] = None
    spec: Optional[str] = None
    price: Optional[int] = None
    remarks: Optional[str] = None
    source: Optional[str] = None

    class Config:
        from_attributes = True


class Manufacturing_elementsListResponse(BaseModel):
    """List response schema"""
    items: List[Manufacturing_elementsResponse]
    total: int
    skip: int
    limit: int


class Manufacturing_elementsBatchCreateRequest(BaseModel):
    """Batch create request"""
    items: List[Manufacturing_elementsData]


class Manufacturing_elementsBatchUpdateItem(BaseModel):
    """Batch update item"""
    id: int
    updates: Manufacturing_elementsUpdateData


class Manufacturing_elementsBatchUpdateRequest(BaseModel):
    """Batch update request"""
    items: List[Manufacturing_elementsBatchUpdateItem]


class Manufacturing_elementsBatchDeleteRequest(BaseModel):
    """Batch delete request"""
    ids: List[int]


# ---------- Routes ----------
@router.get("", response_model=Manufacturing_elementsListResponse)
async def query_manufacturing_elementss(
    query: str = Query(None, description="Query conditions (JSON string)"),
    sort: str = Query(None, description="Sort field (prefix with '-' for descending)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=2000, description="Max number of records to return"),
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: AsyncSession = Depends(get_db),
):
    """Query manufacturing_elementss with filtering, sorting, and pagination"""
    logger.debug(f"Querying manufacturing_elementss: query={query}, sort={sort}, skip={skip}, limit={limit}, fields={fields}")
    
    service = Manufacturing_elementsService(db)
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
        logger.debug(f"Found {result['total']} manufacturing_elementss")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying manufacturing_elementss: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/all", response_model=Manufacturing_elementsListResponse)
async def query_manufacturing_elementss_all(
    query: str = Query(None, description="Query conditions (JSON string)"),
    sort: str = Query(None, description="Sort field (prefix with '-' for descending)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=2000, description="Max number of records to return"),
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: AsyncSession = Depends(get_db),
):
    # Query manufacturing_elementss with filtering, sorting, and pagination without user limitation
    logger.debug(f"Querying manufacturing_elementss: query={query}, sort={sort}, skip={skip}, limit={limit}, fields={fields}")

    service = Manufacturing_elementsService(db)
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
        logger.debug(f"Found {result['total']} manufacturing_elementss")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying manufacturing_elementss: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{id}", response_model=Manufacturing_elementsResponse)
async def get_manufacturing_elements(
    id: int,
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: AsyncSession = Depends(get_db),
):
    """Get a single manufacturing_elements by ID"""
    logger.debug(f"Fetching manufacturing_elements with id: {id}, fields={fields}")
    
    service = Manufacturing_elementsService(db)
    try:
        result = await service.get_by_id(id)
        if not result:
            logger.warning(f"Manufacturing_elements with id {id} not found")
            raise HTTPException(status_code=404, detail="Manufacturing_elements not found")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching manufacturing_elements {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("", response_model=Manufacturing_elementsResponse, status_code=201)
async def create_manufacturing_elements(
    data: Manufacturing_elementsData,
    db: AsyncSession = Depends(get_db),
):
    """Create a new manufacturing_elements"""
    logger.debug(f"Creating new manufacturing_elements with data: {data}")
    
    service = Manufacturing_elementsService(db)
    try:
        result = await service.create(data.model_dump())
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create manufacturing_elements")
        
        logger.info(f"Manufacturing_elements created successfully with id: {result.id}")
        return result
    except ValueError as e:
        logger.error(f"Validation error creating manufacturing_elements: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating manufacturing_elements: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/batch", response_model=List[Manufacturing_elementsResponse], status_code=201)
async def create_manufacturing_elementss_batch(
    request: Manufacturing_elementsBatchCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create multiple manufacturing_elementss in a single request"""
    logger.debug(f"Batch creating {len(request.items)} manufacturing_elementss")
    
    service = Manufacturing_elementsService(db)
    results = []
    
    try:
        for item_data in request.items:
            result = await service.create(item_data.model_dump())
            if result:
                results.append(result)
        
        logger.info(f"Batch created {len(results)} manufacturing_elementss successfully")
        return results
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch create: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch create failed: {str(e)}")


@router.put("/batch", response_model=List[Manufacturing_elementsResponse])
async def update_manufacturing_elementss_batch(
    request: Manufacturing_elementsBatchUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Update multiple manufacturing_elementss in a single request"""
    logger.debug(f"Batch updating {len(request.items)} manufacturing_elementss")
    
    service = Manufacturing_elementsService(db)
    results = []
    
    try:
        for item in request.items:
            # Only include non-None values for partial updates
            update_dict = {k: v for k, v in item.updates.model_dump().items() if v is not None}
            result = await service.update(item.id, update_dict)
            if result:
                results.append(result)
        
        logger.info(f"Batch updated {len(results)} manufacturing_elementss successfully")
        return results
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch update: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch update failed: {str(e)}")


@router.put("/{id}", response_model=Manufacturing_elementsResponse)
async def update_manufacturing_elements(
    id: int,
    data: Manufacturing_elementsUpdateData,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing manufacturing_elements"""
    logger.debug(f"Updating manufacturing_elements {id} with data: {data}")

    service = Manufacturing_elementsService(db)
    try:
        # Only include non-None values for partial updates
        update_dict = {k: v for k, v in data.model_dump().items() if v is not None}
        result = await service.update(id, update_dict)
        if not result:
            logger.warning(f"Manufacturing_elements with id {id} not found for update")
            raise HTTPException(status_code=404, detail="Manufacturing_elements not found")
        
        logger.info(f"Manufacturing_elements {id} updated successfully")
        return result
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error updating manufacturing_elements {id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating manufacturing_elements {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/batch")
async def delete_manufacturing_elementss_batch(
    request: Manufacturing_elementsBatchDeleteRequest,
    db: AsyncSession = Depends(get_db),
):
    """Delete multiple manufacturing_elementss by their IDs"""
    logger.debug(f"Batch deleting {len(request.ids)} manufacturing_elementss")
    
    service = Manufacturing_elementsService(db)
    deleted_count = 0
    
    try:
        for item_id in request.ids:
            success = await service.delete(item_id)
            if success:
                deleted_count += 1
        
        logger.info(f"Batch deleted {deleted_count} manufacturing_elementss successfully")
        return {"message": f"Successfully deleted {deleted_count} manufacturing_elementss", "deleted_count": deleted_count}
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch delete: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch delete failed: {str(e)}")


@router.delete("/{id}")
async def delete_manufacturing_elements(
    id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a single manufacturing_elements by ID"""
    logger.debug(f"Deleting manufacturing_elements with id: {id}")
    
    service = Manufacturing_elementsService(db)
    try:
        success = await service.delete(id)
        if not success:
            logger.warning(f"Manufacturing_elements with id {id} not found for deletion")
            raise HTTPException(status_code=404, detail="Manufacturing_elements not found")
        
        logger.info(f"Manufacturing_elements {id} deleted successfully")
        return {"message": "Manufacturing_elements deleted successfully", "id": id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting manufacturing_elements {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")