import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { cn } from '@/lib/utils';
import { parseMarkdown } from '@/lib/markdown';
import type { Source } from '@/lib/markdown';
import type { Message } from '@/hooks/useChat';

interface MessageBubbleProps {
  message: Message;
  sources: Source[];
  isStreaming?: boolean;
}

function TypingIndicator() {
  return (
    <div className="flex gap-2 items-center px-2 py-1">
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          className="w-2 h-2 rounded-full bg-cyan shadow-[0_0_8px_oklch(0.715_0.143_215_/_0.5)]"
          style={{
            animation: 'bounce-dot 1.4s infinite ease-in-out both',
            animationDelay: `${-0.32 + i * 0.16}s`,
          }}
        />
      ))}
    </div>
  );
}

export default function MessageBubble({
  message,
  sources,
  isStreaming = false,
}: MessageBubbleProps) {
  const isUser = message.role === 'user';

  return (
    <div
      className={cn(
        'animate-slide-in flex gap-4 max-w-[85%] group',
        isUser ? 'self-end flex-row-reverse' : 'self-start'
      )}
    >
      {/* Avatar */}
      <Avatar className={cn(
        'border shrink-0 h-10 w-10 shadow-md transition-transform duration-300 group-hover:scale-105',
        isUser
          ? 'bg-cyan/15 border-cyan/35'
          : 'bg-violet/10 border-violet/30'
      )}>
        <AvatarFallback
          className={cn(
            'text-lg select-none',
            isUser ? 'bg-cyan/10' : 'bg-violet/10'
          )}
        >
          {isUser ? '👤' : '🫁'}
        </AvatarFallback>
      </Avatar>

      {/* Content bubble */}
      <div
        className={cn(
          'rounded-2xl border px-5 py-3.5 text-sm shadow-lg backdrop-blur-md transition-all duration-300 relative',
          isUser
            ? 'bg-gradient-to-br from-cyan/12 to-teal/8 border-cyan/30 rounded-tr-sm text-cyan-50 hover:border-cyan/45'
            : 'bg-white/[0.02] border-white/[0.06] rounded-tl-sm border-l-4 border-l-cyan/50 hover:border-l-cyan/80'
        )}
      >
        {isStreaming && !message.content ? (
          <TypingIndicator />
        ) : (
          <div
            className="markdown-content max-w-none font-sans"
            dangerouslySetInnerHTML={{
              __html: parseMarkdown(message.content, sources),
            }}
          />
        )}
      </div>
    </div>
  );
}
