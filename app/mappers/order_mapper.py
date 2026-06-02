from app.models.order import Order
from app.utils.converters import parse_datetime, parse_decimal


def map_dict_to_order(data: dict, user_id: int, import_job_id: int) -> Order:
    mapped_data = {
        "user_id": user_id,
        "import_job_id": import_job_id,
        "external_order_id": data.get("OrderId"),
        "order_date": parse_datetime(data.get("OrderDate")),
        "seller_status": data.get("SellerStatus"),
        "payment_status": data.get("PaymentStatus"),
        "total_to_pay_amount": parse_decimal(data.get("TotalToPayAmount")),
        "total_to_pay_currency": data.get("TotalToPayCurrency"),
        "total_paid_amount": parse_decimal(data.get("TotalPaidAmount")),
        "total_paid_currency": data.get("TotalPaidCurrency"),

    }
    return Order(**mapped_data)

def update_order_from_dict(existing_order: Order, data: dict, import_job_id: int) -> None:
    seller_status = data.get("SellerStatus")
    if seller_status is not None:
        existing_order.seller_status = seller_status

    payment_status = data.get("PaymentStatus")
    if payment_status is not None:
        existing_order.payment_status = payment_status

    total_to_pay_amount = parse_decimal(data.get("TotalToPayAmount"))
    if total_to_pay_amount is not None:
        existing_order.total_to_pay_amount = total_to_pay_amount

    total_paid_amount = parse_decimal(data.get("TotalPaidAmount"))
    if total_paid_amount is not None:
        existing_order.total_paid_amount = total_paid_amount

    existing_order.import_job_id = import_job_id
