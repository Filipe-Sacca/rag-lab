# SourcesList Quick Reference

## Component Props

```typescript
<SourcesList
  sources={Source[]}  // Array of retrieved sources
  query={string}      // User's search query for highlighting
/>
```

## Features at a Glance

| Feature | Icon | Description | Key |
|---------|------|-------------|-----|
| **Query Highlights** | ✨ | Highlights matching keywords in yellow | Auto |
| **Expand/Collapse** | 📏 | Long sources (>300 chars) can expand | Button |
| **Sorting** | 🔄 | 4 sort options via dropdown | Dropdown |
| **Filtering** | 🎯 | Filter by score threshold | Pills |

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Tab` | Navigate between controls |
| `Enter` / `Space` | Activate button/pill |
| `↑` `↓` | Navigate dropdown options |
| `Esc` | Close dropdown |

## Filter Thresholds

| Filter | Score Range | Use Case |
|--------|-------------|----------|
| **All** | 0% - 100% | View everything |
| **Low** | 40% - 100% | Filter very low confidence |
| **Medium** | 60% - 100% | Quality sources |
| **High** | 80% - 100% | Best matches only |

## Sort Options

| Option | Order | Use Case |
|--------|-------|----------|
| **Best Match** | Score DESC | Default, best first |
| **Lowest Match** | Score ASC | Find edge cases |
| **Document Name** | Alphabetical | Organize by doc |
| **Original Order** | As retrieved | RAG system order |

## Score Badge Colors

| Score Range | Color | Visual |
|-------------|-------|--------|
| ≥ 80% | Green | `bg-green-50 text-green-600` |
| 60-79% | Yellow | `bg-yellow-50 text-yellow-600` |
| < 60% | Orange | `bg-orange-50 text-orange-600` |

## State Management

```typescript
// Expansion state (Set for O(1) lookup)
const [expandedSources, setExpandedSources] = useState<Set<number>>(new Set())

// Sort state
const [sortBy, setSortBy] = useState<SortOption>('score-desc')

// Filter state
const [scoreFilter, setScoreFilter] = useState<number>(0)
```

## Utilities (textHighlight.ts)

```typescript
// Extract meaningful keywords (filter stopwords)
extractKeywords(query: string): string[]

// Highlight text matches
highlightText(content: string, query: string): Array<{text, highlight}>

// Truncate for preview
truncateText(text: string, maxLength: number): string
```

## Configuration Constants

```typescript
const COLLAPSE_THRESHOLD = 300  // Chars before collapse
const PREVIEW_LENGTH = 200      // Chars in preview
```

## Portuguese Stopwords

Filtered automatically: `o`, `a`, `de`, `da`, `do`, `para`, `com`, `em`, `qual`, `que`, etc. (40 total)

## CSS Classes

### Highlights
```css
bg-yellow-200        /* Highlight background */
text-yellow-900      /* Highlight text */
px-0.5 rounded       /* Padding & rounding */
```

### Transitions
```css
transition-all duration-300  /* Expand/collapse */
transition-colors           /* Hover states */
```

### Responsive
```css
flex-col sm:flex-row       /* Stack on mobile */
gap-4                      /* Spacing */
```

## Common Patterns

### Highlight Text
```typescript
{highlightedParts.map((part, i) => (
  part.highlight ? (
    <mark className="bg-yellow-200 text-yellow-900" key={i}>
      {part.text}
    </mark>
  ) : (
    <span key={i}>{part.text}</span>
  )
))}
```

### Toggle Expansion
```typescript
const toggleExpanded = (index: number) => {
  const newExpanded = new Set(expandedSources)
  if (newExpanded.has(index)) {
    newExpanded.delete(index)
  } else {
    newExpanded.add(index)
  }
  setExpandedSources(newExpanded)
}
```

### Memoized Filtering
```typescript
const filteredSources = useMemo(() => {
  return sources.filter(s => s.score >= scoreFilter)
}, [sources, scoreFilter])
```

### Memoized Sorting
```typescript
const sortedSources = useMemo(() => {
  const sorted = [...filteredSources]
  switch (sortBy) {
    case 'score-desc': return sorted.sort((a, b) => b.score - a.score)
    case 'score-asc': return sorted.sort((a, b) => a.score - b.score)
    case 'document-asc': return sorted.sort((a, b) =>
      a.metadata.document.localeCompare(b.metadata.document))
    case 'original': return sorted
  }
}, [filteredSources, sortBy])
```

## Integration Example

```typescript
// In App.tsx
const [currentQuery, setCurrentQuery] = useState<string>('')

const handleQuery = async (query: string) => {
  setCurrentQuery(query)  // Store for highlighting
  // ... rest of query logic
}

return (
  <SourcesList
    sources={response.metadata?.sources || []}
    query={currentQuery}
  />
)
```

## File Structure

```
src/
├── components/
│   └── SourcesList.tsx         # Main component (250 lines)
├── utils/
│   └── textHighlight.ts        # Utilities (95 lines)
└── types/
    └── rag.types.ts            # Type definitions

Docs:
├── SOURCES_FEATURES.md         # Comprehensive guide
├── IMPLEMENTATION_SUMMARY.md   # Implementation details
├── VISUAL_GUIDE.md             # UI/UX reference
├── TESTING_GUIDE.md            # Test scenarios
└── QUICK_REFERENCE.md          # This file
```

## Performance Tips

1. **Memoization**: Use `useMemo` for filtering/sorting
2. **Set for Expansion**: O(1) lookup vs array O(n)
3. **CSS Transitions**: GPU-accelerated animations
4. **Conditional Render**: Only render expanded content when needed

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No highlights | Check `query` prop is passed |
| Expand not working | Verify content >300 chars |
| Filter not updating | Check state updates |
| Sort not working | Verify score values are numbers |

## Browser Support

| Browser | Version | Status |
|---------|---------|--------|
| Chrome | 90+ | ✅ Supported |
| Firefox | 88+ | ✅ Supported |
| Safari | 14+ | ✅ Supported |
| Edge | 90+ | ✅ Supported |

## Accessibility

- ✅ ARIA labels on all controls
- ✅ Keyboard navigation (Tab, Enter, Space)
- ✅ Screen reader announcements
- ✅ Semantic HTML (`<mark>`, `<select>`, `<button>`)
- ✅ Focus indicators visible

## Build Info

```bash
# Type check & build
npm run build

# Output
✓ TypeScript compiled
✓ Vite build: 370.58 kB (123.28 kB gzip)
✓ Build time: ~3.5s
```

## Dependencies

**None added!** Uses existing:
- React (hooks: `useState`, `useMemo`)
- Lucide React (icons)
- Tailwind CSS (styling)

## Links

- Full Documentation: `SOURCES_FEATURES.md`
- Visual Guide: `VISUAL_GUIDE.md`
- Testing Guide: `TESTING_GUIDE.md`
- Implementation Summary: `IMPLEMENTATION_SUMMARY.md`

---

**Quick Start:** Pass `query` prop → Get highlights, expand/collapse, sort, and filter! 🚀
