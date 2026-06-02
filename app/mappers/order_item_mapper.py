from app.models.order_item import OrderItem
from app.utils.converters import parse_int, parse_decimal


def map_dict_to_order_item(data: dict) -> OrderItem:
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

def update_order_item_from_dict(existing_order_item: OrderItem, data: dict) -> None:
    returns_quantity = parse_int(data.get("ReturnsQuantity"))
    if returns_quantity is not None:
        existing_order_item.returns_quantity = returns_quantity
