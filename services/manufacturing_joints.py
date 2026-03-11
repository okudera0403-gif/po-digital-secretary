import logging
from typing import Optional, Dict, Any, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.manufacturing_joints import Manufacturing_joints

logger = logging.getLogger(__name__)


# ------------------ Service Layer ------------------
class Manufacturing_jointsService:
    """Service layer for Manufacturing_joints operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: Dict[str, Any]) -> Optional[Manufacturing_joints]:
        """Create a new manufacturing_joints"""
        try:
            obj = Manufacturing_joints(**data)
            self.db.add(obj)
            await self.db.commit()
            await self.db.refresh(obj)
            logger.info(f"Created manufacturing_joints with id: {obj.id}")
            return obj
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating manufacturing_joints: {str(e)}")
            raise

    async def get_by_id(self, obj_id: int) -> Optional[Manufacturing_joints]:
        """Get manufacturing_joints by ID"""
        try:
            query = select(Manufacturing_joints).where(Manufacturing_joints.id == obj_id)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching manufacturing_joints {obj_id}: {str(e)}")
            raise

    async def get_list(
        self, 
        skip: int = 0, 
        limit: int = 20, 
        query_dict: Optional[Dict[str, Any]] = None,
        sort: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get paginated list of manufacturing_jointss"""
        try:
            query = select(Manufacturing_joints)
            count_query = select(func.count(Manufacturing_joints.id))
            
            if query_dict:
                for field, value in query_dict.items():
                    if hasattr(Manufacturing_joints, field):
                        query = query.where(getattr(Manufacturing_joints, field) == value)
                        count_query = count_query.where(getattr(Manufacturing_joints, field) == value)
            
            count_result = await self.db.execute(count_query)
            total = count_result.scalar()

            if sort:
                if sort.startswith('-'):
                    field_name = sort[1:]
                    if hasattr(Manufacturing_joints, field_name):
                        query = query.order_by(getattr(Manufacturing_joints, field_name).desc())
                else:
                    if hasattr(Manufacturing_joints, sort):
                        query = query.order_by(getattr(Manufacturing_joints, sort))
            else:
                query = query.order_by(Manufacturing_joints.id.desc())

            result = await self.db.execute(query.offset(skip).limit(limit))
            items = result.scalars().all()

            return {
                "items": items,
                "total": total,
                "skip": skip,
                "limit": limit,
            }
        except Exception as e:
            logger.error(f"Error fetching manufacturing_joints list: {str(e)}")
            raise

    async def update(self, obj_id: int, update_data: Dict[str, Any]) -> Optional[Manufacturing_joints]:
        """Update manufacturing_joints"""
        try:
            obj = await self.get_by_id(obj_id)
            if not obj:
                logger.warning(f"Manufacturing_joints {obj_id} not found for update")
                return None
            for key, value in update_data.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)

            await self.db.commit()
            await self.db.refresh(obj)
            logger.info(f"Updated manufacturing_joints {obj_id}")
            return obj
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating manufacturing_joints {obj_id}: {str(e)}")
            raise

    async def delete(self, obj_id: int) -> bool:
        """Delete manufacturing_joints"""
        try:
            obj = await self.get_by_id(obj_id)
            if not obj:
                logger.warning(f"Manufacturing_joints {obj_id} not found for deletion")
                return False
            await self.db.delete(obj)
            await self.db.commit()
            logger.info(f"Deleted manufacturing_joints {obj_id}")
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting manufacturing_joints {obj_id}: {str(e)}")
            raise

    async def get_by_field(self, field_name: str, field_value: Any) -> Optional[Manufacturing_joints]:
        """Get manufacturing_joints by any field"""
        try:
            if not hasattr(Manufacturing_joints, field_name):
                raise ValueError(f"Field {field_name} does not exist on Manufacturing_joints")
            result = await self.db.execute(
                select(Manufacturing_joints).where(getattr(Manufacturing_joints, field_name) == field_value)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching manufacturing_joints by {field_name}: {str(e)}")
            raise

    async def list_by_field(
        self, field_name: str, field_value: Any, skip: int = 0, limit: int = 20
    ) -> List[Manufacturing_joints]:
        """Get list of manufacturing_jointss filtered by field"""
        try:
            if not hasattr(Manufacturing_joints, field_name):
                raise ValueError(f"Field {field_name} does not exist on Manufacturing_joints")
            result = await self.db.execute(
                select(Manufacturing_joints)
                .where(getattr(Manufacturing_joints, field_name) == field_value)
                .offset(skip)
                .limit(limit)
                .order_by(Manufacturing_joints.id.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching manufacturing_jointss by {field_name}: {str(e)}")
            raise