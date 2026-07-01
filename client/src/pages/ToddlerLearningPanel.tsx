import { useCallback, useEffect } from "react";
import { NeonPanel, NeonShell } from "@/components/NeonShell";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useBackend } from "@/contexts/BackendContext";
import { useToddlerLearning } from "@/hooks/useToddlerLearning";
import { Baby, Heart, RefreshCw, Sparkles } from "lucide-react";
import { toast } from "sonner";

const STAGE_LABELS: Record<string, string> = {
  infant: "嬰兒期",
  toddler: "學步期",
  preschool: "學前期",
  school: "學齡期",
};

export default function ToddlerLearningPanel() {
  const { online } = useBackend();
  const { busy, status, progress, refresh, runProgress, sendPraise } = useToddlerLearning();

  const load = useCallback(async () => {
    try {
      await refresh();
    } catch {
      toast.error("無法載入幼兒學習狀態");
    }
  }, [refresh]);

  useEffect(() => {
    void load();
  }, [load]);

  const stage = status?.stage ?? "infant";
  const milestones = status?.milestones ?? {};

  return (
    <NeonShell
      title="幼兒教育式學習"
      subtitle="Guardian Ai 由淺入深成長 · Grok 監督"
      badge="Developed by Suckbob | Guardian Ai"
    >
      <div className="grid gap-4 md:grid-cols-2">
        <NeonPanel title="目前階段" icon={Baby}>
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="secondary">{STAGE_LABELS[stage] ?? stage}</Badge>
            {status?.next_stage && (
              <span className="text-sm text-muted-foreground">下一階段：{status.next_stage}</span>
            )}
          </div>
          <p className="mt-3 text-sm text-muted-foreground">
            學習系統設計為類似人類幼兒般逐步成長，初期可能出現錯誤或不準確，請自行判斷生成內容。
          </p>
          <dl className="mt-4 grid grid-cols-2 gap-2 text-sm">
            <dt>正面回饋</dt>
            <dd>{milestones.positive_feedback ?? 0}</dd>
            <dt>品質通過</dt>
            <dd>{milestones.quality_passes ?? 0}</dd>
            <dt>成功率</dt>
            <dd>{((status?.quality_success_rate ?? 0) * 100).toFixed(1)}%</dd>
            <dt>網絡學習</dt>
            <dd>{status?.network_learning_unlocked ? "已解鎖" : "未解鎖"}</dd>
          </dl>
        </NeonPanel>

        <NeonPanel title="Grok 鼓勵與糾正" icon={Sparkles}>
          {progress?.grok && typeof progress.grok === "object" ? (
            <pre className="max-h-48 overflow-auto rounded bg-muted/40 p-2 text-xs">
              {JSON.stringify(progress.grok, null, 2)}
            </pre>
          ) : (
            <p className="text-sm text-muted-foreground">按「Grok 監督」取得最新鼓勵與溫和糾正建議。</p>
          )}
          <div className="mt-4 flex flex-wrap gap-2">
            <Button size="sm" disabled={!online || busy} onClick={() => void runProgress()}>
              <RefreshCw className="mr-1 h-4 w-4" />
              Grok 監督
            </Button>
            <Button
              size="sm"
              variant="outline"
              disabled={!online || busy}
              onClick={() => void sendPraise().then(() => toast.success("已記錄正面鼓勵"))}
            >
              <Heart className="mr-1 h-4 w-4" />
              給予鼓勵
            </Button>
          </div>
        </NeonPanel>
      </div>
    </NeonShell>
  );
}