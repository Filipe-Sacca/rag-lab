# SourcesList Component - Enhanced Features Documentation

## Overview

The SourcesList component has been enhanced with 4 powerful features to improve source exploration and analysis in the RAG Lab application.

## Feature 1: Query Highlights ✨

### Description
Automatically highlights parts of source content that match the user's query, making it easy to see why a particular chunk was retrieved.

### Implementation Details
- **Smart Keyword Extraction**: Filters out Portuguese stopwords (o, a, de, para, etc.)
- **Case-Insensitive Matching**: Finds matches regardless of capitalization
- **Visual Highlighting**: Uses yellow background (`bg-yellow-200`) with dark text (`text-yellow-900`)
- **Regex-Based**: Efficient pattern matching with word boundary detection

### Example
```
Query: "telefone da empresa"
Content: "Contato: Telefone (11) 1234-5678, Email..."
Result: Contato: [Telefone] (11) 1234-5678, Email...
         (where [Telefone] is highlighted in yellow)
```

### Technical Implementation
```typescript
// Location: src/utils/textHighlight.ts
export function highlightText(content: string, query: string)
  → Returns array of {text, highlight} objects
  → Filters Portuguese stopwords
  → Uses regex with word boundaries
```

---

## Feature 2: Expand/Collapse 📏

### Description
Long source chunks (>300 characters) are automatically collapsed to improve readability, with smooth expand/collapse controls.

### Implementation Details
- **Automatic Detection**: Content >300 characters triggers collapse
- **Preview Length**: Shows first 200 characters when collapsed
- **Smooth Transition**: 300ms CSS transition for visual polish
- **State Management**: Uses React Set to track expanded sources
- **Visual Feedback**: Background color changes when expanded

### Configuration
```typescript
const COLLAPSE_THRESHOLD = 300  // Characters before showing expand/collapse
const PREVIEW_LENGTH = 200      // Characters to show when collapsed
```

### UI Pattern
**Collapsed State:**
```
Content preview (200 chars)...
[Show more ↓]
```

**Expanded State:**
```
Full content here...
[Show less ↑]
```

### Technical Implementation
```typescript
const [expandedSources, setExpandedSources] = useState<Set<number>>(new Set())

const toggleExpanded = (index: number) => {
  // Toggle source expansion state
}
```

---

## Feature 3: Sorting Controls 🔄

### Description
Flexible sorting options to reorder sources based on different criteria.

### Available Sort Options
1. **Best Match (Default)** - Sorts by relevance score (highest first)
2. **Lowest Match** - Sorts by relevance score (lowest first)
3. **Document Name** - Alphabetical by document name, then by page
4. **Original Order** - Preserves the original retrieval order

### Implementation Details
- **Optimized**: Uses `useMemo` to prevent unnecessary re-sorting
- **Visual Indicator**: Dropdown shows current sort option
- **Icon**: ArrowUpDown icon for visual clarity
- **Accessible**: Proper ARIA labels for screen readers

### UI Component
```tsx
<select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
  <option value="score-desc">Best Match</option>
  <option value="score-asc">Lowest Match</option>
  <option value="document-asc">Document Name</option>
  <option value="original">Original Order</option>
</select>
```

### Technical Implementation
```typescript
const sortedSources = useMemo(() => {
  switch (sortBy) {
    case 'score-desc': return sorted.sort((a, b) => b.score - a.score)
    case 'score-asc': return sorted.sort((a, b) => a.score - b.score)
    case 'document-asc': return sorted.sort((a, b) =>
      a.metadata.document.localeCompare(b.metadata.document))
    case 'original': return sorted
  }
}, [filteredSources, sortBy])
```

---

## Feature 4: Score Filtering 🎯

### Description
Filter out low-relevance sources using quick-access filter pills.

### Filter Options
- **All (Default)** - Shows all sources (0% threshold)
- **High (>80%)** - Only high-confidence sources
- **Medium (>60%)** - Medium to high confidence
- **Low (>40%)** - Low to high confidence

### Implementation Details
- **Pill UI**: Clean pill-style buttons for quick filtering
- **Active State**: Highlighted pill shows current filter
- **Dynamic Count**: Shows "X of Y chunks" in header
- **Empty State**: Shows helpful message when no sources match
- **Optimized**: Uses `useMemo` for efficient filtering

### UI Pattern
```
[All] [Low (>40%)] [Medium (>60%)] [High (>80%)]
  ↑ Active filter highlighted in primary color
```

**Dynamic Count:**
```
Retrieved Sources  |  3 of 5 chunks
```

### Empty State
```
No sources match the current filter
[Clear filter] ← Link to reset
```

### Technical Implementation
```typescript
const [scoreFilter, setScoreFilter] = useState<number>(0)

const filteredSources = useMemo(() => {
  return sources.filter(source => source.score >= scoreFilter)
}, [sources, scoreFilter])
```

---

## Responsive Design

All features are fully responsive:

### Desktop (>640px)
- Controls in single row
- All pills visible
- Full dropdown labels

### Mobile (<640px)
- Stacked layout for controls
- Compact filter pills
- Touch-friendly buttons

---

## Accessibility Features

All features include comprehensive accessibility:

### ARIA Labels
```tsx
aria-label="Sort sources"
aria-label="Filter by All"
aria-label={isExpanded ? 'Show less' : 'Show more'}
```

### Keyboard Navigation
- Tab through all interactive elements
- Enter/Space to activate buttons
- Native select keyboard behavior

### Screen Reader Support
- Proper semantic HTML
- ARIA labels on all controls
- Meaningful status text

---

## Performance Optimizations

### React Optimization
```typescript
// Memoized filtering
const filteredSources = useMemo(() => {...}, [sources, scoreFilter])

// Memoized sorting
const sortedSources = useMemo(() => {...}, [filteredSources, sortBy])
```

### Efficient State Management
```typescript
// Set for O(1) lookup
const [expandedSources, setExpandedSources] = useState<Set<number>>(new Set())
```

### CSS Transitions
```tsx
className="transition-all duration-300"
```

---

## File Structure

```
src/
├── components/
│   └── SourcesList.tsx         # Main component (250 lines)
├── utils/
│   └── textHighlight.ts        # Highlighting utilities (95 lines)
└── types/
    └── rag.types.ts            # TypeScript interfaces
```

---

## Integration Guide

### 1. Pass Query to Component
```tsx
// In App.tsx
const [currentQuery, setCurrentQuery] = useState<string>('')

const handleQuery = async (query: string) => {
  setCurrentQuery(query) // Store query
  // ... rest of query logic
}
```

### 2. Update SourcesList Usage
```tsx
<SourcesList
  sources={response.metadata?.sources || []}
  query={currentQuery}  // Pass query for highlighting
/>
```

---

## Testing Checklist

- [x] Highlights work with Portuguese queries
- [x] Portuguese stopwords filtered correctly
- [x] Long sources (>300 chars) show expand/collapse
- [x] All 4 sort options work correctly
- [x] Filter updates count correctly
- [x] Empty state shows when all filtered out
- [x] Mobile responsive layout works
- [x] Keyboard accessible (tab navigation)
- [x] ARIA labels present
- [x] Smooth transitions (300ms)
- [x] Performance optimized (useMemo)

---

## Styling Details

### Color Palette
```css
/* Highlights */
bg-yellow-200      /* Highlight background */
text-yellow-900    /* Highlight text */

/* Score Colors (existing) */
bg-green-50 text-green-600    /* High score (>80%) */
bg-yellow-50 text-yellow-600  /* Medium score (>60%) */
bg-orange-50 text-orange-600  /* Low score (<60%) */

/* Filter Pills */
bg-primary-500 text-white     /* Active filter */
bg-gray-100 text-gray-600     /* Inactive filter */

/* Expanded State */
bg-gray-50 border-primary-300 /* Expanded source card */
```

### Transitions
```css
transition-all duration-300    /* Expand/collapse */
transition-colors              /* Hover states */
```

---

## Advanced Usage Examples

### Example 1: Technical Query
```
Query: "autenticação OAuth token"
→ Highlights: "autenticação", "OAuth", "token"
→ Filters stopwords: (none in this query)
→ Result: All three terms highlighted in yellow
```

### Example 2: Portuguese Query
```
Query: "qual é o telefone da empresa"
→ Keywords: "telefone", "empresa"
→ Filters stopwords: "qual", "é", "o", "da"
→ Result: Only "telefone" and "empresa" highlighted
```

### Example 3: Filtering Workflow
```
1. Initial: 5 chunks shown (All filter)
2. Click "High (>80%)": 2 chunks shown
3. Status: "2 of 5 chunks"
4. Click "All": Back to 5 chunks
```

### Example 4: Sorting Workflow
```
1. Initial: Best Match (score descending)
2. Switch to "Document Name": Alphabetical order
3. Switch to "Lowest Match": Reverse score order
4. Helps identify edge cases or low-confidence results
```

---

## Future Enhancement Ideas

### Potential Additions
1. **Custom Score Slider**: Drag slider for any threshold (0-100%)
2. **Multi-Column Sort**: Secondary sort options
3. **Highlight Color Options**: User-selectable highlight colors
4. **Export Sources**: Download filtered sources as JSON/CSV
5. **Bookmark Sources**: Mark favorite chunks for later
6. **Inline Comments**: Add notes to specific sources
7. **Compare Sources**: Side-by-side comparison view
8. **Search Within Sources**: Additional filter by text content

### Configuration Options
```typescript
interface SourcesListConfig {
  collapseThreshold?: number     // Default: 300
  previewLength?: number          // Default: 200
  defaultSort?: SortOption        // Default: 'score-desc'
  highlightColor?: string         // Default: 'yellow'
  showMetadata?: boolean          // Default: true
}
```

---

## Troubleshooting

### Highlights Not Showing
- Check that `query` prop is passed to SourcesList
- Verify `currentQuery` state is updated in handleQuery
- Ensure query contains meaningful keywords (not all stopwords)

### Expand/Collapse Not Working
- Check browser console for React warnings
- Verify state updates in React DevTools
- Test with different content lengths

### Sort Not Working
- Check that sources array is not empty
- Verify score values are numbers (0-1 range)
- Check browser console for sorting errors

### Filter Not Working
- Verify score values are valid numbers
- Check that filter state updates correctly
- Test with different score thresholds

---

## Component Props

```typescript
interface SourcesListProps {
  sources: Source[]  // Array of retrieved sources
  query: string      // User's search query for highlighting
}

interface Source {
  content: string
  score: number  // 0-1 range
  metadata: {
    document: string
    page: number
    chunk_id: string
  }
}
```

---

## Summary

The enhanced SourcesList component provides:
- ✅ **Query Highlights**: Visual keyword matching with Portuguese support
- ✅ **Expand/Collapse**: Improved readability for long sources
- ✅ **Sorting Controls**: Flexible source reordering
- ✅ **Score Filtering**: Quick relevance filtering

All features are production-ready with:
- Modern React patterns (hooks, memoization)
- Full accessibility (ARIA, keyboard)
- Responsive design (mobile-friendly)
- Smooth animations (CSS transitions)
- Optimized performance (useMemo, Set)

**Total Lines of Code**: ~345 lines
- SourcesList.tsx: 250 lines
- textHighlight.ts: 95 lines

**Dependencies Added**: None (uses existing Lucide icons, Tailwind CSS)
