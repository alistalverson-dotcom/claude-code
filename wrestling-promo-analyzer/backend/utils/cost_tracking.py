"""
Cost tracking utilities for Claude API usage

Pricing as of January 2025:
- Claude 3.5 Sonnet (Latest): $3.00 / 1M input tokens, $15.00 / 1M output tokens
- Claude 3 Haiku: $0.25 / 1M input tokens, $1.25 / 1M output tokens
- Claude 3 Opus: $15.00 / 1M input tokens, $75.00 / 1M output tokens

Reference: https://www.anthropic.com/pricing
"""

from decimal import Decimal
from typing import Dict, Optional
from datetime import datetime, timedelta


# Model pricing (USD per 1M tokens)
MODEL_PRICING = {
    # Claude 3.5 Sonnet
    "claude-3-5-sonnet-20241022": {
        "input": Decimal("3.00"),
        "output": Decimal("15.00"),
        "name": "Claude 3.5 Sonnet"
    },
    "claude-3-5-sonnet": {
        "input": Decimal("3.00"),
        "output": Decimal("15.00"),
        "name": "Claude 3.5 Sonnet"
    },
    # Claude 3 Haiku (for faster, cheaper tasks)
    "claude-3-haiku-20240307": {
        "input": Decimal("0.25"),
        "output": Decimal("1.25"),
        "name": "Claude 3 Haiku"
    },
    "claude-3-haiku": {
        "input": Decimal("0.25"),
        "output": Decimal("1.25"),
        "name": "Claude 3 Haiku"
    },
    # Claude 3 Opus (most capable, most expensive)
    "claude-3-opus-20240229": {
        "input": Decimal("15.00"),
        "output": Decimal("75.00"),
        "name": "Claude 3 Opus"
    },
    "claude-3-opus": {
        "input": Decimal("15.00"),
        "output": Decimal("75.00"),
        "name": "Claude 3 Opus"
    },
}

# Default pricing if model not found
DEFAULT_PRICING = {
    "input": Decimal("3.00"),
    "output": Decimal("15.00"),
    "name": "Unknown Model"
}


def calculate_cost(
    input_tokens: int,
    output_tokens: int,
    model: str = "claude-3-5-sonnet-20241022"
) -> Decimal:
    """
    Calculate the cost of a Claude API call

    Args:
        input_tokens: Number of input tokens sent
        output_tokens: Number of output tokens received
        model: Model identifier string

    Returns:
        Cost in USD as Decimal with 4 decimal places
    """
    pricing = MODEL_PRICING.get(model, DEFAULT_PRICING)

    # Convert to millions of tokens
    input_millions = Decimal(input_tokens) / Decimal("1000000")
    output_millions = Decimal(output_tokens) / Decimal("1000000")

    # Calculate costs
    input_cost = input_millions * pricing["input"]
    output_cost = output_millions * pricing["output"]

    total_cost = input_cost + output_cost

    # Round to 4 decimal places
    return round(total_cost, 4)


def format_cost(cost: Decimal) -> str:
    """
    Format cost for display

    Args:
        cost: Cost in USD as Decimal

    Returns:
        Formatted string like "$0.0123" or "$1.23"
    """
    if cost < Decimal("0.01"):
        return f"${cost:.4f}"
    else:
        return f"${cost:.2f}"


def estimate_cost_from_text(
    text: str,
    estimated_output_tokens: int = 2000,
    model: str = "claude-3-5-sonnet-20241022"
) -> Dict[str, any]:
    """
    Estimate cost before making API call

    Args:
        text: Input text to analyze
        estimated_output_tokens: Estimated response size
        model: Model to use

    Returns:
        Dictionary with estimated costs and token counts
    """
    # Rough estimation: ~4 characters per token for English text
    estimated_input_tokens = len(text) // 4

    cost = calculate_cost(estimated_input_tokens, estimated_output_tokens, model)

    return {
        "estimated_input_tokens": estimated_input_tokens,
        "estimated_output_tokens": estimated_output_tokens,
        "estimated_total_tokens": estimated_input_tokens + estimated_output_tokens,
        "estimated_cost_usd": cost,
        "formatted_cost": format_cost(cost),
        "model": model,
    }


def get_cost_summary(db_session, start_date: Optional[datetime] = None) -> Dict:
    """
    Get cost summary for a time period

    Args:
        db_session: SQLAlchemy database session
        start_date: Start date for summary (default: last 30 days)

    Returns:
        Dictionary with cost statistics
    """
    from models import Analysis
    from sqlalchemy import func

    if start_date is None:
        start_date = datetime.utcnow() - timedelta(days=30)

    # Query analyses in time period
    query = db_session.query(
        func.count(Analysis.id).label("total_analyses"),
        func.sum(Analysis.input_tokens).label("total_input_tokens"),
        func.sum(Analysis.output_tokens).label("total_output_tokens"),
        func.sum(Analysis.total_tokens).label("total_tokens"),
        func.sum(Analysis.estimated_cost_usd).label("total_cost"),
        func.avg(Analysis.estimated_cost_usd).label("avg_cost_per_analysis"),
        func.max(Analysis.estimated_cost_usd).label("max_cost"),
        func.min(Analysis.estimated_cost_usd).label("min_cost"),
    ).filter(
        Analysis.created_at >= start_date
    )

    result = query.first()

    return {
        "period_start": start_date.isoformat(),
        "period_end": datetime.utcnow().isoformat(),
        "total_analyses": result.total_analyses or 0,
        "total_input_tokens": result.total_input_tokens or 0,
        "total_output_tokens": result.total_output_tokens or 0,
        "total_tokens": result.total_tokens or 0,
        "total_cost_usd": float(result.total_cost or 0),
        "formatted_total_cost": format_cost(result.total_cost or Decimal(0)),
        "avg_cost_per_analysis": float(result.avg_cost_per_analysis or 0),
        "max_cost": float(result.max_cost or 0),
        "min_cost": float(result.min_cost or 0),
    }


def get_model_pricing_info(model: str = None) -> Dict:
    """
    Get pricing information for a model

    Args:
        model: Model identifier (if None, returns all pricing)

    Returns:
        Pricing information dictionary
    """
    if model:
        pricing = MODEL_PRICING.get(model, DEFAULT_PRICING)
        return {
            "model": model,
            "name": pricing["name"],
            "input_price_per_1m": float(pricing["input"]),
            "output_price_per_1m": float(pricing["output"]),
            "formatted_input_price": f"${pricing['input']:.2f} / 1M tokens",
            "formatted_output_price": f"${pricing['output']:.2f} / 1M tokens",
        }
    else:
        return {
            model_id: {
                "model": model_id,
                "name": info["name"],
                "input_price_per_1m": float(info["input"]),
                "output_price_per_1m": float(info["output"]),
            }
            for model_id, info in MODEL_PRICING.items()
        }


# Quick cost reference for common scenarios
# Updated for increased frame density (15-60 frames based on duration)
COST_REFERENCES = {
    "short_promo_30s": {
        "description": "30-second promo (~100 words transcript, 15-20 frames)",
        "estimated_cost": "$0.08 - $0.12",
        "frames": "15-20",
        "frame_interval": "~1.5-2s",
    },
    "medium_promo_2min": {
        "description": "2-minute promo (~400 words transcript, 25-30 frames)",
        "estimated_cost": "$0.20 - $0.30",
        "frames": "25-30",
        "frame_interval": "~4-5s",
    },
    "medium_promo_3min": {
        "description": "3-minute promo (~600 words transcript, 30-40 frames)",
        "estimated_cost": "$0.25 - $0.40",
        "frames": "30-40",
        "frame_interval": "~4.5-6s",
    },
    "long_promo_5min": {
        "description": "5-minute promo (~1000 words transcript, 40-50 frames)",
        "estimated_cost": "$0.40 - $0.60",
        "frames": "40-50",
        "frame_interval": "~6-8.5s",
    },
    "very_long_promo_10min": {
        "description": "10-minute promo (~2000 words transcript, 50-60 frames max)",
        "estimated_cost": "$0.70 - $1.20",
        "frames": "50-60",
        "frame_interval": "~10-12s",
    },
}
