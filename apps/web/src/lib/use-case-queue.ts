"use client";

import { useEffect, useState } from "react";
import { CaseSummary, loadCaseQueue } from "@/lib/api";

type QueueState =
  | { status: "loading" }
  | { status: "ready"; cases: CaseSummary[] }
  | { status: "unavailable" };

export function useCaseQueue() {
  const [state, setState] = useState<QueueState>({ status: "loading" });
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    let active = true;
    setState({ status: "loading" });
    void loadCaseQueue().then((cases) => {
      if (active) setState({ status: "ready", cases });
    }).catch(() => {
      if (active) setState({ status: "unavailable" });
    });
    return () => { active = false; };
  }, [attempt]);
  return { state, retry: () => setAttempt((value) => value + 1) };
}
