import json
import logging
from typing import List, Optional


from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from services.option_masters import Option_mastersService

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/entities/option_masters", tags=["option_masters"])


# ---------- Pydantic Schemas ----------
class Option_mastersData(BaseModel):
    """Entity data schema (for create/update)"""
    group_name: str
    item_name: str
    price: int = None
    sort_order: int = None


class Option_mastersUpdateData(BaseModel):
    """Update entity data (partial updates allowed)"""
    group_name: Optional[str] = None
    item_name: Optional[str] = None
    price: Optional[int] = None
    sort_order: Optional[int] = None


class Option_mastersResponse(BaseModel):
    """Entity response schema"""
    id: int
    group_name: str
    item_name: str
    price: Optional[int] = None
    sort_order: Optional[int] = None

    class Config:
        from_attributes = True


class Option_mastersListResponse(BaseModel):
    """List response schema"""
    items: List[Option_mastersResponse]
    total: int
    skip: int
    limit: int


class Option_mastersBatchCreateRequest(BaseModel):
    """Batch create request"""
    items: List[Option_mastersData]


class Option_mastersBatchUpdateItem(BaseModel):
    """Batch update item"""
    id: int
    updates: Option_mastersUpdateData


class Option_mastersBatchUpdateRequest(BaseModel):
    """Batch update request"""
    items: List[Option_mastersBatchUpdateItem]


class Option_mastersBatchDeleteRequest(BaseModel):
    """Batch delete request"""
    ids: List[int]


# ---------- Routes ----------
@router.get("", response_model=Option_mastersListResponse)
async def query_option_masterss(
    query: str = Query(None, description="Query conditions (JSON string)"),
    sort: str = Query(None, description="Sort field (prefix with '-' for descending)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=2000, description="Max number of records to return"),
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: AsyncSession = Depends(get_db),
):
    """Query option_masterss with filtering, sorting, and pagination"""
    logger.debug(f"Querying option_masterss: query={query}, sort={sort}, skip={skip}, limit={limit}, fields={fields}")
    
    service = Option_mastersService(db)
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
        logger.debug(f"Found {result['total']} option_masterss")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying option_masterss: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/all", response_model=Option_mastersListResponse)
async def query_option_masterss_all(
    query: str = Query(None, description="Query conditions (JSON string)"),
    sort: str = Query(None, description="Sort field (prefix with '-' for descending)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=2000, description="Max number of records to return"),
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: AsyncSession = Depends(get_db),
):
    # Query option_masterss with filtering, sorting, and pagination without user limitation
    logger.debug(f"Querying option_masterss: query={query}, sort={sort}, skip={skip}, limit={limit}, fields={fields}")

    service = Option_mastersService(db)
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
        logger.debug(f"Found {result['total']} option_masterss")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying option_masterss: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{id}", response_model=Option_mastersResponse)
async def get_option_masters(
    id: int,
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: AsyncSession = Depends(get_db),
):
    """Get a single option_masters by ID"""
    logger.debug(f"Fetching option_masters with id: {id}, fields={fields}")
    
    service = Option_mastersService(db)
    try:
        result = await service.get_by_id(id)
        if not result:
            logger.warning(f"Option_masters with id {id} not found")
            raise HTTPException(status_code=404, detail="Option_masters not found")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching option_masters {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("", response_model=Option_mastersResponse, status_code=201)
async def create_option_masters(
    data: Option_mastersData,
    db: AsyncSession = Depends(get_db),
):
    """Create a new option_masters"""
    logger.debug(f"Creating new option_masters with data: {data}")
    
    service = Option_mastersService(db)
    try:
        result = await service.create(data.model_dump())
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create option_masters")
        
        logger.info(f"Option_masters created successfully with id: {result.id}")
        return result
    except ValueError as e:
        logger.error(f"Validation error creating option_masters: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating option_masters: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/batch", response_model=List[Option_mastersResponse], status_code=201)
async def create_option_masterss_batch(
    request: Option_mastersBatchCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create multiple option_masterss in a single request"""
    logger.debug(f"Batch creating {len(request.items)} option_masterss")
    
    service = Option_mastersService(db)
    results = []
    
    try:
        for item_data in request.items:
            result = await service.create(item_data.model_dump())
            if result:
                results.append(result)
        
        logger.info(f"Batch created {len(results)} option_masterss successfully")
        return results
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch create: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch create failed: {str(e)}")


@router.put("/batch", response_model=List[Option_mastersResponse])
async def update_option_masterss_batch(
    request: Option_mastersBatchUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Update multiple option_masterss in a single request"""
    logger.debug(f"Batch updating {len(request.items)} option_masterss")
    
    service = Option_mastersService(db)
    results = []
    
    try:
        for item in request.items:
            # Only include non-None values for partial updates
            update_dict = {k: v for k, v in item.updates.model_dump().items() if v is not None}
            result = await service.update(item.id, update_dict)
            if result:
                results.append(result)
        
        logger.info(f"Batch updated {len(results)} option_masterss successfully")
        return results
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch update: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch update failed: {str(e)}")


@router.put("/{id}", response_model=Option_mastersResponse)
async def update_option_masters(
    id: int,
    data: Option_mastersUpdateData,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing option_masters"""
    logger.debug(f"Updating option_masters {id} with data: {data}")

    service = Option_mastersService(db)
    try:
        # Only include non-None values for partial updates
        update_dict = {k: v for k, v in data.model_dump().items() if v is not None}
        result = await service.update(id, update_dict)
        if not result:
            logger.warning(f"Option_masters with id {id} not found for update")
            raise HTTPException(status_code=404, detail="Option_masters not found")
        
        logger.info(f"Option_masters {id} updated successfully")
        return result
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error updating option_masters {id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating option_masters {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/batch")
async def delete_option_masterss_batch(
    request: Option_mastersBatchDeleteRequest,
    db: AsyncSession = Depends(get_db),
):
    """Delete multiple option_masterss by their IDs"""
    logger.debug(f"Batch deleting {len(request.ids)} option_masterss")
    
    service = Option_mastersService(db)
    deleted_count = 0
    
    try:
        for item_id in request.ids:
            success = await service.delete(item_id)
            if success:
                deleted_count += 1
        
        logger.info(f"Batch deleted {deleted_count} option_masterss successfully")
        return {"message": f"Successfully deleted {deleted_count} option_masterss", "deleted_count": deleted_count}
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch delete: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch delete failed: {str(e)}")


@router.delete("/{id}")
async def delete_option_masters(
    id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a single option_masters by ID"""
    logger.debug(f"Deleting option_masters with id: {id}")
    
    service = Option_mastersService(db)
    try:
        success = await service.delete(id)
        if not success:
            logger.warning(f"Option_masters with id {id} not found for deletion")
            raise HTTPException(status_code=404, detail="Option_masters not found")
        
        logger.info(f"Option_masters {id} deleted successfully")
        return {"message": "Option_masters deleted successfully", "id": id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting option_masters {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")