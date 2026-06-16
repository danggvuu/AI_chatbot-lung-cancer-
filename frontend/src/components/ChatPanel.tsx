import { useEffect, useRef, useState } from 'react';
import { Button } from '@/components/ui/button';
import MessageBubble from '@/components/MessageBubble';
import type { Source } from '@/lib/markdown';
import type { Message } from '@/hooks/useChat';

interface ChatPanelProps {
  messages: Message[];
  currentSources: Source[];
  isGenerating: boolean;
  onSendMessage: (query: string) => void;
  onStopGeneration: () => void;
}

const SUGGESTED_PROMPTS = [
  {
    prompt: 'Triệu chứng nhận biết sớm ung thư phổi là gì?',
    label: 'Triệu chứng sớm ⚠️',
  },
  {
    prompt: 'Ai nên sàng lọc ung thư phổi và phương pháp sàng lọc như thế nào?',
    label: 'Đối tượng sàng lọc 🔍',
  },
  {
    prompt: 'Các phương pháp điều trị ung thư phổi hiện nay là gì?',
    label: 'Phương pháp điều trị 💊',
  },
  {
    prompt: 'Hút thuốc lá ảnh hưởng đến nguy cơ ung thư phổi như thế nào?',
    label: 'Hút thuốc & nguy cơ 🚬',
  },
] as const;

export default function ChatPanel({
  messages,
  currentSources,
  isGenerating,
  onSendMessage,
  onStopGeneration,
}: ChatPanelProps) {
  const [input, setInput] = useState('');
  const bottomRef = useRef<HTMLDivElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom only when user is already at the bottom or sent a new message
  useEffect(() => {
    const container = chatContainerRef.current;
    if (!container) return;

    const lastMessage = messages[messages.length - 1];
    const isUserMessage = lastMessage?.role === 'user';

    const threshold = 150;
    const isAtBottom =
      container.scrollHeight - container.scrollTop - container.clientHeight <= threshold;

    if (isAtBottom || isUserMessage) {
      bottomRef.current?.scrollIntoView({ behavior: isUserMessage ? 'smooth' : 'auto' });
    }
  }, [messages]);

  function handleSubmit() {
    const trimmed = input.trim();
    if (!trimmed || isGenerating) return;
    onSendMessage(trimmed);
    setInput('');
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }

  return (
    <div className="glass rounded-2xl flex flex-col min-h-0 overflow-hidden border-t-2 border-t-cyan/40">
      {/* Panel header */}
      <div className="px-6 py-4 border-b border-border/50 flex justify-between items-center bg-background/40 backdrop-blur-md">
        <h2 className="font-heading font-bold text-base tracking-wide text-cyan flex items-center gap-2">
          <span>💬</span> Trò chuyện với Trợ lý AI
        </h2>
      </div>

      {/* Messages area */}
      <div
        ref={chatContainerRef}
        className="flex-1 overflow-y-auto min-h-0 p-6 flex flex-col gap-5"
      >
        {messages.map((msg) => (
          <MessageBubble
            key={msg.id}
            message={msg}
            sources={currentSources}
            isStreaming={
              isGenerating &&
              msg.role === 'assistant' &&
              msg.id === messages[messages.length - 1]?.id
            }
          />
        ))}
        <div ref={bottomRef} />
      </div>

      {/* Suggested prompts — always visible */}
      <div className="flex gap-2.5 px-6 pb-4 overflow-x-auto scrollbar-none no-scrollbar shrink-0">
        {SUGGESTED_PROMPTS.map(({ prompt, label }) => (
          <Button
            key={label}
            variant="outline"
            size="sm"
            disabled={isGenerating}
            className="rounded-full whitespace-nowrap border-cyan/20 bg-cyan/5 text-cyan hover:bg-cyan/15 hover:border-cyan/40 disabled:opacity-30 disabled:pointer-events-none text-xs py-1.5 px-4 transition-all duration-300 shadow-[0_2px_8px_oklch(0.715_0.143_215_/_0.04)]"
            data-prompt={prompt}
            onClick={() => onSendMessage(prompt)}
          >
            {label}
          </Button>
        ))}
      </div>

      {/* Chat input */}
      <div className="p-4 bg-background/20 border-t border-border/50">
        <div className="flex gap-2 items-center bg-black/30 border border-white/5 rounded-full p-1.5 pl-4 pr-1.5 focus-within:border-cyan/40 focus-within:ring-2 focus-within:ring-cyan/15 transition-all shadow-[inset_0_2px_4px_rgba(0,0,0,0.3)]">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Nhập câu hỏi của bạn về ung thư phổi..."
            disabled={isGenerating}
            className="flex-1 bg-transparent border-0 outline-none text-sm text-foreground placeholder-muted-foreground focus:ring-0 focus:outline-none py-2 mr-2"
          />

          {isGenerating ? (
            <Button
              onClick={onStopGeneration}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/80 rounded-full h-10 w-10 p-0 flex items-center justify-center transition-all shadow-md shrink-0"
              size="icon"
              aria-label="Dừng tạo"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="currentColor"
                className="size-4"
              >
                <rect x="7" y="7" width="10" height="10" rx="1" />
              </svg>
            </Button>
          ) : (
            <Button
              onClick={handleSubmit}
              disabled={!input.trim()}
              className="bg-gradient-to-r from-cyan to-teal text-background hover:scale-105 disabled:opacity-40 disabled:scale-100 rounded-full h-10 w-10 p-0 flex items-center justify-center transition-all shadow-[0_4px_12px_oklch(0.715_0.143_215_/_0.35)] shrink-0 cursor-pointer"
              size="icon"
              aria-label="Gửi tin nhắn"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth={2.5}
                strokeLinecap="round"
                strokeLinejoin="round"
                className="size-4 mr-0.5 mt-0.5"
              >
                <path d="m22 2-7 20-4-9-9-4Z" />
                <path d="M22 2 11 13" />
              </svg>
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
