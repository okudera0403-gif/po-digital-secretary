import logging
from typing import Optional, Dict, Any, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.insurance_types import Insurance_types

logger = logging.getLogger(__name__)


# ------------------ Service Layer ------------------
class Insurance_typesService:
    """Service layer for Insurance_types operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: Dict[str, Any]) -> Optional[Insurance_types]:
        """Create a new insurance_types"""
        try:
            obj = Insurance_types(**data)
            self.db.add(obj)
            await self.db.commit()
            await self.db.refresh(obj)
            logger.info(f"Created insurance_types with id: {obj.id}")
            return obj
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating insurance_types: {str(e)}")
            raise

    async def get_by_id(self, obj_id: int) -> Optional[Insurance_types]:
        """Get insurance_types by ID"""
        try:
            query = select(Insurance_types).where(Insurance_types.id == obj_id)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching insurance_types {obj_id}: {str(e)}")
            raise

    async def get_list(
        self, 
        skip: int = 0, 
        limit: int = 20, 
        query_dict: Optional[Dict[str, Any]] = None,
        sort: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get paginated list of insurance_typess"""
        try:
            query = select(Insurance_types)
            count_query = select(func.count(Insurance_types.id))
            
            if query_dict:
                for field, value in query_dict.items():
                    if hasattr(Insurance_types, field):
                        query = query.where(getattr(Insurance_types, field) == value)
                        count_query = count_query.where(getattr(Insurance_types, field) == value)
            
            count_result = await self.db.execute(count_query)
            total = count_result.scalar()

            if sort:
                if sort.startswith('-'):
                    field_name = sort[1:]
                    if hasattr(Insurance_types, field_name):
                        query = query.order_by(getattr(Insurance_types, field_name).desc())
                else:
                    if hasattr(Insurance_types, sort):
                        query = query.order_by(getattr(Insurance_types, sort))
            else:
                query = query.order_by(Insurance_types.id.desc())

            result = await self.db.execute(query.offset(skip).limit(limit))
            items = result.scalars().all()

            return {
                "items": items,
                "total": total,
                "skip": skip,
                "limit": limit,
            }
        except Exception as e:
            logger.error(f"Error fetching insurance_types list: {str(e)}")
            raise

    async def update(self, obj_id: int, update_data: Dict[str, Any]) -> Optional[Insurance_types]:
        """Update insurance_types"""
        try:
            obj = await self.get_by_id(obj_id)
            if not obj:
                logger.warning(f"Insurance_types {obj_id} not found for update")
                return None
            for key, value in update_data.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)

            await self.db.commit()
            await self.db.refresh(obj)
            logger.info(f"Updated insurance_types {obj_id}")
            return obj
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating insurance_types {obj_id}: {str(e)}")
            raise

    async def delete(self, obj_id: int) -> bool:
        """Delete insurance_types"""
        try:
            obj = await self.get_by_id(obj_id)
            if not obj:
                logger.warning(f"Insurance_types {obj_id} not found for deletion")
                return False
            await self.db.delete(obj)
            await self.db.commit()
            logger.info(f"Deleted insurance_types {obj_id}")
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting insurance_types {obj_id}: {str(e)}")
            raise

    async def get_by_field(self, field_name: str, field_value: Any) -> Optional[Insurance_types]:
        """Get insurance_types by any field"""
        try:
            if not hasattr(Insurance_types, field_name):
                raise ValueError(f"Field {field_name} does not exist on Insurance_types")
            result = await self.db.execute(
                select(Insurance_types).where(getattr(Insurance_types, field_name) == field_value)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching insurance_types by {field_name}: {str(e)}")
            raise

    async def list_by_field(
        self, field_name: str, field_value: Any, skip: int = 0, limit: int = 20
    ) -> List[Insurance_types]:
        """Get list of insurance_typess filtered by field"""
        try:
            if not hasattr(Insurance_types, field_name):
                raise ValueError(f"Field {field_name} does not exist on Insurance_types")
            result = await self.db.execute(
                select(Insurance_types)
                .where(getattr(Insurance_types, field_name) == field_value)
                .offset(skip)
                .limit(limit)
                .order_by(Insurance_types.id.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching insurance_typess by {field_name}: {str(e)}")
            raise