import json
import logging
from typing import List, Optional


from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from services.instruction_templates import Instruction_templatesService

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/entities/instruction_templates", tags=["instruction_templates"])


# ---------- Pydantic Schemas ----------
class Instruction_templatesData(BaseModel):
    """Entity data schema (for create/update)"""
    product_code: str
    product_name: str = None
    field_name: str
    input_type: str
    required_flag: int = None
    option_values: str = None
    sort_order: int


class Instruction_templatesUpdateData(BaseModel):
    """Update entity data (partial updates allowed)"""
    product_code: Optional[str] = None
    product_name: Optional[str] = None
    field_name: Optional[str] = None
    input_type: Optional[str] = None
    required_flag: Optional[int] = None
    option_values: Optional[str] = None
    sort_order: Optional[int] = None


class Instruction_templatesResponse(BaseModel):
    """Entity response schema"""
    id: int
    product_code: str
    product_name: Optional[str] = None
    field_name: str
    input_type: str
    required_flag: Optional[int] = None
    option_values: Optional[str] = None
    sort_order: int

    class Config:
        from_attributes = True


class Instruction_templatesListResponse(BaseModel):
    """List response schema"""
    items: List[Instruction_templatesResponse]
    total: int
    skip: int
    limit: int


class Instruction_templatesBatchCreateRequest(BaseModel):
    """Batch create request"""
    items: List[Instruction_templatesData]


class Instruction_templatesBatchUpdateItem(BaseModel):
    """Batch update item"""
    id: int
    updates: Instruction_templatesUpdateData


class Instruction_templatesBatchUpdateRequest(BaseModel):
    """Batch update request"""
    items: List[Instruction_templatesBatchUpdateItem]


class Instruction_templatesBatchDeleteRequest(BaseModel):
    """Batch delete request"""
    ids: List[int]


# ---------- Routes ----------
@router.get("", response_model=Instruction_templatesListResponse)
async def query_instruction_templatess(
    query: str = Query(None, description="Query conditions (JSON string)"),
    sort: str = Query(None, description="Sort field (prefix with '-' for descending)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=2000, description="Max number of records to return"),
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: AsyncSession = Depends(get_db),
):
    """Query instruction_templatess with filtering, sorting, and pagination"""
    logger.debug(f"Querying instruction_templatess: query={query}, sort={sort}, skip={skip}, limit={limit}, fields={fields}")
    
    service = Instruction_templatesService(db)
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
        logger.debug(f"Found {result['total']} instruction_templatess")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying instruction_templatess: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/all", response_model=Instruction_templatesListResponse)
async def query_instruction_templatess_all(
    query: str = Query(None, description="Query conditions (JSON string)"),
    sort: str = Query(None, description="Sort field (prefix with '-' for descending)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=2000, description="Max number of records to return"),
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: AsyncSession = Depends(get_db),
):
    # Query instruction_templatess with filtering, sorting, and pagination without user limitation
    logger.debug(f"Querying instruction_templatess: query={query}, sort={sort}, skip={skip}, limit={limit}, fields={fields}")

    service = Instruction_templatesService(db)
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
        logger.debug(f"Found {result['total']} instruction_templatess")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying instruction_templatess: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{id}", response_model=Instruction_templatesResponse)
async def get_instruction_templates(
    id: int,
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: AsyncSession = Depends(get_db),
):
    """Get a single instruction_templates by ID"""
    logger.debug(f"Fetching instruction_templates with id: {id}, fields={fields}")
    
    service = Instruction_templatesService(db)
    try:
        result = await service.get_by_id(id)
        if not result:
            logger.warning(f"Instruction_templates with id {id} not found")
            raise HTTPException(status_code=404, detail="Instruction_templates not found")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching instruction_templates {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("", response_model=Instruction_templatesResponse, status_code=201)
async def create_instruction_templates(
    data: Instruction_templatesData,
    db: AsyncSession = Depends(get_db),
):
    """Create a new instruction_templates"""
    logger.debug(f"Creating new instruction_templates with data: {data}")
    
    service = Instruction_templatesService(db)
    try:
        result = await service.create(data.model_dump())
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create instruction_templates")
        
        logger.info(f"Instruction_templates created successfully with id: {result.id}")
        return result
    except ValueError as e:
        logger.error(f"Validation error creating instruction_templates: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating instruction_templates: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/batch", response_model=List[Instruction_templatesResponse], status_code=201)
async def create_instruction_templatess_batch(
    request: Instruction_templatesBatchCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create multiple instruction_templatess in a single request"""
    logger.debug(f"Batch creating {len(request.items)} instruction_templatess")
    
    service = Instruction_templatesService(db)
    results = []
    
    try:
        for item_data in request.items:
            result = await service.create(item_data.model_dump())
            if result:
                results.append(result)
        
        logger.info(f"Batch created {len(results)} instruction_templatess successfully")
        return results
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch create: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch create failed: {str(e)}")


@router.put("/batch", response_model=List[Instruction_templatesResponse])
async def update_instruction_templatess_batch(
    request: Instruction_templatesBatchUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Update multiple instruction_templatess in a single request"""
    logger.debug(f"Batch updating {len(request.items)} instruction_templatess")
    
    service = Instruction_templatesService(db)
    results = []
    
    try:
        for item in request.items:
            # Only include non-None values for partial updates
            update_dict = {k: v for k, v in item.updates.model_dump().items() if v is not None}
            result = await service.update(item.id, update_dict)
            if result:
                results.append(result)
        
        logger.info(f"Batch updated {len(results)} instruction_templatess successfully")
        return results
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch update: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch update failed: {str(e)}")


@router.put("/{id}", response_model=Instruction_templatesResponse)
async def update_instruction_templates(
    id: int,
    data: Instruction_templatesUpdateData,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing instruction_templates"""
    logger.debug(f"Updating instruction_templates {id} with data: {data}")

    service = Instruction_templatesService(db)
    try:
        # Only include non-None values for partial updates
        update_dict = {k: v for k, v in data.model_dump().items() if v is not None}
        result = await service.update(id, update_dict)
        if not result:
            logger.warning(f"Instruction_templates with id {id} not found for update")
            raise HTTPException(status_code=404, detail="Instruction_templates not found")
        
        logger.info(f"Instruction_templates {id} updated successfully")
        return result
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error updating instruction_templates {id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating instruction_templates {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/batch")
async def delete_instruction_templatess_batch(
    request: Instruction_templatesBatchDeleteRequest,
    db: AsyncSession = Depends(get_db),
):
    """Delete multiple instruction_templatess by their IDs"""
    logger.debug(f"Batch deleting {len(request.ids)} instruction_templatess")
    
    service = Instruction_templatesService(db)
    deleted_count = 0
    
    try:
        for item_id in request.ids:
            success = await service.delete(item_id)
            if success:
                deleted_count += 1
        
        logger.info(f"Batch deleted {deleted_count} instruction_templatess successfully")
        return {"message": f"Successfully deleted {deleted_count} instruction_templatess", "deleted_count": deleted_count}
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch delete: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch delete failed: {str(e)}")


@router.delete("/{id}")
async def delete_instruction_templates(
    id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a single instruction_templates by ID"""
    logger.debug(f"Deleting instruction_templates with id: {id}")
    
    service = Instruction_templatesService(db)
    try:
        success = await service.delete(id)
        if not success:
            logger.warning(f"Instruction_templates with id {id} not found for deletion")
            raise HTTPException(status_code=404, detail="Instruction_templates not found")
        
        logger.info(f"Instruction_templates {id} deleted successfully")
        return {"message": "Instruction_templates deleted successfully", "id": id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting instruction_templates {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")