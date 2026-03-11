import logging
from typing import Optional, Dict, Any, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.case_opinions import Case_opinions

logger = logging.getLogger(__name__)


# ------------------ Service Layer ------------------
class Case_opinionsService:
    """Service layer for Case_opinions operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: Dict[str, Any], user_id: Optional[str] = None) -> Optional[Case_opinions]:
        """Create a new case_opinions"""
        try:
            if user_id:
                data['user_id'] = user_id
            obj = Case_opinions(**data)
            self.db.add(obj)
            await self.db.commit()
            await self.db.refresh(obj)
            logger.info(f"Created case_opinions with id: {obj.id}")
            return obj
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating case_opinions: {str(e)}")
            raise

    async def check_ownership(self, obj_id: int, user_id: str) -> bool:
        """Check if user owns this record"""
        try:
            obj = await self.get_by_id(obj_id, user_id=user_id)
            return obj is not None
        except Exception as e:
            logger.error(f"Error checking ownership for case_opinions {obj_id}: {str(e)}")
            return False

    async def get_by_id(self, obj_id: int, user_id: Optional[str] = None) -> Optional[Case_opinions]:
        """Get case_opinions by ID (user can only see their own records)"""
        try:
            query = select(Case_opinions).where(Case_opinions.id == obj_id)
            if user_id:
                query = query.where(Case_opinions.user_id == user_id)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching case_opinions {obj_id}: {str(e)}")
            raise

    async def get_list(
        self, 
        skip: int = 0, 
        limit: int = 20, 
        user_id: Optional[str] = None,
        query_dict: Optional[Dict[str, Any]] = None,
        sort: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get paginated list of case_opinionss (user can only see their own records)"""
        try:
            query = select(Case_opinions)
            count_query = select(func.count(Case_opinions.id))
            
            if user_id:
                query = query.where(Case_opinions.user_id == user_id)
                count_query = count_query.where(Case_opinions.user_id == user_id)
            
            if query_dict:
                for field, value in query_dict.items():
                    if hasattr(Case_opinions, field):
                        query = query.where(getattr(Case_opinions, field) == value)
                        count_query = count_query.where(getattr(Case_opinions, field) == value)
            
            count_result = await self.db.execute(count_query)
            total = count_result.scalar()

            if sort:
                if sort.startswith('-'):
                    field_name = sort[1:]
                    if hasattr(Case_opinions, field_name):
                        query = query.order_by(getattr(Case_opinions, field_name).desc())
                else:
                    if hasattr(Case_opinions, sort):
                        query = query.order_by(getattr(Case_opinions, sort))
            else:
                query = query.order_by(Case_opinions.id.desc())

            result = await self.db.execute(query.offset(skip).limit(limit))
            items = result.scalars().all()

            return {
                "items": items,
                "total": total,
                "skip": skip,
                "limit": limit,
            }
        except Exception as e:
            logger.error(f"Error fetching case_opinions list: {str(e)}")
            raise

    async def update(self, obj_id: int, update_data: Dict[str, Any], user_id: Optional[str] = None) -> Optional[Case_opinions]:
        """Update case_opinions (requires ownership)"""
        try:
            obj = await self.get_by_id(obj_id, user_id=user_id)
            if not obj:
                logger.warning(f"Case_opinions {obj_id} not found for update")
                return None
            for key, value in update_data.items():
                if hasattr(obj, key) and key != 'user_id':
                    setattr(obj, key, value)

            await self.db.commit()
            await self.db.refresh(obj)
            logger.info(f"Updated case_opinions {obj_id}")
            return obj
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating case_opinions {obj_id}: {str(e)}")
            raise

    async def delete(self, obj_id: int, user_id: Optional[str] = None) -> bool:
        """Delete case_opinions (requires ownership)"""
        try:
            obj = await self.get_by_id(obj_id, user_id=user_id)
            if not obj:
                logger.warning(f"Case_opinions {obj_id} not found for deletion")
                return False
            await self.db.delete(obj)
            await self.db.commit()
            logger.info(f"Deleted case_opinions {obj_id}")
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting case_opinions {obj_id}: {str(e)}")
            raise

    async def get_by_field(self, field_name: str, field_value: Any) -> Optional[Case_opinions]:
        """Get case_opinions by any field"""
        try:
            if not hasattr(Case_opinions, field_name):
                raise ValueError(f"Field {field_name} does not exist on Case_opinions")
            result = await self.db.execute(
                select(Case_opinions).where(getattr(Case_opinions, field_name) == field_value)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching case_opinions by {field_name}: {str(e)}")
            raise

    async def list_by_field(
        self, field_name: str, field_value: Any, skip: int = 0, limit: int = 20
    ) -> List[Case_opinions]:
        """Get list of case_opinionss filtered by field"""
        try:
            if not hasattr(Case_opinions, field_name):
                raise ValueError(f"Field {field_name} does not exist on Case_opinions")
            result = await self.db.execute(
                select(Case_opinions)
                .where(getattr(Case_opinions, field_name) == field_value)
                .offset(skip)
                .limit(limit)
                .order_by(Case_opinions.id.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching case_opinionss by {field_name}: {str(e)}")
            raise