"""
Supply orders router - Task 7: Supply Order Management
APIs: GET /api/supply-orders, POST /api/supply-orders, PUT /api/supply-orders/:id/status
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query, Request
from typing import Optional
from datetime import datetime
import structlog

from app.models.base import APIResponse, PaginatedResponse
from app.utils.security import verify_token, check_permissions
from app.config.database import get_collection

logger = structlog.get_logger()
router = APIRouter()

@router.get("", response_model=PaginatedResponse)
async def get_supply_orders(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    vendorId: Optional[str] = Query(None),
    dateRange: Optional[str] = Query(None),
    current_user: dict = Depends(verify_token)
):
    """Get supply orders with pagination and filters"""
    try:
        if not check_permissions(current_user["role"], "supply_orders"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        query = {}
        if search:
            query["$or"] = [
                {"orderNumber": {"$regex": search, "$options": "i"}},
                {"vendorName": {"$regex": search, "$options": "i"}}
            ]
        if status:
            query["status"] = status
        if vendorId:
            query["vendorId"] = vendorId
        
        orders_collection = get_collection("supply_orders")
        skip = (page - 1) * limit
        
        total = await orders_collection.count_documents(query)
        cursor = orders_collection.find(query).sort("orderDate", -1).skip(skip).limit(limit)
        orders = await cursor.to_list(length=limit)
        
        order_list = []
        for order in orders:
            order_dict = dict(order)
            order_dict["id"] = str(order["_id"])
            order_list.append(order_dict)
        
        pages = (total + limit - 1) // limit
        
        return PaginatedResponse(
            data=order_list,
            pagination={
                "page": page, "limit": limit, "total": total, "pages": pages,
                "hasNext": page < pages, "hasPrev": page > 1
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get supply orders", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve supply orders")

@router.post("", response_model=APIResponse)
async def create_supply_order(
    order_data: dict,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    """Create a new supply order"""
    try:
        if not check_permissions(current_user["role"], "supply_orders"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        # Implementation for creating supply order
        return APIResponse(success=True, data={"message": "Supply order creation not implemented yet"})
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create supply order", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create supply order")

@router.put("/{order_id}/status", response_model=APIResponse)
async def update_order_status(
    order_id: str,
    status_data: dict,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    """Update supply order status"""
    try:
        if not check_permissions(current_user["role"], "supply_orders"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        # Implementation for updating order status
        return APIResponse(success=True, data={"message": "Order status update not implemented yet"})
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update order status", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update order status")
