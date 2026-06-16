export interface Source {
  id: number;
  source: string;
  url: string;
  title: string;
  section_title: string;
  snippet?: string;
}

/**
 * Escape HTML special characters to prevent XSS.
 */
function escapeHtml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

/**
 * Shorten a Vietnamese source name by stripping common prefixes.
 */
function shortenSource(source: string): string {
  return source
    .replace(/^Bệnh viện\s+/i, '')
    .replace(/^Bộ\s+/i, '');
}

/**
 * Replace citation references like [1], [2] with clickable citation links.
 */
function replaceCitations(html: string, sources: Source[]): string {
  return html.replace(/\[(\d+)\]/g, (_match, num) => {
    const citationIndex = parseInt(num, 10) - 1;
    const source = sources[citationIndex];
    if (source) {
      const short = shortenSource(source.source);
      return `<a href="${escapeHtml(source.url)}" target="_blank" rel="noopener" class="citation-link" data-citation="${num}">[${num} - ${escapeHtml(short)}]</a>`;
    }
    return `<a href="#" class="citation-link" data-citation="${num}">[${num}]</a>`;
  });
}

/**
 * Convert inline markdown (bold and italic) to HTML.
 */
function convertInlineFormatting(text: string): string {
  // Bold: **text** (must run before italic to avoid conflicts)
  let result = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  // Italic: *text* (but not inside <strong> tags — we match single * not preceded/followed by *)
  result = result.replace(/(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)/g, '<em>$1</em>');
  return result;
}

/**
 * Process a single block of text (paragraph-level).
 * Handles lists, blockquotes, and plain paragraphs.
 */
function processBlock(block: string, sources: Source[]): string {
  const lines = block.split('\n');

  // Check if this block is a list (all non-empty lines start with - or *)
  const nonEmptyLines = lines.filter((l) => l.trim().length > 0);
  const isList = nonEmptyLines.length > 0 && nonEmptyLines.every((l) => /^\s*[-*]\s+/.test(l));

  if (isList) {
    const items = nonEmptyLines.map((line) => {
      const content = line.replace(/^\s*[-*]\s+/, '');
      return `<li>${replaceCitations(convertInlineFormatting(content), sources)}</li>`;
    });
    return `<ul>${items.join('')}</ul>`;
  }

  // Check if this block is a blockquote (all non-empty lines start with >)
  const isBlockquote = nonEmptyLines.length > 0 && nonEmptyLines.every((l) => /^\s*>\s?/.test(l));

  if (isBlockquote) {
    const content = nonEmptyLines
      .map((line) => line.replace(/^\s*>\s?/, ''))
      .join('<br>');
    return `<blockquote>${replaceCitations(convertInlineFormatting(content), sources)}</blockquote>`;
  }

  // Regular paragraph: convert single newlines to <br>
  const content = lines
    .map((line) => replaceCitations(convertInlineFormatting(line), sources))
    .join('<br>');
  return `<p>${content}</p>`;
}

/**
 * Parse a subset of markdown into HTML with citation support.
 *
 * Supported syntax:
 * - **bold** → <strong>
 * - *italic* → <em>
 * - [N] → citation link pill
 * - Lines starting with `- ` or `* ` → <ul><li>
 * - Lines starting with `> ` → <blockquote>
 * - Double newlines → paragraph breaks
 * - Single newlines → <br>
 */
export function parseMarkdown(text: string, sources: Source[]): string {
  // First escape HTML in the raw text
  const escaped = escapeHtml(text);

  // Split into blocks by double newlines
  const blocks = escaped.split(/\n\n+/);

  // Process each block
  return blocks
    .map((block) => block.trim())
    .filter((block) => block.length > 0)
    .map((block) => processBlock(block, sources))
    .join('');
}
