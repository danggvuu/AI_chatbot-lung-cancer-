import { useState } from 'react';
import { TooltipProvider } from '@/components/ui/tooltip';
import { Sheet, SheetContent, SheetTrigger, SheetTitle } from '@/components/ui/sheet';
import { Button } from '@/components/ui/button';
import Header from '@/components/Header';
import ChatPanel from '@/components/ChatPanel';
import { KnowledgePanel } from '@/components/KnowledgePanel';
import { WarningBanner } from '@/components/WarningBanner';
import { useChat } from '@/hooks/useChat';
import { useHealth } from '@/hooks/useHealth';

function App() {
  const { messages, currentSources, isGenerating, sendMessage, stopGeneration } = useChat();
  const health = useHealth();
  const [showBanner, setShowBanner] = useState(true);

  return (
    <TooltipProvider>
      <div className="h-screen flex flex-col relative overflow-hidden">
        {/* Glowing Decorative Orbs */}
        <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-cyan/8 rounded-full blur-[130px] pointer-events-none -z-10 animate-float" />
        <div className="absolute bottom-1/3 right-1/4 w-[600px] h-[600px] bg-violet/8 rounded-full blur-[140px] pointer-events-none -z-10 animate-float-delayed" />
        <div className="absolute top-1/2 left-2/3 w-[350px] h-[350px] bg-teal/6 rounded-full blur-[100px] pointer-events-none -z-10" />

        {/* Warning Banner */}
        {showBanner && <WarningBanner onClose={() => setShowBanner(false)} />}

        {/* Main App Container */}
        <div className="flex-1 flex flex-col p-4 gap-4 max-w-[1600px] mx-auto w-full min-h-0 relative z-10">
          {/* Header */}
          <Header
            isOnline={health.isOnline}
            isLoading={health.isLoading}
            modelName={health.modelName}
          />

          {/* Desktop: 2-column layout */}
          <main className="flex-1 grid grid-cols-1 lg:grid-cols-[3fr_2fr] gap-4 min-h-0">
            {/* Chat Panel */}
            <ChatPanel
              messages={messages}
              currentSources={currentSources}
              isGenerating={isGenerating}
              onSendMessage={sendMessage}
              onStopGeneration={stopGeneration}
            />

            {/* Knowledge Panel - Desktop */}
            <div className="hidden lg:flex flex-col min-h-0">
              <KnowledgePanel currentSources={currentSources} />
            </div>

            {/* Knowledge Panel - Mobile (Sheet) */}
            <div className="lg:hidden fixed bottom-4 right-4 z-50">
              <Sheet>
                <SheetTrigger
                  render={
                    <Button
                      size="lg"
                      className="rounded-full shadow-lg bg-cyan text-background hover:bg-cyan/90 h-14 w-14 p-0"
                    >
                      <span className="text-xl">📖</span>
                    </Button>
                  }
                />
                <SheetContent side="right" className="w-[90vw] sm:w-[400px] p-0 bg-background border-border/50">
                  <SheetTitle className="sr-only">Cơ sở dữ liệu Y khoa</SheetTitle>
                  <div className="h-full">
                    <KnowledgePanel currentSources={currentSources} />
                  </div>
                </SheetContent>
              </Sheet>
            </div>
          </main>

          {/* Footer */}
          <footer className="text-center py-3 text-xs text-muted-foreground border-t border-border/30">
            <p>
              © 2026 LungCare AI. Dữ liệu được thu thập từ{' '}
              <a href="https://benhvienk.vn" target="_blank" rel="noopener noreferrer" className="text-cyan hover:text-foreground transition-colors">
                Bệnh viện K
              </a>,{' '}
              <a href="https://tamanhhospital.vn" target="_blank" rel="noopener noreferrer" className="text-cyan hover:text-foreground transition-colors">
                Tâm Anh
              </a>,{' '}
              <a href="https://www.vinmec.com" target="_blank" rel="noopener noreferrer" className="text-cyan hover:text-foreground transition-colors">
                Vinmec
              </a> &amp;{' '}
              <a href="https://kcb.vn" target="_blank" rel="noopener noreferrer" className="text-cyan hover:text-foreground transition-colors">
                Bộ Y tế
              </a>.
            </p>
          </footer>
        </div>
      </div>
    </TooltipProvider>
  );
}

export default App;
