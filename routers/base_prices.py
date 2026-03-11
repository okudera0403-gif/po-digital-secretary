import json
import logging
from typing import List, Optional


from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from services.base_prices import Base_pricesService

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/entities/base_prices", tags=["base_prices"])


# ---------- Pydantic Schemas ----------
class Base_pricesData(BaseModel):
    """Entity data schema (for create/update)"""
    code: str
    molding_price: int
    measurement_price: int
    remarks: str = None


class Base_pricesUpdateData(BaseModel):
    """Update entity data (partial updates allowed)"""
    code: Optional[str] = None
    molding_price: Optional[int] = None
    measurement_price: Optional[int] = None
    remarks: Optional[str] = None


class Base_pricesResponse(BaseModel):
    """Entity response schema"""
    id: int
    code: str
    molding_price: int
    measurement_price: int
    remarks: Optional[str] = None

    class Config:
        from_attributes = True


class Base_pricesListResponse(BaseModel):
    """List response schema"""
    items: List[Base_pricesResponse]
    total: int
    skip: int
    limit: int


class Base_pricesBatchCreateRequest(BaseModel):
    """Batch create request"""
    items: List[Base_pricesData]


class Base_pricesBatchUpdateItem(BaseModel):
    """Batch update item"""
    id: int
    updates: Base_pricesUpdateData


class Base_pricesBatchUpdateRequest(BaseModel):
    """Batch update request"""
    items: List[Base_pricesBatchUpdateItem]


class Base_pricesBatchDeleteRequest(BaseModel):
    """Batch delete request"""
    ids: List[int]


# ---------- Routes ----------
@router.get("", response_model=Base_pricesListResponse)
async def query_base_pricess(
    query: str = Query(None, description="Query conditions (JSON string)"),
    sort: str = Query(None, description="Sort field (prefix with '-' for descending)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=2000, description="Max number of records to return"),
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: AsyncSession = Depends(get_db),
):
    """Query base_pricess with filtering, sorting, and pagination"""
    logger.debug(f"Querying base_pricess: query={query}, sort={sort}, skip={skip}, limit={limit}, fields={fields}")
    
    service = Base_pricesService(db)
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
        logger.debug(f"Found {result['total']} base_pricess")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying base_pricess: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/all", response_model=Base_pricesListResponse)
async def query_base_pricess_all(
    query: str = Query(None, description="Query conditions (JSON string)"),
    sort: str = Query(None, description="Sort field (prefix with '-' for descending)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=2000, description="Max number of records to return"),
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: AsyncSession = Depends(get_db),
):
    # Query base_pricess with filtering, sorting, and pagination without user limitation
    logger.debug(f"Querying base_pricess: query={query}, sort={sort}, skip={skip}, limit={limit}, fields={fields}")

    service = Base_pricesService(db)
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
        logger.debug(f"Found {result['total']} base_pricess")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying base_pricess: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{id}", response_model=Base_pricesResponse)
async def get_base_prices(
    id: int,
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: AsyncSession = Depends(get_db),
):
    """Get a single base_prices by ID"""
    logger.debug(f"Fetching base_prices with id: {id}, fields={fields}")
    
    service = Base_pricesService(db)
    try:
        result = await service.get_by_id(id)
        if not result:
            logger.warning(f"Base_prices with id {id} not found")
            raise HTTPException(status_code=404, detail="Base_prices not found")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching base_prices {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("", response_model=Base_pricesResponse, status_code=201)
async def create_base_prices(
    data: Base_pricesData,
    db: AsyncSession = Depends(get_db),
):
    """Create a new base_prices"""
    logger.debug(f"Creating new base_prices with data: {data}")
    
    service = Base_pricesService(db)
    try:
        result = await service.create(data.model_dump())
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create base_prices")
        
        logger.info(f"Base_prices created successfully with id: {result.id}")
        return result
    except ValueError as e:
        logger.error(f"Validation error creating base_prices: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating base_prices: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/batch", response_model=List[Base_pricesResponse], status_code=201)
async def create_base_pricess_batch(
    request: Base_pricesBatchCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create multiple base_pricess in a single request"""
    logger.debug(f"Batch creating {len(request.items)} base_pricess")
    
    service = Base_pricesService(db)
    results = []
    
    try:
        for item_data in request.items:
            result = await service.create(item_data.model_dump())
            if result:
                results.append(result)
        
        logger.info(f"Batch created {len(results)} base_pricess successfully")
        return results
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch create: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch create failed: {str(e)}")


@router.put("/batch", response_model=List[Base_pricesResponse])
async def update_base_pricess_batch(
    request: Base_pricesBatchUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Update multiple base_pricess in a single request"""
    logger.debug(f"Batch updating {len(request.items)} base_pricess")
    
    service = Base_pricesService(db)
    results = []
    
    try:
        for item in request.items:
            # Only include non-None values for partial updates
            update_dict = {k: v for k, v in item.updates.model_dump().items() if v is not None}
            result = await service.update(item.id, update_dict)
            if result:
                results.append(result)
        
        logger.info(f"Batch updated {len(results)} base_pricess successfully")
        return results
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch update: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch update failed: {str(e)}")


@router.put("/{id}", response_model=Base_pricesResponse)
async def update_base_prices(
    id: int,
    data: Base_pricesUpdateData,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing base_prices"""
    logger.debug(f"Updating base_prices {id} with data: {data}")

    service = Base_pricesService(db)
    try:
        # Only include non-None values for partial updates
        update_dict = {k: v for k, v in data.model_dump().items() if v is not None}
        result = await service.update(id, update_dict)
        if not result:
            logger.warning(f"Base_prices with id {id} not found for update")
            raise HTTPException(status_code=404, detail="Base_prices not found")
        
        logger.info(f"Base_prices {id} updated successfully")
        return result
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error updating base_prices {id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating base_prices {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/batch")
async def delete_base_pricess_batch(
    request: Base_pricesBatchDeleteRequest,
    db: AsyncSession = Depends(get_db),
):
    """Delete multiple base_pricess by their IDs"""
    logger.debug(f"Batch deleting {len(request.ids)} base_pricess")
    
    service = Base_pricesService(db)
    deleted_count = 0
    
    try:
        for item_id in request.ids:
            success = await service.delete(item_id)
            if success:
                deleted_count += 1
        
        logger.info(f"Batch deleted {deleted_count} base_pricess successfully")
        return {"message": f"Successfully deleted {deleted_count} base_pricess", "deleted_count": deleted_count}
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch delete: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch delete failed: {str(e)}")


@router.delete("/{id}")
async def delete_base_prices(
    id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a single base_prices by ID"""
    logger.debug(f"Deleting base_prices with id: {id}")
    
    service = Base_pricesService(db)
    try:
        success = await service.delete(id)
        if not success:
            logger.warning(f"Base_prices with id {id} not found for deletion")
            raise HTTPException(status_code=404, detail="Base_prices not found")
        
        logger.info(f"Base_prices {id} deleted successfully")
        return {"message": "Base_prices deleted successfully", "id": id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting base_prices {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")