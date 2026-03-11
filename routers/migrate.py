import logging
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/migrate", tags=["migrate"])


# All SQL statements are fully hardcoded - no dynamic construction
_ADD_COLUMN_STATEMENTS: dict[str, text] = {
    "case_number": text('ALTER TABLE cases ADD COLUMN "case_number" VARCHAR'),
    "case_date": text('ALTER TABLE cases ADD COLUMN "case_date" VARCHAR'),
    "category_name": text('ALTER TABLE cases ADD COLUMN "category_name" VARCHAR'),
    "case_status": text('ALTER TABLE cases ADD COLUMN "case_status" VARCHAR'),
    "case_type": text('ALTER TABLE cases ADD COLUMN "case_type" VARCHAR'),
    "patient_name": text('ALTER TABLE cases ADD COLUMN "patient_name" VARCHAR'),
    "patient_age": text('ALTER TABLE cases ADD COLUMN "patient_age" INTEGER'),
    "patient_dob": text('ALTER TABLE cases ADD COLUMN "patient_dob" VARCHAR'),
    "gender": text('ALTER TABLE cases ADD COLUMN "gender" VARCHAR'),
    "patient_address": text('ALTER TABLE cases ADD COLUMN "patient_address" VARCHAR'),
    "living_situation": text('ALTER TABLE cases ADD COLUMN "living_situation" VARCHAR'),
    "facility_name": text('ALTER TABLE cases ADD COLUMN "facility_name" VARCHAR'),
    "discharge_estimate": text('ALTER TABLE cases ADD COLUMN "discharge_estimate" VARCHAR'),
    "insurance_type_id": text('ALTER TABLE cases ADD COLUMN "insurance_type_id" VARCHAR'),
    "insurance_name": text('ALTER TABLE cases ADD COLUMN "insurance_name" VARCHAR'),
    "category_id": text('ALTER TABLE cases ADD COLUMN "category_id" VARCHAR'),
    "product_id": text('ALTER TABLE cases ADD COLUMN "product_id" VARCHAR'),
    "product_name": text('ALTER TABLE cases ADD COLUMN "product_name" VARCHAR'),
    "side": text('ALTER TABLE cases ADD COLUMN "side" VARCHAR'),
    "disease_name": text('ALTER TABLE cases ADD COLUMN "disease_name" VARCHAR'),
    "disability_name": text('ALTER TABLE cases ADD COLUMN "disability_name" VARCHAR'),
    "disability_site": text('ALTER TABLE cases ADD COLUMN "disability_site" VARCHAR'),
    "disability_detail": text('ALTER TABLE cases ADD COLUMN "disability_detail" VARCHAR'),
    "symptoms": text('ALTER TABLE cases ADD COLUMN "symptoms" VARCHAR'),
    "diagnosis": text('ALTER TABLE cases ADD COLUMN "diagnosis" VARCHAR'),
    "height_cm": text('ALTER TABLE cases ADD COLUMN "height_cm" FLOAT'),
    "weight_kg": text('ALTER TABLE cases ADD COLUMN "weight_kg" FLOAT'),
    "usage_location": text('ALTER TABLE cases ADD COLUMN "usage_location" VARCHAR'),
    "usage_hours_per_day": text('ALTER TABLE cases ADD COLUMN "usage_hours_per_day" FLOAT'),
    "usage_days_per_week": text('ALTER TABLE cases ADD COLUMN "usage_days_per_week" FLOAT'),
    "device_name": text('ALTER TABLE cases ADD COLUMN "device_name" VARCHAR'),
    "expected_effect": text('ALTER TABLE cases ADD COLUMN "expected_effect" VARCHAR'),
    "parts_used": text('ALTER TABLE cases ADD COLUMN "parts_used" VARCHAR'),
    "parts_reason_daily": text('ALTER TABLE cases ADD COLUMN "parts_reason_daily" VARCHAR'),
    "parts_reason_work": text('ALTER TABLE cases ADD COLUMN "parts_reason_work" VARCHAR'),
    "parts_reason_other": text('ALTER TABLE cases ADD COLUMN "parts_reason_other" VARCHAR'),
    "doctor_name": text('ALTER TABLE cases ADD COLUMN "doctor_name" VARCHAR'),
    "hospital_name": text('ALTER TABLE cases ADD COLUMN "hospital_name" VARCHAR'),
    "department_name": text('ALTER TABLE cases ADD COLUMN "department_name" VARCHAR'),
    "bank_transfer": text('ALTER TABLE cases ADD COLUMN "bank_transfer" BOOLEAN'),
    "invoice_needed": text('ALTER TABLE cases ADD COLUMN "invoice_needed" BOOLEAN'),
    "certificate_received": text('ALTER TABLE cases ADD COLUMN "certificate_received" BOOLEAN'),
    "order_date": text('ALTER TABLE cases ADD COLUMN "order_date" VARCHAR'),
    "fitting_date": text('ALTER TABLE cases ADD COLUMN "fitting_date" VARCHAR'),
    "completion_date": text('ALTER TABLE cases ADD COLUMN "completion_date" VARCHAR'),
    "delivery_date": text('ALTER TABLE cases ADD COLUMN "delivery_date" VARCHAR'),
    "created_at": text('ALTER TABLE cases ADD COLUMN "created_at" TIMESTAMP WITH TIME ZONE'),
    "updated_at": text('ALTER TABLE cases ADD COLUMN "updated_at" TIMESTAMP WITH TIME ZONE'),
    "remarks": text('ALTER TABLE cases ADD COLUMN "remarks" VARCHAR'),
    "media_files": text('ALTER TABLE cases ADD COLUMN "media_files" VARCHAR'),
}

_FIX_TYPE_STATEMENTS: dict[str, text] = {
    "insurance_type_id": text(
        'ALTER TABLE cases ALTER COLUMN "insurance_type_id" '
        'TYPE VARCHAR USING "insurance_type_id"::VARCHAR'
    ),
    "category_id": text(
        'ALTER TABLE cases ALTER COLUMN "category_id" '
        'TYPE VARCHAR USING "category_id"::VARCHAR'
    ),
    "product_id": text(
        'ALTER TABLE cases ALTER COLUMN "product_id" '
        'TYPE VARCHAR USING "product_id"::VARCHAR'
    ),
}

_CHECK_COLUMN_SQL = text(
    "SELECT column_name FROM information_schema.columns "
    "WHERE table_name = :table_name AND column_name = :col_name"
)

_LIST_COLUMNS_SQL = text(
    "SELECT column_name, data_type FROM information_schema.columns "
    "WHERE table_name = 'cases' ORDER BY ordinal_position"
)

# Products table migration - add new columns
_PRODUCTS_ADD_COLUMN_STATEMENTS: dict[str, text] = {
    "product_code": text('ALTER TABLE products ADD COLUMN "product_code" VARCHAR'),
    "type_variant": text('ALTER TABLE products ADD COLUMN "type_variant" VARCHAR'),
    "structure_notes": text('ALTER TABLE products ADD COLUMN "structure_notes" VARCHAR'),
    "durability_years": text('ALTER TABLE products ADD COLUMN "durability_years" FLOAT'),
    "source": text('ALTER TABLE products ADD COLUMN "source" VARCHAR'),
}


@router.post("/cases-columns")
async def add_missing_cases_columns(
    db: AsyncSession = Depends(get_db),
):
    """Add missing columns to cases table if they don't exist.
    All SQL statements are pre-defined constants - no dynamic SQL construction."""
    added = []
    already_exists = []
    errors = []

    for col_name, add_stmt in _ADD_COLUMN_STATEMENTS.items():
        try:
            result = await db.execute(_CHECK_COLUMN_SQL, {"table_name": "cases", "col_name": col_name})
            row = result.fetchone()

            if row is None:
                await db.execute(add_stmt)
                await db.commit()
                added.append(col_name)
                logger.info("Added column %s to cases table", col_name)
            else:
                already_exists.append(col_name)
        except Exception as e:
            errors.append({"column": col_name, "error": str(e)})
            logger.error("Error adding column %s: %s", col_name, e)
            await db.rollback()

    return {
        "added": added,
        "already_exists": already_exists,
        "errors": errors,
    }


@router.post("/products-columns")
async def add_missing_products_columns(
    db: AsyncSession = Depends(get_db),
):
    """Add missing columns to products table if they don't exist.
    All SQL statements are pre-defined constants - no dynamic SQL construction."""
    added = []
    already_exists = []
    errors = []

    for col_name, add_stmt in _PRODUCTS_ADD_COLUMN_STATEMENTS.items():
        try:
            result = await db.execute(_CHECK_COLUMN_SQL, {"table_name": "products", "col_name": col_name})
            row = result.fetchone()

            if row is None:
                await db.execute(add_stmt)
                await db.commit()
                added.append(col_name)
                logger.info("Added column %s to products table", col_name)
            else:
                already_exists.append(col_name)
        except Exception as e:
            errors.append({"column": col_name, "error": str(e)})
            logger.error("Error adding column %s: %s", col_name, e)
            await db.rollback()

    return {
        "added": added,
        "already_exists": already_exists,
        "errors": errors,
    }


@router.post("/fix-column-types")
async def fix_column_types(
    db: AsyncSession = Depends(get_db),
):
    """Fix column types that are integer but should be varchar.
    All SQL statements are pre-defined constants - no dynamic SQL construction."""
    fixed = []
    errors = []

    for col_name, fix_stmt in _FIX_TYPE_STATEMENTS.items():
        try:
            await db.execute(fix_stmt)
            await db.commit()
            fixed.append(col_name)
            logger.info("Changed column %s to VARCHAR", col_name)
        except Exception as e:
            errors.append({"column": col_name, "error": str(e)})
            logger.error("Error fixing column %s: %s", col_name, e)
            await db.rollback()

    return {"fixed": fixed, "errors": errors}


@router.get("/cases-columns")
async def check_cases_columns(
    db: AsyncSession = Depends(get_db),
):
    """Check which columns exist in the cases table."""
    try:
        result = await db.execute(_LIST_COLUMNS_SQL)
        rows = result.fetchall()
        return {
            "columns": [{"name": row[0], "type": row[1]} for row in rows],
            "count": len(rows),
        }
    except Exception as e:
        return {"error": str(e)}