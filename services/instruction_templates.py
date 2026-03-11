import logging
from typing import Optional, Dict, Any, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.instruction_templates import Instruction_templates

logger = logging.getLogger(__name__)


# ------------------ Service Layer ------------------
class Instruction_templatesService:
    """Service layer for Instruction_templates operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: Dict[str, Any]) -> Optional[Instruction_templates]:
        """Create a new instruction_templates"""
        try:
            obj = Instruction_templates(**data)
            self.db.add(obj)
            await self.db.commit()
            await self.db.refresh(obj)
            logger.info(f"Created instruction_templates with id: {obj.id}")
            return obj
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating instruction_templates: {str(e)}")
            raise

    async def get_by_id(self, obj_id: int) -> Optional[Instruction_templates]:
        """Get instruction_templates by ID"""
        try:
            query = select(Instruction_templates).where(Instruction_templates.id == obj_id)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching instruction_templates {obj_id}: {str(e)}")
            raise

    async def get_list(
        self, 
        skip: int = 0, 
        limit: int = 20, 
        query_dict: Optional[Dict[str, Any]] = None,
        sort: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get paginated list of instruction_templatess"""
        try:
            query = select(Instruction_templates)
            count_query = select(func.count(Instruction_templates.id))
            
            if query_dict:
                for field, value in query_dict.items():
                    if hasattr(Instruction_templates, field):
                        query = query.where(getattr(Instruction_templates, field) == value)
                        count_query = count_query.where(getattr(Instruction_templates, field) == value)
            
            count_result = await self.db.execute(count_query)
            total = count_result.scalar()

            if sort:
                if sort.startswith('-'):
                    field_name = sort[1:]
                    if hasattr(Instruction_templates, field_name):
                        query = query.order_by(getattr(Instruction_templates, field_name).desc())
                else:
                    if hasattr(Instruction_templates, sort):
                        query = query.order_by(getattr(Instruction_templates, sort))
            else:
                query = query.order_by(Instruction_templates.id.desc())

            result = await self.db.execute(query.offset(skip).limit(limit))
            items = result.scalars().all()

            return {
                "items": items,
                "total": total,
                "skip": skip,
                "limit": limit,
            }
        except Exception as e:
            logger.error(f"Error fetching instruction_templates list: {str(e)}")
            raise

    async def update(self, obj_id: int, update_data: Dict[str, Any]) -> Optional[Instruction_templates]:
        """Update instruction_templates"""
        try:
            obj = await self.get_by_id(obj_id)
            if not obj:
                logger.warning(f"Instruction_templates {obj_id} not found for update")
                return None
            for key, value in update_data.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)

            await self.db.commit()
            await self.db.refresh(obj)
            logger.info(f"Updated instruction_templates {obj_id}")
            return obj
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating instruction_templates {obj_id}: {str(e)}")
            raise

    async def delete(self, obj_id: int) -> bool:
        """Delete instruction_templates"""
        try:
            obj = await self.get_by_id(obj_id)
            if not obj:
                logger.warning(f"Instruction_templates {obj_id} not found for deletion")
                return False
            await self.db.delete(obj)
            await self.db.commit()
            logger.info(f"Deleted instruction_templates {obj_id}")
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting instruction_templates {obj_id}: {str(e)}")
            raise

    async def get_by_field(self, field_name: str, field_value: Any) -> Optional[Instruction_templates]:
        """Get instruction_templates by any field"""
        try:
            if not hasattr(Instruction_templates, field_name):
                raise ValueError(f"Field {field_name} does not exist on Instruction_templates")
            result = await self.db.execute(
                select(Instruction_templates).where(getattr(Instruction_templates, field_name) == field_value)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching instruction_templates by {field_name}: {str(e)}")
            raise

    async def list_by_field(
        self, field_name: str, field_value: Any, skip: int = 0, limit: int = 20
    ) -> List[Instruction_templates]:
        """Get list of instruction_templatess filtered by field"""
        try:
            if not hasattr(Instruction_templates, field_name):
                raise ValueError(f"Field {field_name} does not exist on Instruction_templates")
            result = await self.db.execute(
                select(Instruction_templates)
                .where(getattr(Instruction_templates, field_name) == field_value)
                .offset(skip)
                .limit(limit)
                .order_by(Instruction_templates.id.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching instruction_templatess by {field_name}: {str(e)}")
            raise