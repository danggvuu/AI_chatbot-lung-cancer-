import { Button } from '@/components/ui/button';

interface WarningBannerProps {
  onClose: () => void;
}

export function WarningBanner({ onClose }: WarningBannerProps) {
  return (
    <div className="mx-auto max-w-[1600px] w-full px-4 pt-4 shrink-0">
      <div className="animate-slide-in rounded-2xl border border-amber-500/20 bg-amber-500/5 text-amber-200 px-5 py-3.5 flex items-center justify-between gap-4 shadow-[0_8px_32px_0_oklch(0.769_0.188_70.08_/_0.15)] backdrop-blur-md relative overflow-hidden">
        <div className="absolute top-0 left-0 bottom-0 w-1 bg-amber-500/80" />
        <div className="flex items-center gap-3">
          <span className="text-xl animate-pulse flex-shrink-0">⚠️</span>
          <p className="text-sm leading-relaxed font-sans font-medium">
            <strong className="font-extrabold tracking-wide text-amber-400">KHUYẾN CÁO Y KHOA:</strong>{' '}
            Nếu bạn hoặc người thân có triệu chứng ho kéo dài trên 3 tuần, ho ra máu, khó thở hoặc đau ngực không rõ nguyên nhân, hãy đến ngay cơ sở y tế chuyên khoa để khám sàng lọc sớm.
          </p>
        </div>
        <Button
          variant="ghost"
          size="icon"
          onClick={onClose}
          className="text-amber-300/80 hover:text-amber-200 hover:bg-amber-500/10 rounded-full flex-shrink-0 h-8 w-8 transition-colors"
          aria-label="Đóng khuyến cáo"
        >
          ✕
        </Button>
      </div>
    </div>
  );
}
