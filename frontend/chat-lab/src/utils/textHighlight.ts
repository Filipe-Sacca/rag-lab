/**
 * Text highlighting utilities for search queries
 */

// Portuguese stopwords to ignore when highlighting
const PORTUGUESE_STOPWORDS = new Set([
  'o', 'a', 'os', 'as', 'um', 'uma', 'uns', 'umas',
  'de', 'da', 'do', 'das', 'dos', 'em', 'na', 'no', 'nas', 'nos',
  'para', 'por', 'com', 'sem', 'sob', 'sobre',
  'e', 'ou', 'mas', 'porém', 'contudo',
  'à', 'ao', 'aos', 'às',
  'pelo', 'pela', 'pelos', 'pelas',
  'este', 'esta', 'estes', 'estas', 'esse', 'essa', 'esses', 'essas',
  'isto', 'isso', 'aquilo',
  'eu', 'tu', 'ele', 'ela', 'nós', 'vós', 'eles', 'elas',
  'meu', 'minha', 'meus', 'minhas', 'teu', 'tua', 'teus', 'tuas',
  'seu', 'sua', 'seus', 'suas',
  'que', 'qual', 'quais', 'quanto', 'quanta', 'quantos', 'quantas',
  'quando', 'onde', 'como', 'por que', 'porque',
  'não', 'sim', 'já', 'ainda', 'mais', 'menos',
  'muito', 'pouco', 'todo', 'toda', 'todos', 'todas',
  'outro', 'outra', 'outros', 'outras',
  'também', 'só', 'apenas', 'mesmo', 'mesma'
])

/**
 * Extract meaningful keywords from query (remove stopwords)
 */
export function extractKeywords(query: string): string[] {
  return query
    .toLowerCase()
    .split(/\s+/)
    .filter(word => word.length > 2 && !PORTUGUESE_STOPWORDS.has(word))
}

/**
 * Highlight text matches in content
 * Returns React-friendly array of text and JSX elements
 */
export function highlightText(
  content: string,
  query: string
): Array<{ text: string; highlight: boolean }> {
  if (!query.trim()) {
    return [{ text: content, highlight: false }]
  }

  const keywords = extractKeywords(query)
  if (keywords.length === 0) {
    return [{ text: content, highlight: false }]
  }

  // Create regex pattern with word boundaries for better matching
  const pattern = new RegExp(
    `(${keywords.map(kw => kw.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|')})`,
    'gi'
  )

  const parts: Array<{ text: string; highlight: boolean }> = []
  let lastIndex = 0
  let match: RegExpExecArray | null

  while ((match = pattern.exec(content)) !== null) {
    // Add text before match
    if (match.index > lastIndex) {
      parts.push({
        text: content.substring(lastIndex, match.index),
        highlight: false
      })
    }

    // Add matched text
    parts.push({
      text: match[0],
      highlight: true
    })

    lastIndex = pattern.lastIndex
  }

  // Add remaining text
  if (lastIndex < content.length) {
    parts.push({
      text: content.substring(lastIndex),
      highlight: false
    })
  }

  return parts
}

/**
 * Simple truncate function for collapsed content
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength).trim() + '...'
}
