import { useState, useRef, useEffect, useCallback } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import type { Source } from '@/lib/markdown';

interface KnowledgePanelProps {
  currentSources: Source[];
}

const BADGE_STYLES: Record<string, string> = {
  'Bệnh viện K': 'bg-red-500/15 text-red-400 border-red-500/25',
  'Tâm Anh': 'bg-cyan/15 text-cyan border-cyan/25',
  'Vinmec': 'bg-emerald-500/15 text-emerald-400 border-emerald-500/25',
  'Bạch Mai': 'bg-violet/15 text-violet border-violet/25',
  'Bộ Y tế': 'bg-amber/15 text-amber border-amber/25',
};

function getBadgeStyle(sourceName: string): string {
  for (const [key, style] of Object.entries(BADGE_STYLES)) {
    if (sourceName.includes(key)) return style;
  }
  return 'bg-cyan/15 text-cyan border-cyan/25';
}

interface AllSource {
  id: number;
  source: string;
  url: string;
  title: string;
  section_title: string;
}

export function KnowledgePanel({ currentSources }: KnowledgePanelProps) {
  const [activeImage, setActiveImage] = useState<{ src: string; alt: string } | null>(null);
  const [allSources, setAllSources] = useState<AllSource[]>([]);
  const [activeTab, setActiveTab] = useState('references');
  const sourceRefs = useRef<Map<number, HTMLDivElement>>(new Map());

  useEffect(() => {
    fetch('/api/sources')
      .then((res) => res.json())
      .then((data) => setAllSources(data))
      .catch(() => setAllSources([]));
  }, []);

  // Switch to references tab when new sources arrive
  useEffect(() => {
    if (currentSources.length > 0) {
      setActiveTab('references');
    }
  }, [currentSources]);

  // Handle citation click from chat messages
  const handleCitationClick = useCallback(
    (e: MouseEvent) => {
      const link = (e.target as HTMLElement).closest('.citation-link');
      if (!link) return;

      const href = link.getAttribute('href');
      if (href === '#') e.preventDefault();

      const citationIdx = parseInt(link.getAttribute('data-citation') || '0') - 1;
      if (citationIdx >= 0 && citationIdx < currentSources.length) {
        setActiveTab('references');
        const refEl = sourceRefs.current.get(citationIdx);
        if (refEl) {
          refEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
          refEl.classList.remove('animate-flash');
          void refEl.offsetWidth; // Trigger reflow
          refEl.classList.add('animate-flash');
        }
      }
    },
    [currentSources]
  );

  useEffect(() => {
    document.addEventListener('click', handleCitationClick);
    return () => document.removeEventListener('click', handleCitationClick);
  }, [handleCitationClick]);

  return (
    <div className="glass rounded-2xl flex flex-col min-h-0 overflow-hidden border-t-2 border-t-violet/40 h-full">
      {/* Header */}
      <div className="px-6 py-4 border-b border-border/50 bg-background/40 backdrop-blur-md">
        <h2 className="font-heading font-bold text-base tracking-wide text-violet flex items-center gap-2">
          <span>📖</span> Cơ sở dữ liệu Y khoa
        </h2>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="flex flex-col flex-1 min-h-0">
        <TabsList className="w-full rounded-none border-b border-border/50 bg-background/40 h-auto p-0 flex">
          <TabsTrigger
            value="references"
            className="flex-1 rounded-none border-b-2 border-transparent data-[state=active]:border-cyan data-[state=active]:text-cyan data-[state=active]:bg-cyan/5 data-[state=active]:shadow-none font-heading font-bold text-xs py-3.5 tracking-wider uppercase transition-all duration-300"
          >
            Tài liệu tham khảo
          </TabsTrigger>
          <TabsTrigger
            value="database"
            className="flex-1 rounded-none border-b-2 border-transparent data-[state=active]:border-violet data-[state=active]:text-violet data-[state=active]:bg-violet/5 data-[state=active]:shadow-none font-heading font-bold text-xs py-3.5 tracking-wider uppercase transition-all duration-300"
          >
            Nguồn dữ liệu
          </TabsTrigger>
        </TabsList>

        {/* References Tab */}
        <TabsContent value="references" className="flex-1 m-0 min-h-0 overflow-y-auto p-5">
          {currentSources.length === 0 ? (
                <div className="flex flex-col items-center justify-center text-center py-20 px-4">
                  <div className="relative mb-6">
                    <div className="absolute inset-0 rounded-full bg-cyan/10 blur-xl animate-pulse" />
                    <div className="w-16 h-16 rounded-2xl bg-cyan/10 border border-cyan/35 flex items-center justify-center text-3xl shadow-[0_0_20px_oklch(0.715_0.143_215_/_0.2)] animate-breathe relative z-10 select-none">
                      📚
                    </div>
                  </div>
                  <h3 className="font-heading font-bold text-base text-foreground mb-2">Đang chờ câu hỏi...</h3>
                  <p className="text-xs text-muted-foreground max-w-[280px] leading-relaxed">
                    Khi bạn hỏi trợ lý, các tài liệu đối chiếu y tế được sử dụng để lập luận câu trả lời sẽ tự động xuất hiện tại đây.
                  </p>
                </div>
              ) : (
                <div className="flex flex-col gap-4">
                  {currentSources.map((src, idx) => (
                    <Card
                      key={`ref-${src.id}-${idx}`}
                      ref={(el) => {
                        if (el) sourceRefs.current.set(idx, el);
                      }}
                      className={cn(
                        'p-4 bg-white/[0.02] border-white/[0.06] border-l-4 border-l-cyan/60 transition-all duration-300 relative overflow-hidden',
                        'hover:border-l-cyan hover:-translate-y-0.5 hover:shadow-[0_8px_25px_oklch(0.715_0.143_215_/_0.15)]'
                      )}
                    >
                      {/* Top shine line */}
                      <div className="absolute top-0 inset-x-0 h-[1px] bg-gradient-to-r from-transparent via-cyan/20 to-transparent" />
                      
                      <div className="flex items-center justify-between gap-2 mb-2 flex-wrap">
                        <Badge variant="outline" className={cn('text-[0.68rem] font-bold px-2 py-0.5 rounded-md', getBadgeStyle(src.source))}>
                          {src.source}
                        </Badge>
                        <Badge className="bg-gradient-to-r from-cyan to-teal text-background border-none text-[0.68rem] font-bold px-2 py-0.5 rounded-md shadow-[0_2px_6px_oklch(0.715_0.143_215_/_0.25)]">
                          Tài liệu [{idx + 1}]
                        </Badge>
                      </div>
                      <h4 className="font-heading font-bold text-sm text-foreground mb-1 leading-snug tracking-wide">
                        {src.title}
                      </h4>
                      <p className="text-xs text-cyan font-semibold mb-2">
                        Phần đối chiếu: {src.section_title}
                      </p>
                      {src.snippet && (
                        <p className="text-xs text-muted-foreground italic border-l-2 border-violet/30 pl-2.5 mb-3 leading-relaxed">
                          "{src.snippet}"
                        </p>
                      )}
                      <a
                        href={src.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-cyan font-bold hover:text-foreground transition-colors inline-flex items-center gap-1 cursor-pointer"
                      >
                        Xem bài gốc 🔗
                      </a>
                    </Card>
                  ))}
                </div>
              )}
        </TabsContent>

        {/* Database Tab */}
        <TabsContent value="database" className="flex-1 m-0 min-h-0 overflow-y-auto p-5">
          <Card className="p-4 bg-white/[0.02] border-white/[0.06] border-l-4 border-l-violet/60 mb-5 relative overflow-hidden">
                <div className="absolute top-0 inset-x-0 h-[1px] bg-gradient-to-r from-transparent via-violet/20 to-transparent" />
                <p className="text-xs text-muted-foreground leading-relaxed mb-3 font-medium">
                  Hệ thống đã thu thập dữ liệu từ <strong className="text-foreground font-semibold">4 nguồn y tế lớn</strong> với tổng cộng{' '}
                  <strong className="text-violet font-extrabold">{allSources.length}</strong> phân đoạn dữ liệu:
                </p>
                <div className="flex gap-2 flex-wrap">
                  {['Bệnh viện K', 'Bệnh viện Tâm Anh', 'Vinmec', 'Bộ Y tế'].map((name) => (
                    <Badge key={name} variant="outline" className={cn('text-[0.68rem] font-bold px-2 py-0.5 rounded-md', getBadgeStyle(name))}>
                      {name}
                    </Badge>
                  ))}
                </div>
              </Card>

              {/* R Analysis Visualizations */}
              <div className="flex flex-col gap-3 mb-5">
                <div className="rounded-xl border border-white/10 bg-white/[0.01] p-3 backdrop-blur-md flex flex-col gap-3">
                  <div className="flex justify-between items-center px-1">
                    <span className="text-xs font-bold text-cyan flex items-center gap-1.5">
                      <span className="h-2 w-2 rounded-full bg-cyan animate-pulse" />
                      Thống kê Cơ sở dữ liệu (R Lang + ggplot2)
                    </span>
                    <Badge variant="outline" className="text-[0.6rem] border-cyan/30 text-cyan/90 font-mono">
                      v1.0.0
                    </Badge>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div
                      className="rounded-lg overflow-hidden border border-white/[0.05] bg-black/25 p-1.5 shadow-inner cursor-zoom-in hover:border-cyan/30 hover:bg-black/40 transition-all duration-300"
                      onClick={() =>
                        setActiveImage({
                          src: '/static/sources_plot.png',
                          alt: 'Biểu đồ phân bố nguồn tài liệu y khoa',
                        })
                      }
                    >
                      <img
                        src="/static/sources_plot.png"
                        alt="Biểu đồ phân bố nguồn tài liệu y khoa"
                        className="w-full h-auto rounded-md object-contain hover:scale-[1.02] transition-transform duration-300"
                      />
                    </div>
                    <div
                      className="rounded-lg overflow-hidden border border-white/[0.05] bg-black/25 p-1.5 shadow-inner cursor-zoom-in hover:border-cyan/30 hover:bg-black/40 transition-all duration-300"
                      onClick={() =>
                        setActiveImage({
                          src: '/static/wordcount_plot.png',
                          alt: 'Biểu đồ độ dài trung bình phân đoạn',
                        })
                      }
                    >
                      <img
                        src="/static/wordcount_plot.png"
                        alt="Biểu đồ độ dài trung bình phân đoạn"
                        className="w-full h-auto rounded-md object-contain hover:scale-[1.02] transition-transform duration-300"
                      />
                    </div>
                    <div
                      className="rounded-lg overflow-hidden border border-white/[0.05] bg-black/25 p-1.5 shadow-inner cursor-zoom-in hover:border-cyan/30 hover:bg-black/40 transition-all duration-300"
                      onClick={() =>
                        setActiveImage({
                          src: '/static/keywords_plot.png',
                          alt: 'Biểu đồ tần suất xuất hiện từ khóa',
                        })
                      }
                    >
                      <img
                        src="/static/keywords_plot.png"
                        alt="Biểu đồ tần suất xuất hiện từ khóa"
                        className="w-full h-auto rounded-md object-contain hover:scale-[1.02] transition-transform duration-300"
                      />
                    </div>
                    <div
                      className="rounded-lg overflow-hidden border border-white/[0.05] bg-black/25 p-1.5 shadow-inner cursor-zoom-in hover:border-cyan/30 hover:bg-black/40 transition-all duration-300"
                      onClick={() =>
                        setActiveImage({
                          src: '/static/density_plot.png',
                          alt: 'Biểu đồ mật độ phân bố độ dài phân đoạn',
                        })
                      }
                    >
                      <img
                        src="/static/density_plot.png"
                        alt="Biểu đồ mật độ phân bố độ dài phân đoạn"
                        className="w-full h-auto rounded-md object-contain hover:scale-[1.02] transition-transform duration-300"
                      />
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex flex-col gap-4">
                {allSources.map((src) => (
                  <Card
                    key={`all-${src.id}`}
                    className={cn(
                      'p-4 bg-white/[0.02] border-white/[0.06] border-l-4 border-l-violet/50 transition-all duration-300 relative overflow-hidden',
                      'hover:border-l-violet hover:-translate-y-0.5 hover:shadow-[0_8px_25px_oklch(0.606_0.25_292_/_0.15)]'
                    )}
                  >
                    <div className="flex items-center justify-between gap-2 mb-2 flex-wrap">
                      <Badge variant="outline" className={cn('text-[0.68rem] font-bold px-2 py-0.5 rounded-md', getBadgeStyle(src.source))}>
                        {src.source}
                      </Badge>
                      <span className="text-[0.68rem] text-muted-foreground font-mono font-medium">ID: #{src.id}</span>
                    </div>
                    <h4 className="font-heading font-bold text-sm text-foreground mb-1 leading-snug tracking-wide">
                      {src.title}
                    </h4>
                    <p className="text-xs text-violet font-semibold mb-2">
                      Mục: {src.section_title}
                    </p>
                    <a
                      href={src.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-violet font-bold hover:text-foreground transition-colors inline-flex items-center gap-1 cursor-pointer"
                    >
                      Xem bài gốc 🔗
                    </a>
                  </Card>
                ))}
              </div>
        </TabsContent>
      </Tabs>

      {/* Lightbox Modal for zooming charts */}
      {activeImage && (
        <div
          className="fixed inset-0 z-[100] flex items-center justify-center bg-black/85 backdrop-blur-md p-4 animate-fade-in cursor-zoom-out"
          onClick={() => setActiveImage(null)}
        >
          <div className="relative max-w-4xl w-full max-h-[90vh] flex flex-col items-center animate-scale-up">
            <button
              className="absolute -top-12 right-0 text-white/80 hover:text-white bg-white/10 hover:bg-white/20 rounded-full p-2 transition-colors cursor-pointer"
              onClick={(e) => {
                e.stopPropagation();
                setActiveImage(null);
              }}
              aria-label="Đóng"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth={2.5}
                className="size-6"
              >
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
              </svg>
            </button>
            <img
              src={activeImage.src}
              alt={activeImage.alt}
              className="w-auto h-auto max-w-full max-h-[80vh] rounded-xl border border-white/10 shadow-2xl object-contain"
              onClick={(e) => e.stopPropagation()}
            />
            <p className="text-sm font-semibold text-white/90 mt-4 bg-black/40 px-4 py-1.5 rounded-full backdrop-blur-sm border border-white/5">
              {activeImage.alt}
            </p>
          </div>
        </div>
      )}

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        @keyframes scaleUp {
          from { transform: scale(0.95); opacity: 0; }
          to { transform: scale(1); opacity: 1; }
        }
        .animate-fade-in {
          animation: fadeIn 0.15s ease-out forwards;
        }
        .animate-scale-up {
          animation: scaleUp 0.2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }
      `}</style>
    </div>
  );
}
