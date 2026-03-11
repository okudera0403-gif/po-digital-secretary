import logging
from typing import Optional, Dict, Any, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.parts import Parts

logger = logging.getLogger(__name__)


# ------------------ Service Layer ------------------
class PartsService:
    """Service layer for Parts operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: Dict[str, Any]) -> Optional[Parts]:
        """Create a new parts"""
        try:
            obj = Parts(**data)
            self.db.add(obj)
            await self.db.commit()
            await self.db.refresh(obj)
            logger.info(f"Created parts with id: {obj.id}")
            return obj
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating parts: {str(e)}")
            raise

    async def get_by_id(self, obj_id: int) -> Optional[Parts]:
        """Get parts by ID"""
        try:
            query = select(Parts).where(Parts.id == obj_id)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching parts {obj_id}: {str(e)}")
            raise

    async def get_list(
        self, 
        skip: int = 0, 
        limit: int = 20, 
        query_dict: Optional[Dict[str, Any]] = None,
        sort: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get paginated list of partss"""
        try:
            query = select(Parts)
            count_query = select(func.count(Parts.id))
            
            if query_dict:
                for field, value in query_dict.items():
                    if hasattr(Parts, field):
                        query = query.where(getattr(Parts, field) == value)
                        count_query = count_query.where(getattr(Parts, field) == value)
            
            count_result = await self.db.execute(count_query)
            total = count_result.scalar()

            if sort:
                if sort.startswith('-'):
                    field_name = sort[1:]
                    if hasattr(Parts, field_name):
                        query = query.order_by(getattr(Parts, field_name).desc())
                else:
                    if hasattr(Parts, sort):
                        query = query.order_by(getattr(Parts, sort))
            else:
                query = query.order_by(Parts.id.desc())

            result = await self.db.execute(query.offset(skip).limit(limit))
            items = result.scalars().all()

            return {
                "items": items,
                "total": total,
                "skip": skip,
                "limit": limit,
            }
        except Exception as e:
            logger.error(f"Error fetching parts list: {str(e)}")
            raise

    async def update(self, obj_id: int, update_data: Dict[str, Any]) -> Optional[Parts]:
        """Update parts"""
        try:
            obj = await self.get_by_id(obj_id)
            if not obj:
                logger.warning(f"Parts {obj_id} not found for update")
                return None
            for key, value in update_data.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)

            await self.db.commit()
            await self.db.refresh(obj)
            logger.info(f"Updated parts {obj_id}")
            return obj
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating parts {obj_id}: {str(e)}")
            raise

    async def delete(self, obj_id: int) -> bool:
        """Delete parts"""
        try:
            obj = await self.get_by_id(obj_id)
            if not obj:
                logger.warning(f"Parts {obj_id} not found for deletion")
                return False
            await self.db.delete(obj)
            await self.db.commit()
            logger.info(f"Deleted parts {obj_id}")
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting parts {obj_id}: {str(e)}")
            raise

    async def get_by_field(self, field_name: str, field_value: Any) -> Optional[Parts]:
        """Get parts by any field"""
        try:
            if not hasattr(Parts, field_name):
                raise ValueError(f"Field {field_name} does not exist on Parts")
            result = await self.db.execute(
                select(Parts).where(getattr(Parts, field_name) == field_value)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching parts by {field_name}: {str(e)}")
            raise

    async def list_by_field(
        self, field_name: str, field_value: Any, skip: int = 0, limit: int = 20
    ) -> List[Parts]:
        """Get list of partss filtered by field"""
        try:
            if not hasattr(Parts, field_name):
                raise ValueError(f"Field {field_name} does not exist on Parts")
            result = await self.db.execute(
                select(Parts)
                .where(getattr(Parts, field_name) == field_value)
                .offset(skip)
                .limit(limit)
                .order_by(Parts.id.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching partss by {field_name}: {str(e)}")
            raise