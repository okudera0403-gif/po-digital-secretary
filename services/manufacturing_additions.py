import logging
from typing import Optional, Dict, Any, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.manufacturing_additions import Manufacturing_additions

logger = logging.getLogger(__name__)


# ------------------ Service Layer ------------------
class Manufacturing_additionsService:
    """Service layer for Manufacturing_additions operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: Dict[str, Any]) -> Optional[Manufacturing_additions]:
        """Create a new manufacturing_additions"""
        try:
            obj = Manufacturing_additions(**data)
            self.db.add(obj)
            await self.db.commit()
            await self.db.refresh(obj)
            logger.info(f"Created manufacturing_additions with id: {obj.id}")
            return obj
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating manufacturing_additions: {str(e)}")
            raise

    async def get_by_id(self, obj_id: int) -> Optional[Manufacturing_additions]:
        """Get manufacturing_additions by ID"""
        try:
            query = select(Manufacturing_additions).where(Manufacturing_additions.id == obj_id)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching manufacturing_additions {obj_id}: {str(e)}")
            raise

    async def get_list(
        self, 
        skip: int = 0, 
        limit: int = 20, 
        query_dict: Optional[Dict[str, Any]] = None,
        sort: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get paginated list of manufacturing_additionss"""
        try:
            query = select(Manufacturing_additions)
            count_query = select(func.count(Manufacturing_additions.id))
            
            if query_dict:
                for field, value in query_dict.items():
                    if hasattr(Manufacturing_additions, field):
                        query = query.where(getattr(Manufacturing_additions, field) == value)
                        count_query = count_query.where(getattr(Manufacturing_additions, field) == value)
            
            count_result = await self.db.execute(count_query)
            total = count_result.scalar()

            if sort:
                if sort.startswith('-'):
                    field_name = sort[1:]
                    if hasattr(Manufacturing_additions, field_name):
                        query = query.order_by(getattr(Manufacturing_additions, field_name).desc())
                else:
                    if hasattr(Manufacturing_additions, sort):
                        query = query.order_by(getattr(Manufacturing_additions, sort))
            else:
                query = query.order_by(Manufacturing_additions.id.desc())

            result = await self.db.execute(query.offset(skip).limit(limit))
            items = result.scalars().all()

            return {
                "items": items,
                "total": total,
                "skip": skip,
                "limit": limit,
            }
        except Exception as e:
            logger.error(f"Error fetching manufacturing_additions list: {str(e)}")
            raise

    async def update(self, obj_id: int, update_data: Dict[str, Any]) -> Optional[Manufacturing_additions]:
        """Update manufacturing_additions"""
        try:
            obj = await self.get_by_id(obj_id)
            if not obj:
                logger.warning(f"Manufacturing_additions {obj_id} not found for update")
                return None
            for key, value in update_data.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)

            await self.db.commit()
            await self.db.refresh(obj)
            logger.info(f"Updated manufacturing_additions {obj_id}")
            return obj
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating manufacturing_additions {obj_id}: {str(e)}")
            raise

    async def delete(self, obj_id: int) -> bool:
        """Delete manufacturing_additions"""
        try:
            obj = await self.get_by_id(obj_id)
            if not obj:
                logger.warning(f"Manufacturing_additions {obj_id} not found for deletion")
                return False
            await self.db.delete(obj)
            await self.db.commit()
            logger.info(f"Deleted manufacturing_additions {obj_id}")
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting manufacturing_additions {obj_id}: {str(e)}")
            raise

    async def get_by_field(self, field_name: str, field_value: Any) -> Optional[Manufacturing_additions]:
        """Get manufacturing_additions by any field"""
        try:
            if not hasattr(Manufacturing_additions, field_name):
                raise ValueError(f"Field {field_name} does not exist on Manufacturing_additions")
            result = await self.db.execute(
                select(Manufacturing_additions).where(getattr(Manufacturing_additions, field_name) == field_value)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching manufacturing_additions by {field_name}: {str(e)}")
            raise

    async def list_by_field(
        self, field_name: str, field_value: Any, skip: int = 0, limit: int = 20
    ) -> List[Manufacturing_additions]:
        """Get list of manufacturing_additionss filtered by field"""
        try:
            if not hasattr(Manufacturing_additions, field_name):
                raise ValueError(f"Field {field_name} does not exist on Manufacturing_additions")
            result = await self.db.execute(
                select(Manufacturing_additions)
                .where(getattr(Manufacturing_additions, field_name) == field_value)
                .offset(skip)
                .limit(limit)
                .order_by(Manufacturing_additions.id.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching manufacturing_additionss by {field_name}: {str(e)}")
            raise