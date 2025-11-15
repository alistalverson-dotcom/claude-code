# Bug Fixes - Multi-Judge System

## Overview
This document tracks critical bugs found and fixed during the multi-judge system implementation debugging session.

---

## Bug #1: Category Score Mapping Issue

### Description
**Severity**: CRITICAL

Dr. Diana Sterling uses different category names than the database expects. Without proper mapping, her evaluation scores would fail to save correctly or save to incorrect database fields.

**Judge Category Mismatch:**
- Dr. Diana Sterling uses: `emotional_authenticity`, `psychological_depth`, `non_verbal_communication`, `audience_psychology`, `vocal_dynamics`, `cognitive_clarity`, `character_consistency`, `emotional_intelligence`, `presence_charisma`
- Database columns expect: `psychology_score`, `character_score`, `delivery_score`, `story_structure_score`, `crowd_connection_score`, `originality_score`, `facial_expressions_score`, `body_language_score`, `visual_presence_score`

### Impact
- Diana Sterling's analysis would fail to save to database
- Or worse, scores would save to incorrect fields, providing misleading data to users
- Visual analysis would use unmapped scores, causing runtime errors

### Root Cause
Each judge has unique evaluation criteria and category names, but the database schema uses standardized column names based on Jake Morrison's original framework.

### Fix Applied
**File**: `backend/tasks.py`
**Lines**: 583-625, 862, 908

Created `map_judge_categories_to_db()` function that translates judge-specific category names to standardized database column names:

```python
def map_judge_categories_to_db(category_scores: dict, judge_slug: str) -> dict:
    """
    Map judge-specific category names to standardized database fields.

    Each judge uses different category names based on their evaluation framework.
    This function maps those to the standardized database column names.
    """

    if judge_slug == 'diana-sterling':
        # Dr. Diana Sterling's psychological categories → Database fields
        return {
            'psychology': category_scores.get('psychological_depth', 0),
            'character_work': category_scores.get('character_consistency', 0),
            'delivery': category_scores.get('vocal_dynamics', 0),
            'story_structure': category_scores.get('cognitive_clarity', 0),
            'crowd_connection': category_scores.get('audience_psychology', 0),
            'originality': category_scores.get('emotional_authenticity', 0),
            'facial_expressions': category_scores.get('emotional_authenticity', 0),
            'body_language': category_scores.get('non_verbal_communication', 0),
            'visual_presence': category_scores.get('presence_charisma', 0),
        }
    else:
        # Jake Morrison (default) - standard categories match database 1:1
        return {
            'psychology': category_scores.get('psychology', 0),
            'character_work': category_scores.get('character_work', 0),
            'delivery': category_scores.get('delivery', 0),
            'story_structure': category_scores.get('story_structure', 0),
            'crowd_connection': category_scores.get('crowd_connection', 0),
            'originality': category_scores.get('originality', 0),
            'facial_expressions': category_scores.get('facial_expressions', 0),
            'body_language': category_scores.get('body_language', 0),
            'visual_presence': category_scores.get('visual_presence', 0),
        }
```

**Applied in two locations:**

1. **Database Save** (line 862):
```python
# Map judge-specific categories to database fields
mapped_scores = map_judge_categories_to_db(analysis_result['category_scores'], judge_slug)

# Create analysis record with mapped scores
analysis = Analysis(
    video_id=video.id,
    judge_id=judge.id,
    psychology_score=Decimal(str(mapped_scores['psychology'])),
    character_score=Decimal(str(mapped_scores['character_work'])),
    delivery_score=Decimal(str(mapped_scores['delivery'])),
    # ... etc
)
```

2. **Visual Analysis** (line 908):
```python
# Use mapped scores for visual analysis
mapped_scores = map_judge_categories_to_db(category_scores, judge_slug)
visual_analysis_task = create_visual_analysis.si(
    video.id,
    transcript_text,
    mapped_scores,  # Use mapped scores
    str(video.file_path)
)
```

### Verification
- [x] Mapping function handles all 9 categories for both judges
- [x] Default fallback to 0 if category missing
- [x] Applied before database save to ensure correct field mapping
- [x] Applied in visual analysis pipeline for consistency
- [x] Backwards compatible with Jake Morrison (1:1 mapping)

---

## Bug #2: Direct API Fetch in Component

### Description
**Severity**: MODERATE

`JudgeSelector.tsx` component was using direct `fetch('/api/v1/judges')` instead of the centralized API service, which could cause issues with:
- API base URL configuration (dev vs production)
- Inconsistent error handling
- Inconsistent response parsing

### Impact
- Component might fail to fetch judges in production if API_BASE_URL differs
- Error handling would be inconsistent with other API calls
- Harder to maintain and test

### Root Cause
Component was created with inline fetch logic instead of using the existing centralized API service pattern.

### Fix Applied
**Files**:
- `frontend/src/services/api.ts` (lines 117-123)
- `frontend/src/components/JudgeSelector.tsx` (line 3, line 23)

**Added to `api.ts`:**
```typescript
/**
 * Get all active judges
 */
export async function getJudges(): Promise<JudgeResponse[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/judges`);
  return handleResponse<JudgeResponse[]>(response);
}
```

**Updated `JudgeSelector.tsx`:**
```typescript
// Import centralized API function
import { getJudges } from '../services/api';

// Use in component
const fetchJudges = async () => {
  try {
    const data = await getJudges();  // Use centralized function
    setJudges(data.filter((j: JudgeResponse) => j.is_active));
    setLoading(false);
  } catch (err) {
    setError(err instanceof Error ? err.message : 'Failed to load judges');
    setLoading(false);
  }
};
```

### Verification
- [x] Component imports and uses centralized API function
- [x] Consistent with other API calls in the application
- [x] Uses correct API_BASE_URL from environment configuration
- [x] Error handling matches existing patterns

---

## Testing Checklist

After applying these fixes, verify:

- [ ] Diana Sterling analysis saves correctly to database
- [ ] All 9 category scores map to correct database fields
- [ ] Visual analysis works with Diana Sterling's categories
- [ ] JudgeSelector component fetches judges in all environments
- [ ] Frontend can switch between Jake Morrison and Diana Sterling
- [ ] Both judges provide different analysis styles
- [ ] No console errors or warnings

---

## Related Files

**Backend:**
- `backend/tasks.py` - Category mapping function and analysis pipeline
- `backend/models.py` - Analysis model with standardized score fields
- `backend/prompts/diana_sterling_system.md` - Diana's evaluation framework

**Frontend:**
- `frontend/src/components/JudgeSelector.tsx` - Judge selection component
- `frontend/src/services/api.ts` - Centralized API service
- `frontend/src/types.ts` - TypeScript interfaces

**Documentation:**
- `MULTI_JUDGE_SYSTEM.md` - Complete multi-judge system guide
- `SETUP_MULTI_JUDGE.md` - Setup and deployment instructions

---

## Future Considerations

### Scalability
When adding future judges:
1. Add new mapping case in `map_judge_categories_to_db()`
2. Ensure all 9 database fields are mapped
3. Test database save and visual analysis pipeline
4. Update this documentation

### Alternative Approaches Considered
1. **Dynamic database schema** - Rejected: Too complex, breaks existing queries
2. **JSON column for categories** - Rejected: Loses type safety and query performance
3. **Separate tables per judge** - Rejected: Duplicates data, complex queries
4. **Current approach (mapping)** - ✅ Selected: Simple, maintainable, backwards compatible

---

**Date**: 2025-11-15
**Fixed By**: Claude (Debugging Session)
**Commit**: [Pending]
