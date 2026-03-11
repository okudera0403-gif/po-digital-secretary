import logging
from typing import Optional, Dict, Any, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.product_part_rules import Product_part_rules

logger = logging.getLogger(__name__)


# ------------------ Service Layer ------------------
class Product_part_rulesService:
    """Service layer for Product_part_rules operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: Dict[str, Any]) -> Optional[Product_part_rules]:
        """Create a new product_part_rules"""
        try:
            obj = Product_part_rules(**data)
            self.db.add(obj)
            await self.db.commit()
            await self.db.refresh(obj)
            logger.info(f"Created product_part_rules with id: {obj.id}")
            return obj
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating product_part_rules: {str(e)}")
            raise

    async def get_by_id(self, obj_id: int) -> Optional[Product_part_rules]:
        """Get product_part_rules by ID"""
        try:
            query = select(Product_part_rules).where(Product_part_rules.id == obj_id)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching product_part_rules {obj_id}: {str(e)}")
            raise

    async def get_list(
        self, 
        skip: int = 0, 
        limit: int = 20, 
        query_dict: Optional[Dict[str, Any]] = None,
        sort: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get paginated list of product_part_ruless"""
        try:
            query = select(Product_part_rules)
            count_query = select(func.count(Product_part_rules.id))
            
            if query_dict:
                for field, value in query_dict.items():
                    if hasattr(Product_part_rules, field):
                        query = query.where(getattr(Product_part_rules, field) == value)
                        count_query = count_query.where(getattr(Product_part_rules, field) == value)
            
            count_result = await self.db.execute(count_query)
            total = count_result.scalar()

            if sort:
                if sort.startswith('-'):
                    field_name = sort[1:]
                    if hasattr(Product_part_rules, field_name):
                        query = query.order_by(getattr(Product_part_rules, field_name).desc())
                else:
                    if hasattr(Product_part_rules, sort):
                        query = query.order_by(getattr(Product_part_rules, sort))
            else:
                query = query.order_by(Product_part_rules.id.desc())

            result = await self.db.execute(query.offset(skip).limit(limit))
            items = result.scalars().all()

            return {
                "items": items,
                "total": total,
                "skip": skip,
                "limit": limit,
            }
        except Exception as e:
            logger.error(f"Error fetching product_part_rules list: {str(e)}")
            raise

    async def update(self, obj_id: int, update_data: Dict[str, Any]) -> Optional[Product_part_rules]:
        """Update product_part_rules"""
        try:
            obj = await self.get_by_id(obj_id)
            if not obj:
                logger.warning(f"Product_part_rules {obj_id} not found for update")
                return None
            for key, value in update_data.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)

            await self.db.commit()
            await self.db.refresh(obj)
            logger.info(f"Updated product_part_rules {obj_id}")
            return obj
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating product_part_rules {obj_id}: {str(e)}")
            raise

    async def delete(self, obj_id: int) -> bool:
        """Delete product_part_rules"""
        try:
            obj = await self.get_by_id(obj_id)
            if not obj:
                logger.warning(f"Product_part_rules {obj_id} not found for deletion")
                return False
            await self.db.delete(obj)
            await self.db.commit()
            logger.info(f"Deleted product_part_rules {obj_id}")
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting product_part_rules {obj_id}: {str(e)}")
            raise

    async def get_by_field(self, field_name: str, field_value: Any) -> Optional[Product_part_rules]:
        """Get product_part_rules by any field"""
        try:
            if not hasattr(Product_part_rules, field_name):
                raise ValueError(f"Field {field_name} does not exist on Product_part_rules")
            result = await self.db.execute(
                select(Product_part_rules).where(getattr(Product_part_rules, field_name) == field_value)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching product_part_rules by {field_name}: {str(e)}")
            raise

    async def list_by_field(
        self, field_name: str, field_value: Any, skip: int = 0, limit: int = 20
    ) -> List[Product_part_rules]:
        """Get list of product_part_ruless filtered by field"""
        try:
            if not hasattr(Product_part_rules, field_name):
                raise ValueError(f"Field {field_name} does not exist on Product_part_rules")
            result = await self.db.execute(
                select(Product_part_rules)
                .where(getattr(Product_part_rules, field_name) == field_value)
                .offset(skip)
                .limit(limit)
                .order_by(Product_part_rules.id.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching product_part_ruless by {field_name}: {str(e)}")
            raise