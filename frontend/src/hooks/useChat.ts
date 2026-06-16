import { useCallback, useRef, useState } from 'react';
import type { Source } from '@/lib/markdown';

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
}

const WELCOME_MESSAGE: Message = {
  id: 'welcome',
  role: 'assistant',
  content:
    'Xin chào! Tôi là **LungCare AI**, trợ lý ảo hỗ trợ thông tin y khoa về ung thư phổi.\n\n' +
    'Tôi có thể giúp bạn tìm hiểu về:\n' +
    '- Triệu chứng nhận biết sớm ung thư phổi\n' +
    '- Đối tượng nên sàng lọc và phương pháp tầm soát\n' +
    '- Yếu tố nguy cơ, bao gồm hút thuốc lá\n' +
    '- Tổng quan các phương pháp điều trị hiện nay\n\n' +
    '> ⚠️ *Lưu ý: Tôi là trợ lý AI thông tin, không thay thế cho tư vấn y khoa chuyên môn.*',
};

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([WELCOME_MESSAGE]);
  const [currentSources, setCurrentSources] = useState<Source[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);

  const stopGeneration = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
  }, []);

  const sendMessage = useCallback(async (query: string) => {
    const trimmed = query.trim();
    if (!trimmed || isGenerating) return;

    // Add user message
    const userMessage: Message = {
      id: Math.random().toString(36).substring(7),
      role: 'user',
      content: trimmed,
    };
    setMessages((prev) => [...prev, userMessage]);
    setCurrentSources([]);
    setIsGenerating(true);

    // Build conversation history (exclude system messages)
    const conversationHistory = messages
      .filter((msg) => msg.role === 'user' || msg.role === 'assistant')
      .map((msg) => ({ role: msg.role as 'user' | 'assistant', content: msg.content }));
    conversationHistory.push({ role: 'user', content: userMessage.content });

    // Create abort controller
    const controller = new AbortController();
    abortControllerRef.current = controller;

    // Add placeholder assistant message
    const assistantId = Math.random().toString(36).substring(7);
    setMessages((prev) => {
      return [...prev, { id: assistantId, role: 'assistant' as const, content: '' }];
    });

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: conversationHistory, stream: true }),
        signal: controller.signal,
      });

      if (!response.ok) {
        throw new Error(`Lỗi máy chủ: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('Không thể đọc phản hồi từ máy chủ.');
      }

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');

        // Keep the last partial line in the buffer
        buffer = lines.pop() ?? '';

        for (const line of lines) {
          const trimmedLine = line.trim();
          if (!trimmedLine || !trimmedLine.startsWith('data: ')) continue;

          const jsonStr = trimmedLine.slice(6); // Remove "data: "
          if (jsonStr === '[DONE]') continue;

          try {
            const data = JSON.parse(jsonStr) as Record<string, unknown>;

            // Handle sources
            if ('sources' in data && Array.isArray(data.sources)) {
              setCurrentSources(data.sources as Source[]);
            }

            // Handle delta text
            if ('delta' in data && typeof data.delta === 'string') {
              setMessages((prev) => {
                const updated = [...prev];
                const idx = updated.findIndex((msg) => msg.id === assistantId);
                if (idx >= 0) {
                  updated[idx] = {
                    ...updated[idx],
                    content: updated[idx].content + data.delta,
                  };
                }
                return updated;
              });
            }

            // Handle errors from the stream
            if ('error' in data && typeof data.error === 'string') {
              setMessages((prev) => {
                const updated = [...prev];
                const idx = updated.findIndex((msg) => msg.id === assistantId);
                if (idx >= 0) {
                  updated[idx] = {
                    ...updated[idx],
                    content: `⚠️ Lỗi: ${data.error}`,
                  };
                }
                return updated;
              });
            }
          } catch {
            // Skip malformed JSON lines
          }
        }
      }
    } catch (err: unknown) {
      if (err instanceof DOMException && err.name === 'AbortError') {
        // User cancelled — append cancellation notice
        setMessages((prev) => {
          const updated = [...prev];
          const idx = updated.findIndex((msg) => msg.id === assistantId);
          if (idx >= 0) {
            updated[idx] = {
              ...updated[idx],
              content: updated[idx].content + '\n\n*(Bạn đã ngừng tạo phản hồi)*',
            };
          }
          return updated;
        });
      } else {
        // Network or other error
        const errorMessage = err instanceof Error ? err.message : 'Đã xảy ra lỗi không xác định';
        setMessages((prev) => {
          const updated = [...prev];
          const idx = updated.findIndex((msg) => msg.id === assistantId);
          if (idx >= 0) {
            updated[idx] = {
              ...updated[idx],
              content: `⚠️ Không thể kết nối đến máy chủ. Vui lòng thử lại.\n\n_${errorMessage}_`,
            };
          }
          return updated;
        });
      }
    } finally {
      setIsGenerating(false);
      abortControllerRef.current = null;
    }
  }, [messages, isGenerating]);

  return { messages, currentSources, isGenerating, sendMessage, stopGeneration };
}
