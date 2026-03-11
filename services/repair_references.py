import logging
from typing import Optional, Dict, Any, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.repair_references import Repair_references

logger = logging.getLogger(__name__)


# ------------------ Service Layer ------------------
class Repair_referencesService:
    """Service layer for Repair_references operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: Dict[str, Any]) -> Optional[Repair_references]:
        """Create a new repair_references"""
        try:
            obj = Repair_references(**data)
            self.db.add(obj)
            await self.db.commit()
            await self.db.refresh(obj)
            logger.info(f"Created repair_references with id: {obj.id}")
            return obj
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating repair_references: {str(e)}")
            raise

    async def get_by_id(self, obj_id: int) -> Optional[Repair_references]:
        """Get repair_references by ID"""
        try:
            query = select(Repair_references).where(Repair_references.id == obj_id)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching repair_references {obj_id}: {str(e)}")
            raise

    async def get_list(
        self, 
        skip: int = 0, 
        limit: int = 20, 
        query_dict: Optional[Dict[str, Any]] = None,
        sort: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get paginated list of repair_referencess"""
        try:
            query = select(Repair_references)
            count_query = select(func.count(Repair_references.id))
            
            if query_dict:
                for field, value in query_dict.items():
                    if hasattr(Repair_references, field):
                        query = query.where(getattr(Repair_references, field) == value)
                        count_query = count_query.where(getattr(Repair_references, field) == value)
            
            count_result = await self.db.execute(count_query)
            total = count_result.scalar()

            if sort:
                if sort.startswith('-'):
                    field_name = sort[1:]
                    if hasattr(Repair_references, field_name):
                        query = query.order_by(getattr(Repair_references, field_name).desc())
                else:
                    if hasattr(Repair_references, sort):
                        query = query.order_by(getattr(Repair_references, sort))
            else:
                query = query.order_by(Repair_references.id.desc())

            result = await self.db.execute(query.offset(skip).limit(limit))
            items = result.scalars().all()

            return {
                "items": items,
                "total": total,
                "skip": skip,
                "limit": limit,
            }
        except Exception as e:
            logger.error(f"Error fetching repair_references list: {str(e)}")
            raise

    async def update(self, obj_id: int, update_data: Dict[str, Any]) -> Optional[Repair_references]:
        """Update repair_references"""
        try:
            obj = await self.get_by_id(obj_id)
            if not obj:
                logger.warning(f"Repair_references {obj_id} not found for update")
                return None
            for key, value in update_data.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)

            await self.db.commit()
            await self.db.refresh(obj)
            logger.info(f"Updated repair_references {obj_id}")
            return obj
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating repair_references {obj_id}: {str(e)}")
            raise

    async def delete(self, obj_id: int) -> bool:
        """Delete repair_references"""
        try:
            obj = await self.get_by_id(obj_id)
            if not obj:
                logger.warning(f"Repair_references {obj_id} not found for deletion")
                return False
            await self.db.delete(obj)
            await self.db.commit()
            logger.info(f"Deleted repair_references {obj_id}")
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting repair_references {obj_id}: {str(e)}")
            raise

    async def get_by_field(self, field_name: str, field_value: Any) -> Optional[Repair_references]:
        """Get repair_references by any field"""
        try:
            if not hasattr(Repair_references, field_name):
                raise ValueError(f"Field {field_name} does not exist on Repair_references")
            result = await self.db.execute(
                select(Repair_references).where(getattr(Repair_references, field_name) == field_value)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching repair_references by {field_name}: {str(e)}")
            raise

    async def list_by_field(
        self, field_name: str, field_value: Any, skip: int = 0, limit: int = 20
    ) -> List[Repair_references]:
        """Get list of repair_referencess filtered by field"""
        try:
            if not hasattr(Repair_references, field_name):
                raise ValueError(f"Field {field_name} does not exist on Repair_references")
            result = await self.db.execute(
                select(Repair_references)
                .where(getattr(Repair_references, field_name) == field_value)
                .offset(skip)
                .limit(limit)
                .order_by(Repair_references.id.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching repair_referencess by {field_name}: {str(e)}")
            raise