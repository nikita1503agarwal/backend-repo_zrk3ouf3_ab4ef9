import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Pizza, Order

app = FastAPI(title="Pizza Delivery API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helpers

def to_serializable(doc):
    if doc is None:
        return None
    d = dict(doc)
    if "_id" in d:
        d["id"] = str(d.pop("_id"))
    return d

# Seed some pizzas if collection empty
@app.on_event("startup")
async def seed_data():
    if db is None:
        return
    if db["pizza"].count_documents({}) == 0:
        sample_pizzas = [
            {
                "name": "Margherita",
                "description": "Fresh mozzarella, basil, San Marzano tomatoes.",
                "image": "https://images.unsplash.com/photo-1548365328-9f547fb095de?w=800&q=80",
                "category": "classic",
                "base_price": 8.99,
                "sizes": ["Small", "Medium", "Large"],
                "toppings": ["Mozzarella", "Basil", "Tomato"],
                "is_popular": True,
            },
            {
                "name": "Pepperoni",
                "description": "Crispy pepperoni, premium mozzarella.",
                "image": "https://images.unsplash.com/photo-1542281286-9e0a16bb7366?w=800&q=80",
                "category": "classic",
                "base_price": 9.99,
                "sizes": ["Small", "Medium", "Large"],
                "toppings": ["Pepperoni", "Mozzarella"],
                "is_popular": True,
            },
            {
                "name": "Veggie Garden",
                "description": "Mushrooms, peppers, olives, onions.",
                "image": "https://images.unsplash.com/photo-1600028068383-ea11a7a101f9?w=800&q=80",
                "category": "vegan",
                "base_price": 10.49,
                "sizes": ["Small", "Medium", "Large"],
                "toppings": ["Mushroom", "Bell Pepper", "Olives", "Onion"],
                "is_popular": False,
            },
        ]
        for p in sample_pizzas:
            create_document("pizza", p)

@app.get("/")
def read_root():
    return {"message": "Pizza Delivery Backend running"}

# Menu endpoints
@app.get("/api/pizzas")
def list_pizzas(category: Optional[str] = None):
    filter_q = {"category": category} if category else {}
    docs = get_documents("pizza", filter_q)
    return [to_serializable(d) for d in docs]

@app.get("/api/pizzas/{pizza_id}")
def get_pizza(pizza_id: str):
    try:
        doc = db["pizza"].find_one({"_id": ObjectId(pizza_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Pizza not found")
        return to_serializable(doc)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID")

# Orders
@app.post("/api/orders")
def create_order(order: Order):
    order_data = order.model_dump()
    order_id = create_document("order", order_data)
    return {"id": order_id, "status": "received"}

@app.get("/api/featured")
def featured_pizzas():
    docs = get_documents("pizza", {"is_popular": True})
    return [to_serializable(d) for d in docs]

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        from database import db as _db
        if _db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = _db.name if hasattr(_db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = _db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
