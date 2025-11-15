# Cost Tracking & Monitoring

This document explains the cost tracking system for Claude API usage in the Wrestling Promo Analyzer.

## Overview

Every analysis performed by Jake Morrison (or future judges) uses the Claude API, which has per-token pricing. The cost tracking system automatically monitors and calculates costs for each analysis.

## Features

### 1. Automatic Cost Calculation

Every time an analysis is performed:
- **Input tokens** (prompt sent to Claude) are tracked
- **Output tokens** (Claude's response) are tracked
- **Total cost** is automatically calculated based on current pricing
- All data is stored in the database for future reference

### 2. API Endpoints

#### Get Cost Statistics
```http
GET /api/v1/stats/costs?days=30
```

Returns aggregated cost statistics for the specified time period.

**Response:**
```json
{
  "period_start": "2025-01-01T00:00:00",
  "period_end": "2025-01-30T00:00:00",
  "total_analyses": 150,
  "total_input_tokens": 450000,
  "total_output_tokens": 300000,
  "total_tokens": 750000,
  "total_cost_usd": 45.00,
  "formatted_total_cost": "$45.00",
  "avg_cost_per_analysis": 0.30,
  "max_cost": 1.25,
  "min_cost": 0.05
}
```

#### Get Pricing Information
```http
GET /api/v1/stats/pricing
GET /api/v1/stats/pricing?model=claude-3-5-sonnet-20241022
```

Returns current pricing for Claude models.

**Response (all models):**
```json
{
  "claude-3-5-sonnet-20241022": {
    "model": "claude-3-5-sonnet-20241022",
    "name": "Claude 3.5 Sonnet",
    "input_price_per_1m": 3.00,
    "output_price_per_1m": 15.00
  },
  "claude-3-haiku": {
    "model": "claude-3-haiku",
    "name": "Claude 3 Haiku",
    "input_price_per_1m": 0.25,
    "output_price_per_1m": 1.25
  }
}
```

### 3. Cost Data in Responses

Analysis responses now include detailed cost information:

```json
{
  "analysis_id": "...",
  "overall_score": 85,
  "processing_time_seconds": 12.5,
  "input_tokens": 2500,
  "output_tokens": 1800,
  "total_tokens": 4300,
  "estimated_cost_usd": 0.0345,
  "model_version": "claude-3-5-sonnet-20241022"
}
```

## Current Pricing (as of January 2025)

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|-------|----------------------|------------------------|
| Claude 3.5 Sonnet (Latest) | $3.00 | $15.00 |
| Claude 3 Haiku | $0.25 | $1.25 |
| Claude 3 Opus | $15.00 | $75.00 |

Source: https://www.anthropic.com/pricing

## Typical Costs by Promo Length

Based on testing:

| Promo Length | Transcript Words | Typical Cost | Range |
|--------------|-----------------|--------------|-------|
| 30 seconds | ~100 words | $0.08 | $0.05 - $0.10 |
| 2 minutes | ~400 words | $0.20 | $0.15 - $0.25 |
| 5 minutes | ~1000 words | $0.40 | $0.30 - $0.50 |
| 10 minutes | ~2000 words | $0.80 | $0.60 - $1.00 |

## Database Schema

Cost tracking is stored in the `analyses` table:

```sql
ALTER TABLE analyses
    ADD COLUMN input_tokens INTEGER,
    ADD COLUMN output_tokens INTEGER,
    ADD COLUMN total_tokens INTEGER,
    ADD COLUMN estimated_cost_usd DECIMAL(10, 4);
```

## Implementation Details

### Cost Calculation Utility

Located at `backend/utils/cost_tracking.py`:

```python
from utils.cost_tracking import calculate_cost

# Calculate cost for an API call
cost = calculate_cost(
    input_tokens=2500,
    output_tokens=1800,
    model="claude-3-5-sonnet-20241022"
)
# Returns: Decimal('0.0345')
```

### Automatic Tracking in Celery Tasks

The `analyze_with_jake` task automatically tracks costs:

```python
# Extract token usage from API response
input_tokens = response.usage.input_tokens
output_tokens = response.usage.output_tokens
estimated_cost = calculate_cost(input_tokens, output_tokens, model)

# Store in database
analysis = Analysis(
    ...
    input_tokens=input_tokens,
    output_tokens=output_tokens,
    total_tokens=total_tokens,
    estimated_cost_usd=estimated_cost,
    ...
)
```

## Monitoring & Alerts

### Basic Monitoring

Check your costs regularly:
```bash
# Get last 7 days
curl http://localhost:8000/api/v1/stats/costs?days=7

# Get last 30 days
curl http://localhost:8000/api/v1/stats/costs?days=30
```

### Future Enhancements

Potential additions for production:

1. **Cost Alerts**: Email notifications when daily/monthly costs exceed thresholds
2. **Per-User Quotas**: Limit API usage per user to prevent abuse
3. **Cost Dashboard**: Visual charts showing cost trends over time
4. **Budget Limits**: Automatically pause processing if budget is exceeded
5. **Export Reports**: CSV/PDF reports for accounting

## Cost Optimization Tips

### 1. Use Appropriate Models

- **Claude 3.5 Sonnet**: Default - good balance of quality and cost
- **Claude 3 Haiku**: 5-10x cheaper - consider for simpler analyses
- **Claude 3 Opus**: Most capable but expensive - use sparingly

### 2. Optimize Prompts

- Keep system prompts concise
- Don't include unnecessary context
- Use JSON mode to reduce output tokens

### 3. Batch Processing

- Process multiple videos in parallel to amortize overhead
- Consider analyzing shorter clips during testing

### 4. Caching

- Cache common responses (future enhancement)
- Reuse analyses for similar content

## Database Migration

To add cost tracking to an existing installation:

```bash
# Run migration
psql -U promo_analyzer -d promo_analyzer_db -f backend/migrations/003_add_cost_tracking.sql
```

## Troubleshooting

### Missing Cost Data

If older analyses show `null` for cost fields:
- This is normal - cost tracking was added in Sprint 2
- Only new analyses will have cost data
- Historical data can't be reconstructed without API logs

### Inaccurate Costs

Cost estimates are based on:
- Current published pricing from Anthropic
- Actual token counts from API responses

If actual costs differ:
- Check if Anthropic updated pricing
- Update `MODEL_PRICING` in `cost_tracking.py`
- Pricing changes are applied to future analyses only

## Support

For questions about cost tracking:
1. Check API documentation at `/docs`
2. Review this document
3. Contact system administrator
