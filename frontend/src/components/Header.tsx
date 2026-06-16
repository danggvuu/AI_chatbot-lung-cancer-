import { Badge } from '@/components/ui/badge';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { cn } from '@/lib/utils';

interface HeaderProps {
  isOnline: boolean;
  isLoading: boolean;
  modelName: string;
}

function getStatus(isOnline: boolean, isLoading: boolean) {
  if (isLoading) {
    return {
      dotClass: 'bg-amber-500 animate-status-pulse',
      badgeClass: 'border-amber-500/20 bg-amber-500/5 text-amber-300 shadow-[0_0_12px_rgba(245,158,11,0.05)]',
      label: 'Đang kiểm tra...',
    };
  }
  if (isOnline) {
    return {
      dotClass: 'bg-green-500 animate-status-pulse',
      badgeClass: 'border-green-500/30 bg-green-500/10 text-green-400 shadow-[0_0_12px_rgba(34,197,94,0.08)]',
      label: 'Ollama Sẵn Sàng',
    };
  }
  return {
    dotClass: 'bg-red-500',
    badgeClass: 'border-red-500/30 bg-red-500/10 text-red-400 shadow-[0_0_12px_rgba(239,68,68,0.08)]',
    label: 'Mất kết nối',
  };
}

export default function Header({ isOnline, isLoading, modelName }: HeaderProps) {
  const status = getStatus(isOnline, isLoading);

  return (
    <header className="glass rounded-2xl px-6 py-4 flex justify-between items-center relative overflow-hidden border-t-2 border-t-cyan/15">
      {/* Decorative top reflection glare */}
      <div className="absolute top-0 inset-x-0 h-[1px] bg-gradient-to-r from-transparent via-cyan/25 to-transparent" />
      
      {/* Left — Logo */}
      <div className="flex items-center gap-3">
        <span className="text-4xl animate-breathe drop-shadow-[0_0_10px_oklch(0.715_0.143_215_/_0.25)] select-none">🫁</span>
        <div>
          <h1 className="font-heading text-2xl font-extrabold gradient-text tracking-tight">
            LungCare AI
          </h1>
          <p className="text-xs text-muted-foreground font-medium tracking-wide">
            Hệ thống Tư vấn Thông tin Ung thư Phổi
          </p>
        </div>
      </div>

      {/* Right — Connection status */}
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger>
            <div className="flex items-center gap-2.5">
              <Badge variant="outline" className={cn("flex items-center gap-2 px-3.5 py-1.5 rounded-full border text-xs font-semibold backdrop-blur-md transition-all duration-300", status.badgeClass)}>
                <div className={cn('w-2 h-2 rounded-full', status.dotClass)} />
                <span>{status.label}</span>
              </Badge>
              {isOnline && (
                <Badge variant="secondary" className="bg-white/5 border border-white/10 text-muted-foreground px-3 py-1.5 rounded-full text-xs font-mono font-medium hidden sm:inline-flex">
                  Model: {modelName}
                </Badge>
              )}
            </div>
          </TooltipTrigger>
          <TooltipContent side="bottom" className="bg-popover border border-border/50 text-foreground px-3 py-1.5 text-xs rounded-xl shadow-lg backdrop-blur-md">
            <p>Kết nối cục bộ với mô hình ngôn ngữ lớn (LLM) qua Ollama</p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    </header>
  );
}
