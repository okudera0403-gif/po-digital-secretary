import json
import logging
from typing import List, Optional

from datetime import datetime, date

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from services.cases import CasesService
from dependencies.auth import get_current_user
from schemas.auth import UserResponse

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/entities/cases", tags=["cases"])


# ---------- Pydantic Schemas ----------
class CasesData(BaseModel):
    """Entity data schema (for create/update)"""
    case_number: str = None
    case_status: str = None
    case_type: str = None
    case_date: str = None
    order_date: str = None
    fitting_date: str = None
    completion_date: str = None
    delivery_date: str = None
    patient_name: str = None
    patient_age: int = None
    patient_dob: str = None
    gender: str = None
    patient_address: str = None
    living_situation: str = None
    facility_name: str = None
    discharge_estimate: str = None
    insurance_type_id: str = None
    insurance_name: str = None
    category_id: str = None
    category_name: str = None
    product_id: str = None
    product_name: str = None
    side: str = None
    disease_name: str = None
    disability_name: str = None
    disability_site: str = None
    disability_detail: str = None
    symptoms: str = None
    diagnosis: str = None
    height_cm: float = None
    weight_kg: float = None
    usage_location: str = None
    usage_hours_per_day: float = None
    usage_days_per_week: float = None
    device_name: str = None
    expected_effect: str = None
    parts_used: str = None
    parts_reason_daily: str = None
    parts_reason_work: str = None
    parts_reason_other: str = None
    doctor_name: str = None
    hospital_name: str = None
    department_name: str = None
    bank_transfer: bool = None
    invoice_needed: bool = None
    certificate_received: bool = None
    remarks: str = None
    media_files: str = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CasesUpdateData(BaseModel):
    """Update entity data (partial updates allowed)"""
    case_number: Optional[str] = None
    case_status: Optional[str] = None
    case_type: Optional[str] = None
    case_date: Optional[str] = None
    order_date: Optional[str] = None
    fitting_date: Optional[str] = None
    completion_date: Optional[str] = None
    delivery_date: Optional[str] = None
    patient_name: Optional[str] = None
    patient_age: Optional[int] = None
    patient_dob: Optional[str] = None
    gender: Optional[str] = None
    patient_address: Optional[str] = None
    living_situation: Optional[str] = None
    facility_name: Optional[str] = None
    discharge_estimate: Optional[str] = None
    insurance_type_id: Optional[str] = None
    insurance_name: Optional[str] = None
    category_id: Optional[str] = None
    category_name: Optional[str] = None
    product_id: Optional[str] = None
    product_name: Optional[str] = None
    side: Optional[str] = None
    disease_name: Optional[str] = None
    disability_name: Optional[str] = None
    disability_site: Optional[str] = None
    disability_detail: Optional[str] = None
    symptoms: Optional[str] = None
    diagnosis: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    usage_location: Optional[str] = None
    usage_hours_per_day: Optional[float] = None
    usage_days_per_week: Optional[float] = None
    device_name: Optional[str] = None
    expected_effect: Optional[str] = None
    parts_used: Optional[str] = None
    parts_reason_daily: Optional[str] = None
    parts_reason_work: Optional[str] = None
    parts_reason_other: Optional[str] = None
    doctor_name: Optional[str] = None
    hospital_name: Optional[str] = None
    department_name: Optional[str] = None
    bank_transfer: Optional[bool] = None
    invoice_needed: Optional[bool] = None
    certificate_received: Optional[bool] = None
    remarks: Optional[str] = None
    media_files: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CasesResponse(BaseModel):
    """Entity response schema"""
    id: int
    user_id: str
    case_number: Optional[str] = None
    case_status: Optional[str] = None
    case_type: Optional[str] = None
    case_date: Optional[str] = None
    order_date: Optional[str] = None
    fitting_date: Optional[str] = None
    completion_date: Optional[str] = None
    delivery_date: Optional[str] = None
    patient_name: Optional[str] = None
    patient_age: Optional[int] = None
    patient_dob: Optional[str] = None
    gender: Optional[str] = None
    patient_address: Optional[str] = None
    living_situation: Optional[str] = None
    facility_name: Optional[str] = None
    discharge_estimate: Optional[str] = None
    insurance_type_id: Optional[str] = None
    insurance_name: Optional[str] = None
    category_id: Optional[str] = None
    category_name: Optional[str] = None
    product_id: Optional[str] = None
    product_name: Optional[str] = None
    side: Optional[str] = None
    disease_name: Optional[str] = None
    disability_name: Optional[str] = None
    disability_site: Optional[str] = None
    disability_detail: Optional[str] = None
    symptoms: Optional[str] = None
    diagnosis: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    usage_location: Optional[str] = None
    usage_hours_per_day: Optional[float] = None
    usage_days_per_week: Optional[float] = None
    device_name: Optional[str] = None
    expected_effect: Optional[str] = None
    parts_used: Optional[str] = None
    parts_reason_daily: Optional[str] = None
    parts_reason_work: Optional[str] = None
    parts_reason_other: Optional[str] = None
    doctor_name: Optional[str] = None
    hospital_name: Optional[str] = None
    department_name: Optional[str] = None
    bank_transfer: Optional[bool] = None
    invoice_needed: Optional[bool] = None
    certificate_received: Optional[bool] = None
    remarks: Optional[str] = None
    media_files: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CasesListResponse(BaseModel):
    """List response schema"""
    items: List[CasesResponse]
    total: int
    skip: int
    limit: int


class CasesBatchCreateRequest(BaseModel):
    """Batch create request"""
    items: List[CasesData]


class CasesBatchUpdateItem(BaseModel):
    """Batch update item"""
    id: int
    updates: CasesUpdateData


class CasesBatchUpdateRequest(BaseModel):
    """Batch update request"""
    items: List[CasesBatchUpdateItem]


class CasesBatchDeleteRequest(BaseModel):
    """Batch delete request"""
    ids: List[int]


# ---------- Routes ----------
@router.get("", response_model=CasesListResponse)
async def query_casess(
    query: str = Query(None, description="Query conditions (JSON string)"),
    sort: str = Query(None, description="Sort field (prefix with '-' for descending)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=2000, description="Max number of records to return"),
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Query casess with filtering, sorting, and pagination (user can only see their own records)"""
    logger.debug(f"Querying casess: query={query}, sort={sort}, skip={skip}, limit={limit}, fields={fields}")
    
    service = CasesService(db)
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
        logger.debug(f"Found {result['total']} casess")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying casess: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/all", response_model=CasesListResponse)
async def query_casess_all(
    query: str = Query(None, description="Query conditions (JSON string)"),
    sort: str = Query(None, description="Sort field (prefix with '-' for descending)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=2000, description="Max number of records to return"),
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: AsyncSession = Depends(get_db),
):
    # Query casess with filtering, sorting, and pagination without user limitation
    logger.debug(f"Querying casess: query={query}, sort={sort}, skip={skip}, limit={limit}, fields={fields}")

    service = CasesService(db)
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
        logger.debug(f"Found {result['total']} casess")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying casess: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{id}", response_model=CasesResponse)
async def get_cases(
    id: int,
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single cases by ID (user can only see their own records)"""
    logger.debug(f"Fetching cases with id: {id}, fields={fields}")
    
    service = CasesService(db)
    try:
        result = await service.get_by_id(id, user_id=str(current_user.id))
        if not result:
            logger.warning(f"Cases with id {id} not found")
            raise HTTPException(status_code=404, detail="Cases not found")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching cases {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("", response_model=CasesResponse, status_code=201)
async def create_cases(
    data: CasesData,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new cases"""
    logger.debug(f"Creating new cases with data: {data}")
    
    service = CasesService(db)
    try:
        result = await service.create(data.model_dump(), user_id=str(current_user.id))
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create cases")
        
        logger.info(f"Cases created successfully with id: {result.id}")
        return result
    except ValueError as e:
        logger.error(f"Validation error creating cases: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating cases: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/batch", response_model=List[CasesResponse], status_code=201)
async def create_casess_batch(
    request: CasesBatchCreateRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create multiple casess in a single request"""
    logger.debug(f"Batch creating {len(request.items)} casess")
    
    service = CasesService(db)
    results = []
    
    try:
        for item_data in request.items:
            result = await service.create(item_data.model_dump(), user_id=str(current_user.id))
            if result:
                results.append(result)
        
        logger.info(f"Batch created {len(results)} casess successfully")
        return results
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch create: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch create failed: {str(e)}")


@router.put("/batch", response_model=List[CasesResponse])
async def update_casess_batch(
    request: CasesBatchUpdateRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update multiple casess in a single request (requires ownership)"""
    logger.debug(f"Batch updating {len(request.items)} casess")
    
    service = CasesService(db)
    results = []
    
    try:
        for item in request.items:
            # Only include non-None values for partial updates
            update_dict = {k: v for k, v in item.updates.model_dump().items() if v is not None}
            result = await service.update(item.id, update_dict, user_id=str(current_user.id))
            if result:
                results.append(result)
        
        logger.info(f"Batch updated {len(results)} casess successfully")
        return results
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch update: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch update failed: {str(e)}")


@router.put("/{id}", response_model=CasesResponse)
async def update_cases(
    id: int,
    data: CasesUpdateData,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update an existing cases (requires ownership)"""
    logger.debug(f"Updating cases {id} with data: {data}")

    service = CasesService(db)
    try:
        # Only include non-None values for partial updates
        update_dict = {k: v for k, v in data.model_dump().items() if v is not None}
        result = await service.update(id, update_dict, user_id=str(current_user.id))
        if not result:
            logger.warning(f"Cases with id {id} not found for update")
            raise HTTPException(status_code=404, detail="Cases not found")
        
        logger.info(f"Cases {id} updated successfully")
        return result
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error updating cases {id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating cases {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/batch")
async def delete_casess_batch(
    request: CasesBatchDeleteRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete multiple casess by their IDs (requires ownership)"""
    logger.debug(f"Batch deleting {len(request.ids)} casess")
    
    service = CasesService(db)
    deleted_count = 0
    
    try:
        for item_id in request.ids:
            success = await service.delete(item_id, user_id=str(current_user.id))
            if success:
                deleted_count += 1
        
        logger.info(f"Batch deleted {deleted_count} casess successfully")
        return {"message": f"Successfully deleted {deleted_count} casess", "deleted_count": deleted_count}
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch delete: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch delete failed: {str(e)}")


@router.delete("/{id}")
async def delete_cases(
    id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a single cases by ID (requires ownership)"""
    logger.debug(f"Deleting cases with id: {id}")
    
    service = CasesService(db)
    try:
        success = await service.delete(id, user_id=str(current_user.id))
        if not success:
            logger.warning(f"Cases with id {id} not found for deletion")
            raise HTTPException(status_code=404, detail="Cases not found")
        
        logger.info(f"Cases {id} deleted successfully")
        return {"message": "Cases deleted successfully", "id": id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting cases {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")