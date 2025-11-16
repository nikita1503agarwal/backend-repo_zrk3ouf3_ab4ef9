"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
Each Pydantic model represents a collection in your database.
Class name lowercased is used as the collection name.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal

# Core app schemas for Pizza Store

class Pizza(BaseModel):
    name: str = Field(..., description="Pizza name")
    description: Optional[str] = Field(None, description="Short description")
    image: Optional[str] = Field(None, description="Image URL")
    category: Literal["classic", "gourmet", "vegan", "special"] = "classic"
    base_price: float = Field(..., ge=0, description="Base price for small size")
    sizes: List[str] = Field(default_factory=lambda: ["Small", "Medium", "Large"])  # labels only
    toppings: List[str] = Field(default_factory=list, description="Default toppings")
    is_popular: bool = Field(False, description="Shown as featured on landing")

class OrderItem(BaseModel):
    pizza_id: str
    name: str
    size: str
    unit_price: float = Field(..., ge=0)
    quantity: int = Field(..., ge=1)
    image: Optional[str] = None

class CustomerInfo(BaseModel):
    name: str
    phone: str
    address: str

class Order(BaseModel):
    customer: CustomerInfo
    items: List[OrderItem]
    notes: Optional[str] = None
    subtotal: float = Field(..., ge=0)
    delivery_fee: float = Field(..., ge=0)
    total: float = Field(..., ge=0)
    status: Literal["pending", "preparing", "out_for_delivery", "delivered", "cancelled"] = "pending"
