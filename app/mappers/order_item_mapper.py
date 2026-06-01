from app.models import OrderItem
from app.utils.converters import parse_int, parse_decimal


def map_dict_to_order_item(data: dict):
    mapped_data = {
        "external_line_item_id": data.get("LineItemId"),
        "external_offer_id": data.get("OfferId"),
        "name": data.get("Name"),
        "quantity": parse_int(data.get("Quantity")),
        "price": parse_decimal(data.get("Price")),
        "currency": data.get("Currency"),
        "returns_quantity": parse_int(data.get("ReturnsQuantity")),
    }
    return OrderItem(**mapped_data)