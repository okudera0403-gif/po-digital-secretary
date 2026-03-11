import logging
from typing import Optional, Dict, Any, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.finished_parts_master import Finished_parts_master

logger = logging.getLogger(__name__)


# ------------------ Service Layer ------------------
class Finished_parts_masterService:
    """Service layer for Finished_parts_master operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: Dict[str, Any]) -> Optional[Finished_parts_master]:
        """Create a new finished_parts_master"""
        try:
            obj = Finished_parts_master(**data)
            self.db.add(obj)
            await self.db.commit()
            await self.db.refresh(obj)
            logger.info(f"Created finished_parts_master with id: {obj.id}")
            return obj
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating finished_parts_master: {str(e)}")
            raise

    async def get_by_id(self, obj_id: int) -> Optional[Finished_parts_master]:
        """Get finished_parts_master by ID"""
        try:
            query = select(Finished_parts_master).where(Finished_parts_master.id == obj_id)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching finished_parts_master {obj_id}: {str(e)}")
            raise

    async def get_list(
        self, 
        skip: int = 0, 
        limit: int = 20, 
        query_dict: Optional[Dict[str, Any]] = None,
        sort: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get paginated list of finished_parts_masters"""
        try:
            query = select(Finished_parts_master)
            count_query = select(func.count(Finished_parts_master.id))
            
            if query_dict:
                for field, value in query_dict.items():
                    if hasattr(Finished_parts_master, field):
                        query = query.where(getattr(Finished_parts_master, field) == value)
                        count_query = count_query.where(getattr(Finished_parts_master, field) == value)
            
            count_result = await self.db.execute(count_query)
            total = count_result.scalar()

            if sort:
                if sort.startswith('-'):
                    field_name = sort[1:]
                    if hasattr(Finished_parts_master, field_name):
                        query = query.order_by(getattr(Finished_parts_master, field_name).desc())
                else:
                    if hasattr(Finished_parts_master, sort):
                        query = query.order_by(getattr(Finished_parts_master, sort))
            else:
                query = query.order_by(Finished_parts_master.id.desc())

            result = await self.db.execute(query.offset(skip).limit(limit))
            items = result.scalars().all()

            return {
                "items": items,
                "total": total,
                "skip": skip,
                "limit": limit,
            }
        except Exception as e:
            logger.error(f"Error fetching finished_parts_master list: {str(e)}")
            raise

    async def update(self, obj_id: int, update_data: Dict[str, Any]) -> Optional[Finished_parts_master]:
        """Update finished_parts_master"""
        try:
            obj = await self.get_by_id(obj_id)
            if not obj:
                logger.warning(f"Finished_parts_master {obj_id} not found for update")
                return None
            for key, value in update_data.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)

            await self.db.commit()
            await self.db.refresh(obj)
            logger.info(f"Updated finished_parts_master {obj_id}")
            return obj
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating finished_parts_master {obj_id}: {str(e)}")
            raise

    async def delete(self, obj_id: int) -> bool:
        """Delete finished_parts_master"""
        try:
            obj = await self.get_by_id(obj_id)
            if not obj:
                logger.warning(f"Finished_parts_master {obj_id} not found for deletion")
                return False
            await self.db.delete(obj)
            await self.db.commit()
            logger.info(f"Deleted finished_parts_master {obj_id}")
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting finished_parts_master {obj_id}: {str(e)}")
            raise

    async def get_by_field(self, field_name: str, field_value: Any) -> Optional[Finished_parts_master]:
        """Get finished_parts_master by any field"""
        try:
            if not hasattr(Finished_parts_master, field_name):
                raise ValueError(f"Field {field_name} does not exist on Finished_parts_master")
            result = await self.db.execute(
                select(Finished_parts_master).where(getattr(Finished_parts_master, field_name) == field_value)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching finished_parts_master by {field_name}: {str(e)}")
            raise

    async def list_by_field(
        self, field_name: str, field_value: Any, skip: int = 0, limit: int = 20
    ) -> List[Finished_parts_master]:
        """Get list of finished_parts_masters filtered by field"""
        try:
            if not hasattr(Finished_parts_master, field_name):
                raise ValueError(f"Field {field_name} does not exist on Finished_parts_master")
            result = await self.db.execute(
                select(Finished_parts_master)
                .where(getattr(Finished_parts_master, field_name) == field_value)
                .offset(skip)
                .limit(limit)
                .order_by(Finished_parts_master.id.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching finished_parts_masters by {field_name}: {str(e)}")
            raise