import logging
from typing import Optional, Dict, Any, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.finished_parts import Finished_parts

logger = logging.getLogger(__name__)


# ------------------ Service Layer ------------------
class Finished_partsService:
    """Service layer for Finished_parts operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: Dict[str, Any]) -> Optional[Finished_parts]:
        """Create a new finished_parts"""
        try:
            obj = Finished_parts(**data)
            self.db.add(obj)
            await self.db.commit()
            await self.db.refresh(obj)
            logger.info(f"Created finished_parts with id: {obj.id}")
            return obj
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating finished_parts: {str(e)}")
            raise

    async def get_by_id(self, obj_id: int) -> Optional[Finished_parts]:
        """Get finished_parts by ID"""
        try:
            query = select(Finished_parts).where(Finished_parts.id == obj_id)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching finished_parts {obj_id}: {str(e)}")
            raise

    async def get_list(
        self, 
        skip: int = 0, 
        limit: int = 20, 
        query_dict: Optional[Dict[str, Any]] = None,
        sort: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get paginated list of finished_partss"""
        try:
            query = select(Finished_parts)
            count_query = select(func.count(Finished_parts.id))
            
            if query_dict:
                for field, value in query_dict.items():
                    if hasattr(Finished_parts, field):
                        query = query.where(getattr(Finished_parts, field) == value)
                        count_query = count_query.where(getattr(Finished_parts, field) == value)
            
            count_result = await self.db.execute(count_query)
            total = count_result.scalar()

            if sort:
                if sort.startswith('-'):
                    field_name = sort[1:]
                    if hasattr(Finished_parts, field_name):
                        query = query.order_by(getattr(Finished_parts, field_name).desc())
                else:
                    if hasattr(Finished_parts, sort):
                        query = query.order_by(getattr(Finished_parts, sort))
            else:
                query = query.order_by(Finished_parts.id.desc())

            result = await self.db.execute(query.offset(skip).limit(limit))
            items = result.scalars().all()

            return {
                "items": items,
                "total": total,
                "skip": skip,
                "limit": limit,
            }
        except Exception as e:
            logger.error(f"Error fetching finished_parts list: {str(e)}")
            raise

    async def update(self, obj_id: int, update_data: Dict[str, Any]) -> Optional[Finished_parts]:
        """Update finished_parts"""
        try:
            obj = await self.get_by_id(obj_id)
            if not obj:
                logger.warning(f"Finished_parts {obj_id} not found for update")
                return None
            for key, value in update_data.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)

            await self.db.commit()
            await self.db.refresh(obj)
            logger.info(f"Updated finished_parts {obj_id}")
            return obj
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating finished_parts {obj_id}: {str(e)}")
            raise

    async def delete(self, obj_id: int) -> bool:
        """Delete finished_parts"""
        try:
            obj = await self.get_by_id(obj_id)
            if not obj:
                logger.warning(f"Finished_parts {obj_id} not found for deletion")
                return False
            await self.db.delete(obj)
            await self.db.commit()
            logger.info(f"Deleted finished_parts {obj_id}")
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting finished_parts {obj_id}: {str(e)}")
            raise

    async def get_by_field(self, field_name: str, field_value: Any) -> Optional[Finished_parts]:
        """Get finished_parts by any field"""
        try:
            if not hasattr(Finished_parts, field_name):
                raise ValueError(f"Field {field_name} does not exist on Finished_parts")
            result = await self.db.execute(
                select(Finished_parts).where(getattr(Finished_parts, field_name) == field_value)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching finished_parts by {field_name}: {str(e)}")
            raise

    async def list_by_field(
        self, field_name: str, field_value: Any, skip: int = 0, limit: int = 20
    ) -> List[Finished_parts]:
        """Get list of finished_partss filtered by field"""
        try:
            if not hasattr(Finished_parts, field_name):
                raise ValueError(f"Field {field_name} does not exist on Finished_parts")
            result = await self.db.execute(
                select(Finished_parts)
                .where(getattr(Finished_parts, field_name) == field_value)
                .offset(skip)
                .limit(limit)
                .order_by(Finished_parts.id.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching finished_partss by {field_name}: {str(e)}")
            raise