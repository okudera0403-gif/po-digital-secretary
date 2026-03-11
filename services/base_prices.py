import logging
from typing import Optional, Dict, Any, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.base_prices import Base_prices

logger = logging.getLogger(__name__)


# ------------------ Service Layer ------------------
class Base_pricesService:
    """Service layer for Base_prices operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: Dict[str, Any]) -> Optional[Base_prices]:
        """Create a new base_prices"""
        try:
            obj = Base_prices(**data)
            self.db.add(obj)
            await self.db.commit()
            await self.db.refresh(obj)
            logger.info(f"Created base_prices with id: {obj.id}")
            return obj
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating base_prices: {str(e)}")
            raise

    async def get_by_id(self, obj_id: int) -> Optional[Base_prices]:
        """Get base_prices by ID"""
        try:
            query = select(Base_prices).where(Base_prices.id == obj_id)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching base_prices {obj_id}: {str(e)}")
            raise

    async def get_list(
        self, 
        skip: int = 0, 
        limit: int = 20, 
        query_dict: Optional[Dict[str, Any]] = None,
        sort: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get paginated list of base_pricess"""
        try:
            query = select(Base_prices)
            count_query = select(func.count(Base_prices.id))
            
            if query_dict:
                for field, value in query_dict.items():
                    if hasattr(Base_prices, field):
                        query = query.where(getattr(Base_prices, field) == value)
                        count_query = count_query.where(getattr(Base_prices, field) == value)
            
            count_result = await self.db.execute(count_query)
            total = count_result.scalar()

            if sort:
                if sort.startswith('-'):
                    field_name = sort[1:]
                    if hasattr(Base_prices, field_name):
                        query = query.order_by(getattr(Base_prices, field_name).desc())
                else:
                    if hasattr(Base_prices, sort):
                        query = query.order_by(getattr(Base_prices, sort))
            else:
                query = query.order_by(Base_prices.id.desc())

            result = await self.db.execute(query.offset(skip).limit(limit))
            items = result.scalars().all()

            return {
                "items": items,
                "total": total,
                "skip": skip,
                "limit": limit,
            }
        except Exception as e:
            logger.error(f"Error fetching base_prices list: {str(e)}")
            raise

    async def update(self, obj_id: int, update_data: Dict[str, Any]) -> Optional[Base_prices]:
        """Update base_prices"""
        try:
            obj = await self.get_by_id(obj_id)
            if not obj:
                logger.warning(f"Base_prices {obj_id} not found for update")
                return None
            for key, value in update_data.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)

            await self.db.commit()
            await self.db.refresh(obj)
            logger.info(f"Updated base_prices {obj_id}")
            return obj
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating base_prices {obj_id}: {str(e)}")
            raise

    async def delete(self, obj_id: int) -> bool:
        """Delete base_prices"""
        try:
            obj = await self.get_by_id(obj_id)
            if not obj:
                logger.warning(f"Base_prices {obj_id} not found for deletion")
                return False
            await self.db.delete(obj)
            await self.db.commit()
            logger.info(f"Deleted base_prices {obj_id}")
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting base_prices {obj_id}: {str(e)}")
            raise

    async def get_by_field(self, field_name: str, field_value: Any) -> Optional[Base_prices]:
        """Get base_prices by any field"""
        try:
            if not hasattr(Base_prices, field_name):
                raise ValueError(f"Field {field_name} does not exist on Base_prices")
            result = await self.db.execute(
                select(Base_prices).where(getattr(Base_prices, field_name) == field_value)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching base_prices by {field_name}: {str(e)}")
            raise

    async def list_by_field(
        self, field_name: str, field_value: Any, skip: int = 0, limit: int = 20
    ) -> List[Base_prices]:
        """Get list of base_pricess filtered by field"""
        try:
            if not hasattr(Base_prices, field_name):
                raise ValueError(f"Field {field_name} does not exist on Base_prices")
            result = await self.db.execute(
                select(Base_prices)
                .where(getattr(Base_prices, field_name) == field_value)
                .offset(skip)
                .limit(limit)
                .order_by(Base_prices.id.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching base_pricess by {field_name}: {str(e)}")
            raise