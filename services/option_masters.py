import logging
from typing import Optional, Dict, Any, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.option_masters import Option_masters

logger = logging.getLogger(__name__)


# ------------------ Service Layer ------------------
class Option_mastersService:
    """Service layer for Option_masters operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: Dict[str, Any]) -> Optional[Option_masters]:
        """Create a new option_masters"""
        try:
            obj = Option_masters(**data)
            self.db.add(obj)
            await self.db.commit()
            await self.db.refresh(obj)
            logger.info(f"Created option_masters with id: {obj.id}")
            return obj
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating option_masters: {str(e)}")
            raise

    async def get_by_id(self, obj_id: int) -> Optional[Option_masters]:
        """Get option_masters by ID"""
        try:
            query = select(Option_masters).where(Option_masters.id == obj_id)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching option_masters {obj_id}: {str(e)}")
            raise

    async def get_list(
        self, 
        skip: int = 0, 
        limit: int = 20, 
        query_dict: Optional[Dict[str, Any]] = None,
        sort: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get paginated list of option_masterss"""
        try:
            query = select(Option_masters)
            count_query = select(func.count(Option_masters.id))
            
            if query_dict:
                for field, value in query_dict.items():
                    if hasattr(Option_masters, field):
                        query = query.where(getattr(Option_masters, field) == value)
                        count_query = count_query.where(getattr(Option_masters, field) == value)
            
            count_result = await self.db.execute(count_query)
            total = count_result.scalar()

            if sort:
                if sort.startswith('-'):
                    field_name = sort[1:]
                    if hasattr(Option_masters, field_name):
                        query = query.order_by(getattr(Option_masters, field_name).desc())
                else:
                    if hasattr(Option_masters, sort):
                        query = query.order_by(getattr(Option_masters, sort))
            else:
                query = query.order_by(Option_masters.id.desc())

            result = await self.db.execute(query.offset(skip).limit(limit))
            items = result.scalars().all()

            return {
                "items": items,
                "total": total,
                "skip": skip,
                "limit": limit,
            }
        except Exception as e:
            logger.error(f"Error fetching option_masters list: {str(e)}")
            raise

    async def update(self, obj_id: int, update_data: Dict[str, Any]) -> Optional[Option_masters]:
        """Update option_masters"""
        try:
            obj = await self.get_by_id(obj_id)
            if not obj:
                logger.warning(f"Option_masters {obj_id} not found for update")
                return None
            for key, value in update_data.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)

            await self.db.commit()
            await self.db.refresh(obj)
            logger.info(f"Updated option_masters {obj_id}")
            return obj
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating option_masters {obj_id}: {str(e)}")
            raise

    async def delete(self, obj_id: int) -> bool:
        """Delete option_masters"""
        try:
            obj = await self.get_by_id(obj_id)
            if not obj:
                logger.warning(f"Option_masters {obj_id} not found for deletion")
                return False
            await self.db.delete(obj)
            await self.db.commit()
            logger.info(f"Deleted option_masters {obj_id}")
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting option_masters {obj_id}: {str(e)}")
            raise

    async def get_by_field(self, field_name: str, field_value: Any) -> Optional[Option_masters]:
        """Get option_masters by any field"""
        try:
            if not hasattr(Option_masters, field_name):
                raise ValueError(f"Field {field_name} does not exist on Option_masters")
            result = await self.db.execute(
                select(Option_masters).where(getattr(Option_masters, field_name) == field_value)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching option_masters by {field_name}: {str(e)}")
            raise

    async def list_by_field(
        self, field_name: str, field_value: Any, skip: int = 0, limit: int = 20
    ) -> List[Option_masters]:
        """Get list of option_masterss filtered by field"""
        try:
            if not hasattr(Option_masters, field_name):
                raise ValueError(f"Field {field_name} does not exist on Option_masters")
            result = await self.db.execute(
                select(Option_masters)
                .where(getattr(Option_masters, field_name) == field_value)
                .offset(skip)
                .limit(limit)
                .order_by(Option_masters.id.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching option_masterss by {field_name}: {str(e)}")
            raise