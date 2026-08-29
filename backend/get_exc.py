import sys
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models import ExceptionRecord

def main():
    db = SessionLocal()
    exc = db.query(ExceptionRecord).filter(ExceptionRecord.id == "8ea2a991-8931-4633-93fc-a713feae3441").first()
    if exc:
        print("ID:", exc.id)
        print("Type:", exc.exception_type)
        print("Decision:", exc.decision)
        print("Variance details:", exc.variance_details)
        print("Order:", exc.order_id)
        print("Payment:", exc.payment_id)
        print("Settlement:", exc.settlement_id)
        print("Bank:", exc.bank_transaction_id)
    else:
        print("Not found")

if __name__ == "__main__":
    main()
