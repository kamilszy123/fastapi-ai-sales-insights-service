import functools
import logging
import os
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Standalone script (not an installed package) — this makes `app.*` importable
# without installing the project, since it's launched directly by Claude Desktop.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(Path(__file__).parent.parent / ".env")

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


class _MCPSettings(BaseSettings):
    mcp_user_id: int
    mcp_database_url: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


try:
    _settings = _MCPSettings()
except ValidationError:
    logger.exception(
        "Missing or invalid MCP settings — set MCP_DATABASE_URL and MCP_USER_ID "
        "in .env. See mcp_server/README.md's Configure section."
    )
    raise

engine = create_engine(_settings.mcp_database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from app.repositories.analytics_repository import AnalyticsRepository  # noqa: E402  (imports after settings so .env is loaded)
from app.services.analytics_service import AnalyticsService  # noqa: E402
from app.tools.analytics_tools import (  # noqa: E402
    GetMonthlySalesArgs,
    GetTopProductsArgs,
    GetTopReturnedProductsArgs,
    get_monthly_sales_tool,
    get_top_products_tool,
    get_top_returned_products_tool,
)

mcp = FastMCP("Sales Analytics")


@contextmanager
def _analytics_service() -> Iterator[AnalyticsService]:
    db = SessionLocal()
    try:
        yield AnalyticsService(AnalyticsRepository(db))
    finally:
        db.close()


def _log_errors(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception:
            logger.exception("%s failed", fn.__name__)
            raise

    return wrapper


@mcp.tool()
@_log_errors
def get_top_products(limit: int = 5) -> dict:
    """Top-selling products ranked by total revenue.

    Returns a list of products with name, sold_quantity, returns_quantity,
    and revenue. Use this to identify your best-performing products.
    The `limit` parameter controls how many products are returned (default 5).
    """
    with _analytics_service() as service:
        return get_top_products_tool(
            args=GetTopProductsArgs(limit=limit),
            analytics_service=service,
            user_id=_settings.mcp_user_id,
        )


@mcp.tool()
@_log_errors
def get_top_returned_products(limit: int = 5) -> dict:
    """Products with the highest number of returns.

    Returns a list of products with name, sold_quantity, returns_quantity,
    and return_rate (as a percentage). Use this to spot products with
    quality issues or listing/expectation mismatches.
    The `limit` parameter controls how many products are returned (default 5).
    """
    with _analytics_service() as service:
        return get_top_returned_products_tool(
            args=GetTopReturnedProductsArgs(limit=limit),
            analytics_service=service,
            user_id=_settings.mcp_user_id,
        )


@mcp.tool()
@_log_errors
def get_monthly_sales() -> dict:
    """Month-by-month sales breakdown across all time.

    Returns a chronological list of months with orders_count, revenue,
    and average_order_value. Use this to identify growth trends,
    seasonality, and revenue patterns over time.
    """
    with _analytics_service() as service:
        return get_monthly_sales_tool(
            args=GetMonthlySalesArgs(),
            analytics_service=service,
            user_id=_settings.mcp_user_id,
        )


@mcp.resource(
    "sales://overview",
    name="sales_overview",
    description="Current store-wide totals: orders count, revenue, products sold, returns count.",
    mime_type="application/json",
)
@_log_errors
def sales_overview() -> dict:
    with _analytics_service() as service:
        return service.get_overview(user_id=_settings.mcp_user_id).model_dump(mode="json")


@mcp.resource(
    "sales://returns/overview",
    name="returns_overview",
    description="Store-wide return metrics: products sold, returns count, return rate.",
    mime_type="application/json",
)
@_log_errors
def returns_overview() -> dict:
    with _analytics_service() as service:
        return service.get_returns_overview(user_id=_settings.mcp_user_id).model_dump(mode="json")


@mcp.resource(
    "sales://offers/{offer_id}/name-performance",
    name="offer_name_performance",
    description=(
        "Sales performance for a specific offer, broken down by product name "
        "(sold/returns quantity, revenue, average price, return rate, active-days stats)."
    ),
    mime_type="application/json",
)
@_log_errors
def offer_name_performance(offer_id: str) -> dict:
    with _analytics_service() as service:
        result = service.get_offer_name_performance(
            user_id=_settings.mcp_user_id, offer_id=offer_id
        )
        return {"name_performance": [r.model_dump(mode="json") for r in result]}


@mcp.resource(
    "sales://offers/{offer_id}/price-performance",
    name="offer_price_performance",
    description=(
        "Sales performance for a specific offer, broken down by price point "
        "(sold/returns quantity, revenue, return rate)."
    ),
    mime_type="application/json",
)
@_log_errors
def offer_price_performance(offer_id: str) -> dict:
    with _analytics_service() as service:
        result = service.get_offer_price_performance(
            user_id=_settings.mcp_user_id, offer_id=offer_id
        )
        return {"price_performance": [r.model_dump(mode="json") for r in result]}


@mcp.prompt()
def sales_performance_review() -> str:
    """Start a full store performance review using the available tools and resources."""
    return (
        "Give me a full review of my store's sales performance. "
        "Use get_top_products, get_top_returned_products, and get_monthly_sales "
        "(and the sales://overview and sales://returns/overview resources) to ground your analysis. "
        "Use only the data returned by these tools/resources — do not invent numbers or speculate "
        "about competitors, customer behavior, or product quality beyond what the data supports. "
        "Call out any months with partial data. Keep recommendations practical and actionable."
    )


@mcp.prompt()
def offer_deep_dive(offer_id: str) -> str:
    """Start a focused performance review for a single offer."""
    return (
        f"Analyze the sales performance of offer {offer_id}. "
        f"Use the sales://offers/{offer_id}/name-performance and "
        f"sales://offers/{offer_id}/price-performance resources to ground your analysis. "
        "Use only the data returned by these resources — do not invent numbers or speculate beyond "
        "what the data supports. Highlight return-rate concerns and pricing performance, and state "
        "explicitly if the data is insufficient to draw a conclusion."
    )


if __name__ == "__main__":
    logger.info("Starting Sales Analytics MCP server (stdio)")
    mcp.run()
