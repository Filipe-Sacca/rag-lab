# RAGAS Chart Database Integration

## Summary
Connected RAGASChart component to database to display historical average scores automatically.

## File Modified
`/root/Filipe/Teste-Claude/rag-lab/frontend/chat-lab/src/components/RAGASChart.tsx`

## Key Changes

### 1. Hook Integration
Added `useComparison` hook to fetch comparison data from database:
```typescript
import { useComparison } from '../hooks/useComparison'

const { data: comparisonData, loading } = useComparison()
```

### 2. Average Calculation
Implemented `calculateAverageScores()` function that:
- Iterates through all database entries
- Sums all RAGAS scores (faithfulness, answer_relevancy, precision, recall)
- Returns average scores across all queries

**Formula**:
```typescript
Average Score = Sum of all scores / Total number of valid entries

For each metric:
- faithfulness_avg = Σ(faithfulness) / count
- answer_relevancy_avg = Σ(answer_relevancy) / count
- context_precision_avg = Σ(precision) / count
- context_recall_avg = Σ(recall) / count
```

### 3. Smart Score Display
Priority system for displaying scores:
1. **Individual query scores** (from props) - shown when user runs a specific query
2. **Database averages** - shown when no individual query scores available
3. **Empty state** - shown when database is empty

```typescript
const displayScores = scores || calculateAverageScores()
```

### 4. Visual Indicators
Added visual feedback to show data source:
- Badge showing "Avg of X queries" when displaying database averages
- Loading state while fetching data
- Empty state message when no data available

### 5. Props Update
Changed `scores` prop from required to optional:
```typescript
interface RAGASChartProps {
  scores?: RAGASScores | null  // Now optional
}
```

## Automatic Updates
The chart updates automatically every 5 seconds because:
- `useComparison` hook has auto-refresh built-in (5s interval)
- Component re-renders when `comparisonData` changes
- New averages are recalculated on each render with fresh data

## Data Flow

```
Database (SQLite)
    ↓
Backend API (/api/v1/comparison-data)
    ↓
useComparison Hook (auto-refresh every 5s)
    ↓
RAGASChart Component
    ↓
calculateAverageScores()
    ↓
Display in Chart
```

## Example Calculation

With 3 database entries:

| Entry | Faithfulness | Answer Relevancy | Precision | Recall |
|-------|--------------|------------------|-----------|--------|
| 1     | 0.92         | 0.88             | 0.85      | 0.82   |
| 2     | 0.94         | 0.91             | 0.88      | 0.85   |
| 3     | 0.90         | 0.86             | 0.83      | 0.80   |

**Averages**:
- Faithfulness: (0.92 + 0.94 + 0.90) / 3 = 0.92 → **92.0%**
- Answer Relevancy: (0.88 + 0.91 + 0.86) / 3 = 0.88 → **88.3%**
- Context Precision: (0.85 + 0.88 + 0.83) / 3 = 0.85 → **85.3%**
- Context Recall: (0.82 + 0.85 + 0.80) / 3 = 0.82 → **82.3%**

## Testing Scenarios

### Scenario 1: Empty Database
**Expected**: "No RAGAS data available. Run queries to see quality scores."

### Scenario 2: Database with History
**Expected**: Chart shows average scores with badge "Avg of N queries"

### Scenario 3: Individual Query
**Expected**: Chart shows specific query scores (ignores database averages)

### Scenario 4: Loading State
**Expected**: "Loading RAGAS data..." while fetching from database

## Benefits

1. **Immediate Visual Feedback**: Users see historical performance without running queries
2. **Trend Analysis**: Average scores show overall system quality
3. **Zero Configuration**: Works automatically with existing backend
4. **Backward Compatible**: Still supports individual query scores
5. **Real-time Updates**: Auto-refreshes every 5 seconds

## No Backend Changes Required

This implementation uses the existing `/api/v1/comparison-data` endpoint.
No backend modifications needed.

## Verification Steps

1. Open frontend: `http://localhost:3000`
2. Navigate to RAG Lab dashboard
3. Observe RAGAS chart showing database averages (if data exists)
4. Run a query - chart updates to show specific query scores
5. Wait 5 seconds - chart refreshes with latest database state

## Additional Changes

### App.tsx Update
**File**: `/root/Filipe/Teste-Claude/rag-lab/frontend/chat-lab/src/App.tsx`

Changed RAGAS chart rendering to always display (not just when there's a response):

**Before**:
```typescript
{response && <RAGASChart scores={response.ragas_scores} />}
```

**After**:
```typescript
<RAGASChart scores={response?.ragas_scores} />
```

This ensures:
- Chart is visible on page load, showing database averages
- Chart updates when user runs a query (shows individual scores)
- Chart reverts to averages when user clears the query
- No need to run a query to see RAGAS metrics

## Complete Implementation Summary

### Files Modified
1. `/root/Filipe/Teste-Claude/rag-lab/frontend/chat-lab/src/components/RAGASChart.tsx`
   - Added `useComparison` hook integration
   - Implemented `calculateAverageScores()` function
   - Made `scores` prop optional
   - Added loading and empty states
   - Added visual indicator for database averages

2. `/root/Filipe/Teste-Claude/rag-lab/frontend/chat-lab/src/App.tsx`
   - Changed chart to always render (not conditional on response)
   - Uses optional chaining for scores prop

### User Experience Flow

**Initial Page Load**:
1. User opens dashboard
2. RAGASChart fetches data from `/api/v1/comparison-data`
3. Chart displays average scores from all historical queries
4. Badge shows "Avg of X queries"

**After Running Query**:
1. User submits a query
2. Backend processes and returns response with RAGAS scores
3. Chart updates to show specific query scores
4. Badge disappears (showing individual result)

**Auto-Refresh**:
1. Every 5 seconds, `useComparison` refreshes database data
2. If showing averages, chart updates automatically
3. If showing individual query, individual scores take priority

**Empty Database**:
1. Chart shows message "No RAGAS data available"
2. Prompts user to run queries
3. After first query, averages start appearing

## Testing Checklist

- [ ] Empty database shows appropriate message
- [ ] Database with history shows average scores
- [ ] Badge displays correct count of queries
- [ ] Individual query overrides database averages
- [ ] Chart updates every 5 seconds when showing averages
- [ ] Loading state appears during initial fetch
- [ ] All 4 metrics calculate correctly
- [ ] Percentages display with 1 decimal place
- [ ] Average score calculation is correct
- [ ] Visual indicators match data source (individual vs average)
