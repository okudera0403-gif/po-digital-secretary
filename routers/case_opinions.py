import json
import logging
from typing import List, Optional

from datetime import datetime, date

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from services.case_opinions import Case_opinionsService
from dependencies.auth import get_current_user
from schemas.auth import UserResponse

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/entities/case_opinions", tags=["case_opinions"])


# ---------- Pydantic Schemas ----------
class Case_opinionsData(BaseModel):
    """Entity data schema (for create/update)"""
    case_id: int
    opinion_type_purchase: bool = None
    opinion_type_repair: bool = None
    opinion_type_loan: bool = None
    opinion_type_special: bool = None
    disease_name: str = None
    disability_name_part: str = None
    disability_condition: str = None
    height_cm: float = None
    weight_kg: float = None
    usage_place_home: bool = None
    usage_place_work: bool = None
    usage_place_facility: bool = None
    usage_place_school: bool = None
    usage_place_other: bool = None
    usage_place_other_text: str = None
    frequency_per_day: str = None
    frequency_per_week: str = None
    orthosis_name: str = None
    expected_effect: str = None
    parts_text: str = None
    reason_daily_life_checked: bool = None
    reason_daily_life: str = None
    reason_work_school_checked: bool = None
    reason_work_school: str = None
    reason_other_checked: bool = None
    reason_other: str = None
    doctor_name: str = None
    department_name: str = None
    medical_institution: str = None
    opinion_date: str = None
    generated_draft: str = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Case_opinionsUpdateData(BaseModel):
    """Update entity data (partial updates allowed)"""
    case_id: Optional[int] = None
    opinion_type_purchase: Optional[bool] = None
    opinion_type_repair: Optional[bool] = None
    opinion_type_loan: Optional[bool] = None
    opinion_type_special: Optional[bool] = None
    disease_name: Optional[str] = None
    disability_name_part: Optional[str] = None
    disability_condition: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    usage_place_home: Optional[bool] = None
    usage_place_work: Optional[bool] = None
    usage_place_facility: Optional[bool] = None
    usage_place_school: Optional[bool] = None
    usage_place_other: Optional[bool] = None
    usage_place_other_text: Optional[str] = None
    frequency_per_day: Optional[str] = None
    frequency_per_week: Optional[str] = None
    orthosis_name: Optional[str] = None
    expected_effect: Optional[str] = None
    parts_text: Optional[str] = None
    reason_daily_life_checked: Optional[bool] = None
    reason_daily_life: Optional[str] = None
    reason_work_school_checked: Optional[bool] = None
    reason_work_school: Optional[str] = None
    reason_other_checked: Optional[bool] = None
    reason_other: Optional[str] = None
    doctor_name: Optional[str] = None
    department_name: Optional[str] = None
    medical_institution: Optional[str] = None
    opinion_date: Optional[str] = None
    generated_draft: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Case_opinionsResponse(BaseModel):
    """Entity response schema"""
    id: int
    user_id: str
    case_id: int
    opinion_type_purchase: Optional[bool] = None
    opinion_type_repair: Optional[bool] = None
    opinion_type_loan: Optional[bool] = None
    opinion_type_special: Optional[bool] = None
    disease_name: Optional[str] = None
    disability_name_part: Optional[str] = None
    disability_condition: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    usage_place_home: Optional[bool] = None
    usage_place_work: Optional[bool] = None
    usage_place_facility: Optional[bool] = None
    usage_place_school: Optional[bool] = None
    usage_place_other: Optional[bool] = None
    usage_place_other_text: Optional[str] = None
    frequency_per_day: Optional[str] = None
    frequency_per_week: Optional[str] = None
    orthosis_name: Optional[str] = None
    expected_effect: Optional[str] = None
    parts_text: Optional[str] = None
    reason_daily_life_checked: Optional[bool] = None
    reason_daily_life: Optional[str] = None
    reason_work_school_checked: Optional[bool] = None
    reason_work_school: Optional[str] = None
    reason_other_checked: Optional[bool] = None
    reason_other: Optional[str] = None
    doctor_name: Optional[str] = None
    department_name: Optional[str] = None
    medical_institution: Optional[str] = None
    opinion_date: Optional[str] = None
    generated_draft: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Case_opinionsListResponse(BaseModel):
    """List response schema"""
    items: List[Case_opinionsResponse]
    total: int
    skip: int
    limit: int


class Case_opinionsBatchCreateRequest(BaseModel):
    """Batch create request"""
    items: List[Case_opinionsData]


class Case_opinionsBatchUpdateItem(BaseModel):
    """Batch update item"""
    id: int
    updates: Case_opinionsUpdateData


class Case_opinionsBatchUpdateRequest(BaseModel):
    """Batch update request"""
    items: List[Case_opinionsBatchUpdateItem]


class Case_opinionsBatchDeleteRequest(BaseModel):
    """Batch delete request"""
    ids: List[int]


# ---------- Routes ----------
@router.get("", response_model=Case_opinionsListResponse)
async def query_case_opinionss(
    query: str = Query(None, description="Query conditions (JSON string)"),
    sort: str = Query(None, description="Sort field (prefix with '-' for descending)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=2000, description="Max number of records to return"),
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Query case_opinionss with filtering, sorting, and pagination (user can only see their own records)"""
    logger.debug(f"Querying case_opinionss: query={query}, sort={sort}, skip={skip}, limit={limit}, fields={fields}")
    
    service = Case_opinionsService(db)
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
        logger.debug(f"Found {result['total']} case_opinionss")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying case_opinionss: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/all", response_model=Case_opinionsListResponse)
async def query_case_opinionss_all(
    query: str = Query(None, description="Query conditions (JSON string)"),
    sort: str = Query(None, description="Sort field (prefix with '-' for descending)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=2000, description="Max number of records to return"),
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: AsyncSession = Depends(get_db),
):
    # Query case_opinionss with filtering, sorting, and pagination without user limitation
    logger.debug(f"Querying case_opinionss: query={query}, sort={sort}, skip={skip}, limit={limit}, fields={fields}")

    service = Case_opinionsService(db)
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
        logger.debug(f"Found {result['total']} case_opinionss")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying case_opinionss: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{id}", response_model=Case_opinionsResponse)
async def get_case_opinions(
    id: int,
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single case_opinions by ID (user can only see their own records)"""
    logger.debug(f"Fetching case_opinions with id: {id}, fields={fields}")
    
    service = Case_opinionsService(db)
    try:
        result = await service.get_by_id(id, user_id=str(current_user.id))
        if not result:
            logger.warning(f"Case_opinions with id {id} not found")
            raise HTTPException(status_code=404, detail="Case_opinions not found")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching case_opinions {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("", response_model=Case_opinionsResponse, status_code=201)
async def create_case_opinions(
    data: Case_opinionsData,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new case_opinions"""
    logger.debug(f"Creating new case_opinions with data: {data}")
    
    service = Case_opinionsService(db)
    try:
        result = await service.create(data.model_dump(), user_id=str(current_user.id))
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create case_opinions")
        
        logger.info(f"Case_opinions created successfully with id: {result.id}")
        return result
    except ValueError as e:
        logger.error(f"Validation error creating case_opinions: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating case_opinions: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/batch", response_model=List[Case_opinionsResponse], status_code=201)
async def create_case_opinionss_batch(
    request: Case_opinionsBatchCreateRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create multiple case_opinionss in a single request"""
    logger.debug(f"Batch creating {len(request.items)} case_opinionss")
    
    service = Case_opinionsService(db)
    results = []
    
    try:
        for item_data in request.items:
            result = await service.create(item_data.model_dump(), user_id=str(current_user.id))
            if result:
                results.append(result)
        
        logger.info(f"Batch created {len(results)} case_opinionss successfully")
        return results
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch create: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch create failed: {str(e)}")


@router.put("/batch", response_model=List[Case_opinionsResponse])
async def update_case_opinionss_batch(
    request: Case_opinionsBatchUpdateRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update multiple case_opinionss in a single request (requires ownership)"""
    logger.debug(f"Batch updating {len(request.items)} case_opinionss")
    
    service = Case_opinionsService(db)
    results = []
    
    try:
        for item in request.items:
            # Only include non-None values for partial updates
            update_dict = {k: v for k, v in item.updates.model_dump().items() if v is not None}
            result = await service.update(item.id, update_dict, user_id=str(current_user.id))
            if result:
                results.append(result)
        
        logger.info(f"Batch updated {len(results)} case_opinionss successfully")
        return results
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch update: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch update failed: {str(e)}")


@router.put("/{id}", response_model=Case_opinionsResponse)
async def update_case_opinions(
    id: int,
    data: Case_opinionsUpdateData,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update an existing case_opinions (requires ownership)"""
    logger.debug(f"Updating case_opinions {id} with data: {data}")

    service = Case_opinionsService(db)
    try:
        # Only include non-None values for partial updates
        update_dict = {k: v for k, v in data.model_dump().items() if v is not None}
        result = await service.update(id, update_dict, user_id=str(current_user.id))
        if not result:
            logger.warning(f"Case_opinions with id {id} not found for update")
            raise HTTPException(status_code=404, detail="Case_opinions not found")
        
        logger.info(f"Case_opinions {id} updated successfully")
        return result
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error updating case_opinions {id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating case_opinions {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/batch")
async def delete_case_opinionss_batch(
    request: Case_opinionsBatchDeleteRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete multiple case_opinionss by their IDs (requires ownership)"""
    logger.debug(f"Batch deleting {len(request.ids)} case_opinionss")
    
    service = Case_opinionsService(db)
    deleted_count = 0
    
    try:
        for item_id in request.ids:
            success = await service.delete(item_id, user_id=str(current_user.id))
            if success:
                deleted_count += 1
        
        logger.info(f"Batch deleted {deleted_count} case_opinionss successfully")
        return {"message": f"Successfully deleted {deleted_count} case_opinionss", "deleted_count": deleted_count}
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch delete: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch delete failed: {str(e)}")


@router.delete("/{id}")
async def delete_case_opinions(
    id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a single case_opinions by ID (requires ownership)"""
    logger.debug(f"Deleting case_opinions with id: {id}")
    
    service = Case_opinionsService(db)
    try:
        success = await service.delete(id, user_id=str(current_user.id))
        if not success:
            logger.warning(f"Case_opinions with id {id} not found for deletion")
            raise HTTPException(status_code=404, detail="Case_opinions not found")
        
        logger.info(f"Case_opinions {id} deleted successfully")
        return {"message": "Case_opinions deleted successfully", "id": id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting case_opinions {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")