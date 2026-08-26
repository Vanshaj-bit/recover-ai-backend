from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 1. Initialize FastAPI FIRST
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://recover-ai-frontend-r6310moh1-vanshaj2.vercel.app/"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Import ALL routers AFTER app is created
from app.api.v1 import auth, customers, payments

# 3. Register routers BELOW app definition
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(customers.router, prefix="/api/v1/customers", tags=["Customers"])
app.include_router(payments.router, prefix="/api/v1/payments", tags=["Payments"])

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "RecoverAI API"
    }