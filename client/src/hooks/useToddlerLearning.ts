import { useCallback, useState } from "react";
import { monsterFetch } from "@/lib/monsterApi";

export interface ToddlerStatus {
  stage: string;
  milestones: Record<string, number>;
  quality_success_rate: number;
  encouragement_count: number;
  correction_count: number;
  next_stage: string | null;
  network_learning_unlocked: boolean;
}

export function useToddlerLearning() {
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState<ToddlerStatus | null>(null);
  const [progress, setProgress] = useState<Record<string, unknown> | null>(null);

  const refresh = useCallback(async () => {
    const data = await monsterFetch<ToddlerStatus>("/api/guardian/learning/toddler/status");
    setStatus(data);
    return data;
  }, []);

  const runProgress = useCallback(async () => {
    setBusy(true);
    try {
      const data = await monsterFetch<Record<string, unknown>>(
        "/api/guardian/learning/toddler/progress",
        { method: "POST" },
      );
      setProgress(data);
      if (data.status && typeof data.status === "object") {
        setStatus(data.status as ToddlerStatus);
      }
      return data;
    } finally {
      setBusy(false);
    }
  }, []);

  const sendPraise = useCallback(async (reason = "user_praise") => {
    setBusy(true);
    try {
      const data = await monsterFetch<{ status: ToddlerStatus }>(
        "/api/guardian/learning/toddler/feedback",
        { method: "POST", body: JSON.stringify({ reason }) },
      );
      setStatus(data.status);
      return data;
    } finally {
      setBusy(false);
    }
  }, []);

  return { busy, status, progress, refresh, runProgress, sendPraise };
}