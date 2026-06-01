from app.models import Order
from app.utils.converters import parse_datetime, parse_decimal


def map_dict_to_order(data: dict, user_id: int, import_job_id: int):
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
