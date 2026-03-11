import json
import logging
from typing import List, Optional


from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from services.product_price_rules import Product_price_rulesService

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/entities/product_price_rules", tags=["product_price_rules"])


# ---------- Pydantic Schemas ----------
class Product_price_rulesData(BaseModel):
    """Entity data schema (for create/update)"""
    category_name: str = None
    product_name: str = None
    molding_type: str = None
    sub_type: str = None
    price_input_mode: str = None
    base_price_molding: float = None
    base_price_measurement: float = None
    surcharge_label: str = None
    surcharge_price: float = None
    remarks: str = None
    source: str = None


class Product_price_rulesUpdateData(BaseModel):
    """Update entity data (partial updates allowed)"""
    category_name: Optional[str] = None
    product_name: Optional[str] = None
    molding_type: Optional[str] = None
    sub_type: Optional[str] = None
    price_input_mode: Optional[str] = None
    base_price_molding: Optional[float] = None
    base_price_measurement: Optional[float] = None
    surcharge_label: Optional[str] = None
    surcharge_price: Optional[float] = None
    remarks: Optional[str] = None
    source: Optional[str] = None


class Product_price_rulesResponse(BaseModel):
    """Entity response schema"""
    id: int
    category_name: Optional[str] = None
    product_name: Optional[str] = None
    molding_type: Optional[str] = None
    sub_type: Optional[str] = None
    price_input_mode: Optional[str] = None
    base_price_molding: Optional[float] = None
    base_price_measurement: Optional[float] = None
    surcharge_label: Optional[str] = None
    surcharge_price: Optional[float] = None
    remarks: Optional[str] = None
    source: Optional[str] = None

    class Config:
        from_attributes = True


class Product_price_rulesListResponse(BaseModel):
    """List response schema"""
    items: List[Product_price_rulesResponse]
    total: int
    skip: int
    limit: int


class Product_price_rulesBatchCreateRequest(BaseModel):
    """Batch create request"""
    items: List[Product_price_rulesData]


class Product_price_rulesBatchUpdateItem(BaseModel):
    """Batch update item"""
    id: int
    updates: Product_price_rulesUpdateData


class Product_price_rulesBatchUpdateRequest(BaseModel):
    """Batch update request"""
    items: List[Product_price_rulesBatchUpdateItem]


class Product_price_rulesBatchDeleteRequest(BaseModel):
    """Batch delete request"""
    ids: List[int]


# ---------- Routes ----------
@router.get("", response_model=Product_price_rulesListResponse)
async def query_product_price_ruless(
    query: str = Query(None, description="Query conditions (JSON string)"),
    sort: str = Query(None, description="Sort field (prefix with '-' for descending)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=2000, description="Max number of records to return"),
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: AsyncSession = Depends(get_db),
):
    """Query product_price_ruless with filtering, sorting, and pagination"""
    logger.debug(f"Querying product_price_ruless: query={query}, sort={sort}, skip={skip}, limit={limit}, fields={fields}")
    
    service = Product_price_rulesService(db)
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
        logger.debug(f"Found {result['total']} product_price_ruless")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying product_price_ruless: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/all", response_model=Product_price_rulesListResponse)
async def query_product_price_ruless_all(
    query: str = Query(None, description="Query conditions (JSON string)"),
    sort: str = Query(None, description="Sort field (prefix with '-' for descending)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=2000, description="Max number of records to return"),
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: AsyncSession = Depends(get_db),
):
    # Query product_price_ruless with filtering, sorting, and pagination without user limitation
    logger.debug(f"Querying product_price_ruless: query={query}, sort={sort}, skip={skip}, limit={limit}, fields={fields}")

    service = Product_price_rulesService(db)
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
        logger.debug(f"Found {result['total']} product_price_ruless")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying product_price_ruless: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{id}", response_model=Product_price_rulesResponse)
async def get_product_price_rules(
    id: int,
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: AsyncSession = Depends(get_db),
):
    """Get a single product_price_rules by ID"""
    logger.debug(f"Fetching product_price_rules with id: {id}, fields={fields}")
    
    service = Product_price_rulesService(db)
    try:
        result = await service.get_by_id(id)
        if not result:
            logger.warning(f"Product_price_rules with id {id} not found")
            raise HTTPException(status_code=404, detail="Product_price_rules not found")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching product_price_rules {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("", response_model=Product_price_rulesResponse, status_code=201)
async def create_product_price_rules(
    data: Product_price_rulesData,
    db: AsyncSession = Depends(get_db),
):
    """Create a new product_price_rules"""
    logger.debug(f"Creating new product_price_rules with data: {data}")
    
    service = Product_price_rulesService(db)
    try:
        result = await service.create(data.model_dump())
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create product_price_rules")
        
        logger.info(f"Product_price_rules created successfully with id: {result.id}")
        return result
    except ValueError as e:
        logger.error(f"Validation error creating product_price_rules: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating product_price_rules: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/batch", response_model=List[Product_price_rulesResponse], status_code=201)
async def create_product_price_ruless_batch(
    request: Product_price_rulesBatchCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create multiple product_price_ruless in a single request"""
    logger.debug(f"Batch creating {len(request.items)} product_price_ruless")
    
    service = Product_price_rulesService(db)
    results = []
    
    try:
        for item_data in request.items:
            result = await service.create(item_data.model_dump())
            if result:
                results.append(result)
        
        logger.info(f"Batch created {len(results)} product_price_ruless successfully")
        return results
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch create: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch create failed: {str(e)}")


@router.put("/batch", response_model=List[Product_price_rulesResponse])
async def update_product_price_ruless_batch(
    request: Product_price_rulesBatchUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Update multiple product_price_ruless in a single request"""
    logger.debug(f"Batch updating {len(request.items)} product_price_ruless")
    
    service = Product_price_rulesService(db)
    results = []
    
    try:
        for item in request.items:
            # Only include non-None values for partial updates
            update_dict = {k: v for k, v in item.updates.model_dump().items() if v is not None}
            result = await service.update(item.id, update_dict)
            if result:
                results.append(result)
        
        logger.info(f"Batch updated {len(results)} product_price_ruless successfully")
        return results
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch update: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch update failed: {str(e)}")


@router.put("/{id}", response_model=Product_price_rulesResponse)
async def update_product_price_rules(
    id: int,
    data: Product_price_rulesUpdateData,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing product_price_rules"""
    logger.debug(f"Updating product_price_rules {id} with data: {data}")

    service = Product_price_rulesService(db)
    try:
        # Only include non-None values for partial updates
        update_dict = {k: v for k, v in data.model_dump().items() if v is not None}
        result = await service.update(id, update_dict)
        if not result:
            logger.warning(f"Product_price_rules with id {id} not found for update")
            raise HTTPException(status_code=404, detail="Product_price_rules not found")
        
        logger.info(f"Product_price_rules {id} updated successfully")
        return result
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error updating product_price_rules {id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating product_price_rules {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/batch")
async def delete_product_price_ruless_batch(
    request: Product_price_rulesBatchDeleteRequest,
    db: AsyncSession = Depends(get_db),
):
    """Delete multiple product_price_ruless by their IDs"""
    logger.debug(f"Batch deleting {len(request.ids)} product_price_ruless")
    
    service = Product_price_rulesService(db)
    deleted_count = 0
    
    try:
        for item_id in request.ids:
            success = await service.delete(item_id)
            if success:
                deleted_count += 1
        
        logger.info(f"Batch deleted {deleted_count} product_price_ruless successfully")
        return {"message": f"Successfully deleted {deleted_count} product_price_ruless", "deleted_count": deleted_count}
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch delete: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch delete failed: {str(e)}")


@router.delete("/{id}")
async def delete_product_price_rules(
    id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a single product_price_rules by ID"""
    logger.debug(f"Deleting product_price_rules with id: {id}")
    
    service = Product_price_rulesService(db)
    try:
        success = await service.delete(id)
        if not success:
            logger.warning(f"Product_price_rules with id {id} not found for deletion")
            raise HTTPException(status_code=404, detail="Product_price_rules not found")
        
        logger.info(f"Product_price_rules {id} deleted successfully")
        return {"message": "Product_price_rules deleted successfully", "id": id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting product_price_rules {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")