from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://localhost:4300"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/login")
def login(data: LoginRequest):
    if not data.username or not data.password:
        raise HTTPException(status_code=400, detail="Username and password required")

    username = data.username.strip()
    password = data.password.strip()

    if username == "admin@crm.com" and password == "admin123":
        return {
            "status": "success",
            "message": "Login successful",
            "token": "fake-jwt-token-123"
        }
    raise HTTPException(status_code=401, detail="Invalid credentials")

# --- CUSTOMER MANAGEMENT ---

customers_db = {}
customer_id_counter = 1

class CustomerBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class CustomerResponse(CustomerBase):
    id: int

@app.get("/customers", response_model=List[CustomerResponse])
def get_customers():
    return list(customers_db.values())

@app.get("/customers/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: int):
    if customer_id not in customers_db:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customers_db[customer_id]

@app.post("/customers", response_model=CustomerResponse)
def create_customer(data: CustomerCreate):
    global customer_id_counter
    # Check duplicate email
    for c in customers_db.values():
        if c["email"] == data.email:
            raise HTTPException(status_code=400, detail="Email already exists")
    
    new_customer = data.dict()
    new_customer["id"] = customer_id_counter
    customers_db[customer_id_counter] = new_customer
    customer_id_counter += 1
    return new_customer

@app.put("/customers/{customer_id}", response_model=CustomerResponse)
def update_customer(customer_id: int, data: CustomerUpdate):
    if customer_id not in customers_db:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Check duplicate email
    if data.email:
        for cid, c in customers_db.items():
            if c["email"] == data.email and cid != customer_id:
                raise HTTPException(status_code=400, detail="Email already exists")
    
    stored_customer = customers_db[customer_id]
    update_data = data.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        stored_customer[key] = value
        
    customers_db[customer_id] = stored_customer
    return stored_customer

@app.delete("/customers/{customer_id}")
def delete_customer(customer_id: int):
    if customer_id not in customers_db:
        raise HTTPException(status_code=404, detail="Customer not found")
    del customers_db[customer_id]
    return {"message": "Customer deleted successfully"}