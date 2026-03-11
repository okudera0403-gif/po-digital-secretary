import logging
from typing import Optional, Dict, Any, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.cases import Cases

logger = logging.getLogger(__name__)


# ------------------ Service Layer ------------------
class CasesService:
    """Service layer for Cases operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: Dict[str, Any], user_id: Optional[str] = None) -> Optional[Cases]:
        """Create a new cases"""
        try:
            if user_id:
                data['user_id'] = user_id
            obj = Cases(**data)
            self.db.add(obj)
            await self.db.commit()
            await self.db.refresh(obj)
            logger.info(f"Created cases with id: {obj.id}")
            return obj
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating cases: {str(e)}")
            raise

    async def check_ownership(self, obj_id: int, user_id: str) -> bool:
        """Check if user owns this record"""
        try:
            obj = await self.get_by_id(obj_id, user_id=user_id)
            return obj is not None
        except Exception as e:
            logger.error(f"Error checking ownership for cases {obj_id}: {str(e)}")
            return False

    async def get_by_id(self, obj_id: int, user_id: Optional[str] = None) -> Optional[Cases]:
        """Get cases by ID (user can only see their own records)"""
        try:
            query = select(Cases).where(Cases.id == obj_id)
            if user_id:
                query = query.where(Cases.user_id == user_id)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching cases {obj_id}: {str(e)}")
            raise

    async def get_list(
        self, 
        skip: int = 0, 
        limit: int = 20, 
        user_id: Optional[str] = None,
        query_dict: Optional[Dict[str, Any]] = None,
        sort: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get paginated list of casess (user can only see their own records)"""
        try:
            query = select(Cases)
            count_query = select(func.count(Cases.id))
            
            if user_id:
                query = query.where(Cases.user_id == user_id)
                count_query = count_query.where(Cases.user_id == user_id)
            
            if query_dict:
                for field, value in query_dict.items():
                    if hasattr(Cases, field):
                        query = query.where(getattr(Cases, field) == value)
                        count_query = count_query.where(getattr(Cases, field) == value)
            
            count_result = await self.db.execute(count_query)
            total = count_result.scalar()

            if sort:
                if sort.startswith('-'):
                    field_name = sort[1:]
                    if hasattr(Cases, field_name):
                        query = query.order_by(getattr(Cases, field_name).desc())
                else:
                    if hasattr(Cases, sort):
                        query = query.order_by(getattr(Cases, sort))
            else:
                query = query.order_by(Cases.id.desc())

            result = await self.db.execute(query.offset(skip).limit(limit))
            items = result.scalars().all()

            return {
                "items": items,
                "total": total,
                "skip": skip,
                "limit": limit,
            }
        except Exception as e:
            logger.error(f"Error fetching cases list: {str(e)}")
            raise

    async def update(self, obj_id: int, update_data: Dict[str, Any], user_id: Optional[str] = None) -> Optional[Cases]:
        """Update cases (requires ownership)"""
        try:
            obj = await self.get_by_id(obj_id, user_id=user_id)
            if not obj:
                logger.warning(f"Cases {obj_id} not found for update")
                return None
            for key, value in update_data.items():
                if hasattr(obj, key) and key != 'user_id':
                    setattr(obj, key, value)

            await self.db.commit()
            await self.db.refresh(obj)
            logger.info(f"Updated cases {obj_id}")
            return obj
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating cases {obj_id}: {str(e)}")
            raise

    async def delete(self, obj_id: int, user_id: Optional[str] = None) -> bool:
        """Delete cases (requires ownership)"""
        try:
            obj = await self.get_by_id(obj_id, user_id=user_id)
            if not obj:
                logger.warning(f"Cases {obj_id} not found for deletion")
                return False
            await self.db.delete(obj)
            await self.db.commit()
            logger.info(f"Deleted cases {obj_id}")
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting cases {obj_id}: {str(e)}")
            raise

    async def get_by_field(self, field_name: str, field_value: Any) -> Optional[Cases]:
        """Get cases by any field"""
        try:
            if not hasattr(Cases, field_name):
                raise ValueError(f"Field {field_name} does not exist on Cases")
            result = await self.db.execute(
                select(Cases).where(getattr(Cases, field_name) == field_value)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching cases by {field_name}: {str(e)}")
            raise

    async def list_by_field(
        self, field_name: str, field_value: Any, skip: int = 0, limit: int = 20
    ) -> List[Cases]:
        """Get list of casess filtered by field"""
        try:
            if not hasattr(Cases, field_name):
                raise ValueError(f"Field {field_name} does not exist on Cases")
            result = await self.db.execute(
                select(Cases)
                .where(getattr(Cases, field_name) == field_value)
                .offset(skip)
                .limit(limit)
                .order_by(Cases.id.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching casess by {field_name}: {str(e)}")
            raise