from sqlmodel import Session, select
from app.models.payment_model import Payment, PaymentCreate, PaymentUpdate
from fastapi import HTTPException
import stripe

stripe.api_key = "sk_test_51Pgis3RoRfMmPaxp3mtohBmnPfe3TdB1ohkZToTOVYdACkxIB4BSaiG00HtbUQb0APCN2dhkKceUF2chYKFohPTA000cibX9gH"

def create_payment(session: Session, payment_data: PaymentCreate, user_id: int):
    if payment_data.method == "stripe":
        # return  {"working":"good"}
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Order {}'.format(payment_data.order_id),
                    },
                    'unit_amount': int(payment_data.amount * 100),  # amount in cents
                },
                'quantity': 1,
            }],
            mode='payment',
           success_url="http://localhost:8001/stripe-callback/payment-success/?session_id={CHECKOUT_SESSION_ID}",
           cancel_url="http://localhost:8001/stripe-callback/payment-fail/?session_id={CHECKOUT_SESSION_ID}",
            metadata={'order_id': payment_data.order_id, 'user_id': user_id}
        )
        # return checkout_session.url
        
        payment = Payment(
            order_id=payment_data.order_id,
            user_id=user_id,
            amount=payment_data.amount,
            currency="usd",
            status="pending",
            method="stripe",
            stripe_payment_intent_id=checkout_session['id']
        )
    else:
        payment = Payment(
            order_id=payment_data.order_id,
            user_id=user_id,
            amount=payment_data.amount,
            currency="usd",
            status="pending",
            method="cash_on_delivery"
        )
    
    session.add(payment)
    session.commit()
    session.refresh(payment)
    
    if payment_data.method == "stripe":
        return payment, checkout_session.url
    
    return payment, None


def get_payment(session: Session, payment_id: int, user_id: int) -> Payment:
    payment = session.exec(select(Payment).where(Payment.id == payment_id, Payment.user_id == user_id)).one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

def update_payment_status(session: Session, payment_id: int, status: str):
    payment = session.get(Payment, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    payment.status = status
    session.add(payment)
    session.commit()
    session.refresh(payment)
    return payment



def update_payment_status(session: Session, order_id: int, status: str):
    payment = session.exec(select(Payment).where(Payment.order_id == order_id)).one_or_none()
    if payment:
        payment.status = status
        session.add(payment)
        session.commit()
        session.refresh(payment)
    else:
        raise HTTPException(status_code=404, detail=f"Payment not found for order_id: {order_id}")
    return payment

def get_payment_intent_status(session_id: str):
    checkout_session = stripe.checkout.Session.retrieve(session_id)
    payment_intent = stripe.PaymentIntent.retrieve(checkout_session['payment_intent'])
    order_id = int(checkout_session['metadata']['order_id'])
    return payment_intent['status'], order_id
