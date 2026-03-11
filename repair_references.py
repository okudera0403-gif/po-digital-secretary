import json
import logging
from typing import List, Optional


from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from services.repair_references import Repair_referencesService

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/entities/repair_references", tags=["repair_references"])


# ---------- Pydantic Schemas ----------
class Repair_referencesData(BaseModel):
    """Entity data schema (for create/update)"""
    repair_category: str = None
    item_name: str
    price: int
    remarks: str = None
    source: str = None


class Repair_referencesUpdateData(BaseModel):
    """Update entity data (partial updates allowed)"""
    repair_category: Optional[str] = None
    item_name: Optional[str] = None
    price: Optional[int] = None
    remarks: Optional[str] = None
    source: Optional[str] = None


class Repair_referencesResponse(BaseModel):
    """Entity response schema"""
    id: int
    repair_category: Optional[str] = None
    item_name: str
    price: int
    remarks: Optional[str] = None
    source: Optional[str] = None

    class Config:
        from_attributes = True


class Repair_referencesListResponse(BaseModel):
    """List response schema"""
    items: List[Repair_referencesResponse]
    total: int
    skip: int
    limit: int


class Repair_referencesBatchCreateRequest(BaseModel):
    """Batch create request"""
    items: List[Repair_referencesData]


class Repair_referencesBatchUpdateItem(BaseModel):
    """Batch update item"""
    id: int
    updates: Repair_referencesUpdateData


class Repair_referencesBatchUpdateRequest(BaseModel):
    """Batch update request"""
    items: List[Repair_referencesBatchUpdateItem]


class Repair_referencesBatchDeleteRequest(BaseModel):
    """Batch delete request"""
    ids: List[int]


# ---------- Routes ----------
@router.get("", response_model=Repair_referencesListResponse)
async def query_repair_referencess(
    query: str = Query(None, description="Query conditions (JSON string)"),
    sort: str = Query(None, description="Sort field (prefix with '-' for descending)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=2000, description="Max number of records to return"),
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: AsyncSession = Depends(get_db),
):
    """Query repair_referencess with filtering, sorting, and pagination"""
    logger.debug(f"Querying repair_referencess: query={query}, sort={sort}, skip={skip}, limit={limit}, fields={fields}")
    
    service = Repair_referencesService(db)
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
        logger.debug(f"Found {result['total']} repair_referencess")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying repair_referencess: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/all", response_model=Repair_referencesListResponse)
async def query_repair_referencess_all(
    query: str = Query(None, description="Query conditions (JSON string)"),
    sort: str = Query(None, description="Sort field (prefix with '-' for descending)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=2000, description="Max number of records to return"),
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: AsyncSession = Depends(get_db),
):
    # Query repair_referencess with filtering, sorting, and pagination without user limitation
    logger.debug(f"Querying repair_referencess: query={query}, sort={sort}, skip={skip}, limit={limit}, fields={fields}")

    service = Repair_referencesService(db)
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
        logger.debug(f"Found {result['total']} repair_referencess")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying repair_referencess: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{id}", response_model=Repair_referencesResponse)
async def get_repair_references(
    id: int,
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: AsyncSession = Depends(get_db),
):
    """Get a single repair_references by ID"""
    logger.debug(f"Fetching repair_references with id: {id}, fields={fields}")
    
    service = Repair_referencesService(db)
    try:
        result = await service.get_by_id(id)
        if not result:
            logger.warning(f"Repair_references with id {id} not found")
            raise HTTPException(status_code=404, detail="Repair_references not found")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching repair_references {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("", response_model=Repair_referencesResponse, status_code=201)
async def create_repair_references(
    data: Repair_referencesData,
    db: AsyncSession = Depends(get_db),
):
    """Create a new repair_references"""
    logger.debug(f"Creating new repair_references with data: {data}")
    
    service = Repair_referencesService(db)
    try:
        result = await service.create(data.model_dump())
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create repair_references")
        
        logger.info(f"Repair_references created successfully with id: {result.id}")
        return result
    except ValueError as e:
        logger.error(f"Validation error creating repair_references: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating repair_references: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/batch", response_model=List[Repair_referencesResponse], status_code=201)
async def create_repair_referencess_batch(
    request: Repair_referencesBatchCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create multiple repair_referencess in a single request"""
    logger.debug(f"Batch creating {len(request.items)} repair_referencess")
    
    service = Repair_referencesService(db)
    results = []
    
    try:
        for item_data in request.items:
            result = await service.create(item_data.model_dump())
            if result:
                results.append(result)
        
        logger.info(f"Batch created {len(results)} repair_referencess successfully")
        return results
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch create: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch create failed: {str(e)}")


@router.put("/batch", response_model=List[Repair_referencesResponse])
async def update_repair_referencess_batch(
    request: Repair_referencesBatchUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Update multiple repair_referencess in a single request"""
    logger.debug(f"Batch updating {len(request.items)} repair_referencess")
    
    service = Repair_referencesService(db)
    results = []
    
    try:
        for item in request.items:
            # Only include non-None values for partial updates
            update_dict = {k: v for k, v in item.updates.model_dump().items() if v is not None}
            result = await service.update(item.id, update_dict)
            if result:
                results.append(result)
        
        logger.info(f"Batch updated {len(results)} repair_referencess successfully")
        return results
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch update: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch update failed: {str(e)}")


@router.put("/{id}", response_model=Repair_referencesResponse)
async def update_repair_references(
    id: int,
    data: Repair_referencesUpdateData,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing repair_references"""
    logger.debug(f"Updating repair_references {id} with data: {data}")

    service = Repair_referencesService(db)
    try:
        # Only include non-None values for partial updates
        update_dict = {k: v for k, v in data.model_dump().items() if v is not None}
        result = await service.update(id, update_dict)
        if not result:
            logger.warning(f"Repair_references with id {id} not found for update")
            raise HTTPException(status_code=404, detail="Repair_references not found")
        
        logger.info(f"Repair_references {id} updated successfully")
        return result
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error updating repair_references {id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating repair_references {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/batch")
async def delete_repair_referencess_batch(
    request: Repair_referencesBatchDeleteRequest,
    db: AsyncSession = Depends(get_db),
):
    """Delete multiple repair_referencess by their IDs"""
    logger.debug(f"Batch deleting {len(request.ids)} repair_referencess")
    
    service = Repair_referencesService(db)
    deleted_count = 0
    
    try:
        for item_id in request.ids:
            success = await service.delete(item_id)
            if success:
                deleted_count += 1
        
        logger.info(f"Batch deleted {deleted_count} repair_referencess successfully")
        return {"message": f"Successfully deleted {deleted_count} repair_referencess", "deleted_count": deleted_count}
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch delete: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch delete failed: {str(e)}")


@router.delete("/{id}")
async def delete_repair_references(
    id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a single repair_references by ID"""
    logger.debug(f"Deleting repair_references with id: {id}")
    
    service = Repair_referencesService(db)
    try:
        success = await service.delete(id)
        if not success:
            logger.warning(f"Repair_references with id {id} not found for deletion")
            raise HTTPException(status_code=404, detail="Repair_references not found")
        
        logger.info(f"Repair_references {id} deleted successfully")
        return {"message": "Repair_references deleted successfully", "id": id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting repair_references {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")