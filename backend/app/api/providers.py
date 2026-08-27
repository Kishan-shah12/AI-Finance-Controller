from fastapi import APIRouter
from app.providers.razorpay_provider import RazorpayProvider

router = APIRouter(prefix="/api/v1/providers/razorpay", tags=["providers"])

@router.get("/status")
def get_razorpay_status():
    provider = RazorpayProvider()
    return provider.get_status()

@router.post("/test-connection")
def test_razorpay_connection():
    provider = RazorpayProvider()
    status = provider.get_status()
    if not status["configured"]:
        return {"success": False, "message": "Server credentials not configured."}
        
    reachable = provider.test_connection()
    return {
        "success": reachable,
        "message": "Connection successful" if reachable else "Unable to reach Razorpay APIs."
    }
