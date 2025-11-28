# SourcesList Visual Guide

## UI Layout

```
┌────────────────────────────────────────────────────────────────────────┐
│ Retrieved Sources                                    3 of 5 chunks     │
│                                                                         │
│  [↕] Sort: [Best Match ▼]  [All] [Low] [Med] [High]                  │
│                              ↑     ↑     ↑     ↑                       │
│                           Active filters (pills)                       │
└────────────────────────────────────────────────────────────────────────┘
```

## Source Card (Collapsed)

```
┌────────────────────────────────────────────────────────────────────────┐
│ document.pdf  Page 3                                     [85.2%] ▲     │
│ chunk-001                                                              │
│                                                                         │
│ This is the content preview showing only the first 200 characters      │
│ of the source chunk. The user's query terms like "telefone" and       │
│ "empresa" are highlighted in yellow...                                │
│                                                                         │
│ [Show more ↓]                                                          │
└────────────────────────────────────────────────────────────────────────┘
```

## Source Card (Expanded)

```
┌────────────────────────────────────────────────────────────────────────┐
│ document.pdf  Page 3                                     [85.2%] ▲     │
│ chunk-001                                                              │
│ ┌──────────────────────────────────────────────────────────────────┐  │
│ │ This is the complete content of the source chunk with all text   │  │
│ │ visible. The user's query terms like "telefone" and "empresa"    │  │
│ │ are highlighted in yellow throughout the entire content.         │  │
│ │                                                                   │  │
│ │ Additional paragraphs and information continue here with proper  │  │
│ │ formatting and readability...                                    │  │
│ └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│ [Show less ↑]                                                          │
└────────────────────────────────────────────────────────────────────────┘
```

## Highlight Example

```
Query: "telefone da empresa"

Source content:
"Para contato, ligue no telefone (11) 1234-5678 ou envie email para a empresa."

Rendered with highlights:
"Para contato, ligue no [telefone] (11) 1234-5678 ou envie email para a [empresa]."
                         └─────┘                                        └────┘
                         Yellow highlight                              Yellow highlight
```

## Filter States

### All Sources (Default)
```
[All*] [Low] [Med] [High]
  ↑
Active

"5 chunks"
```

### High Confidence Only
```
[All] [Low] [Med] [High*]
                    ↑
                  Active

"2 of 5 chunks"
```

### No Matches (Empty State)
```
[All] [Low] [Med] [High*]

┌─────────────────────────────────┐
│                                 │
│ No sources match current filter │
│                                 │
│       [Clear filter]            │
│                                 │
└─────────────────────────────────┘
```

## Sort Dropdown

```
┌──────────────────────────┐
│ [↕] Sort: Best Match ▼   │
│  ┌───────────────────┐   │
│  │ Best Match ✓      │   │
│  │ Lowest Match      │   │
│  │ Document Name     │   │
│  │ Original Order    │   │
│  └───────────────────┘   │
└──────────────────────────┘
```

## Score Badge Colors

### High Score (>80%)
```
┌──────────┐
│ ▲ 85.2% │  Green background
└──────────┘  (bg-green-50 text-green-600)
```

### Medium Score (60-80%)
```
┌──────────┐
│ ▲ 67.3% │  Yellow background
└──────────┘  (bg-yellow-50 text-yellow-600)
```

### Low Score (<60%)
```
┌──────────┐
│ ▲ 45.8% │  Orange background
└──────────┘  (bg-orange-50 text-orange-600)
```

## Mobile Layout (< 640px)

```
┌────────────────────────────────┐
│ Retrieved Sources              │
│ 3 of 5 chunks                  │
│                                │
│ [↕] Sort: [Best Match ▼]      │
│                                │
│ [All] [Low] [Med] [High]       │
│                                │
│ ┌──────────────────────────┐  │
│ │ Source Card 1            │  │
│ └──────────────────────────┘  │
│                                │
│ ┌──────────────────────────┐  │
│ │ Source Card 2            │  │
│ └──────────────────────────┘  │
└────────────────────────────────┘
```

## Interaction Flows

### Flow 1: Exploring Sources
```
1. User submits query: "telefone da empresa"
   ↓
2. Sources load with highlights on "telefone" and "empresa"
   ↓
3. User clicks "High (>80%)" filter
   ↓
4. List updates to show only 2 of 5 chunks
   ↓
5. User clicks "Show more" on first source
   ↓
6. Source expands with smooth transition
   ↓
7. User reads full content with highlights
   ↓
8. User clicks "Show less" to collapse
```

### Flow 2: Sorting Analysis
```
1. Sources display in "Best Match" order (default)
   ↓
2. User opens sort dropdown
   ↓
3. User selects "Document Name"
   ↓
4. Sources reorder alphabetically by document
   ↓
5. User identifies pattern in document organization
   ↓
6. User switches to "Lowest Match" to see edge cases
```

### Flow 3: Finding Specific Content
```
1. User sees 5 sources (overwhelming)
   ↓
2. User clicks "High (>80%)" filter
   ↓
3. Only 2 high-confidence sources remain
   ↓
4. User expands first source
   ↓
5. Highlighted terms immediately visible
   ↓
6. User finds relevant information quickly
```

## Accessibility Features

### Keyboard Navigation
```
Tab Order:
1. Sort dropdown
2. Filter pill: All
3. Filter pill: Low
4. Filter pill: Medium
5. Filter pill: High
6. Source card 1: Expand button (if long)
7. Source card 2: Expand button (if long)
...

Enter/Space: Activate focused element
Arrow Keys: Navigate dropdown options
```

### Screen Reader Announcements
```
Sort dropdown:
"Sort sources, dropdown menu, Best Match selected"

Filter pill:
"Filter by All, button, pressed"

Expand button:
"Show more, button"

Source card:
"Retrieved source from document.pdf, page 3, score 85.2%"
```

## Color Palette Reference

```
Highlights:
bg-yellow-200      #FEF08A  (Light yellow)
text-yellow-900    #713F12  (Dark yellow-brown)

Primary (Active):
bg-primary-500     #3B82F6  (Blue)
text-white         #FFFFFF

Inactive:
bg-gray-100        #F3F4F6  (Light gray)
text-gray-600      #4B5563  (Medium gray)

Score Colors:
High:   bg-green-50  text-green-600   (#F0FDF4 / #16A34A)
Medium: bg-yellow-50 text-yellow-600  (#FEFCE8 / #CA8A04)
Low:    bg-orange-50 text-orange-600  (#FFF7ED / #EA580C)
```

## Animation Timings

```
Expand/Collapse: 300ms ease-in-out
Hover states:    150ms ease
Filter change:   Instant (no animation)
Sort change:     Instant (no animation)
Border colors:   200ms ease
```

## Responsive Breakpoints

```
Mobile:  < 640px  (sm)
Tablet:  640px+   (sm+)
Desktop: 1024px+  (lg+)

Changes at mobile:
- Stacked controls (column layout)
- Full-width filter pills
- Compact sort dropdown
```

## Example Queries & Results

### Query 1: "telefone contato"
```
Highlights: "telefone", "contato"
Stopwords: (none)
Result: Both terms highlighted throughout sources
```

### Query 2: "qual é o telefone da empresa"
```
Highlights: "telefone", "empresa"
Stopwords: "qual", "é", "o", "da" (filtered out)
Result: Only meaningful terms highlighted
```

### Query 3: "authentication OAuth token"
```
Highlights: "authentication", "OAuth", "token"
Stopwords: (none - English terms pass through)
Result: All three terms highlighted
```

## Edge Cases

### No Highlights (All Stopwords)
```
Query: "o a de para"
Highlights: (none)
Result: Content displayed normally without highlights
```

### Very Short Source (<300 chars)
```
Content: "Brief content here."
Result: No expand/collapse button shown
Display: Full content always visible
```

### All Sources Filtered Out
```
Filter: High (>80%)
Sources: All below 80%
Result: Empty state with "Clear filter" button
```

### Single Source
```
Sources: 1 chunk
Display: "1 chunk" (singular)
Filter: All filters still available
```

## Performance Indicators

```
Fast Operations (< 10ms):
- Expand/collapse toggle
- Filter pill click
- Sort dropdown change

Moderate Operations (10-50ms):
- Initial render (5 sources)
- Highlight computation
- Re-sort large lists

No Lag:
- Smooth 60fps transitions
- Instant visual feedback
- No layout shifts
```
