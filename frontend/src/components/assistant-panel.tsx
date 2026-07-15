"use client";

import { useState } from "react";
import { Sparkles, Send, Loader2, CheckCircle2, AlertCircle, MinusCircle } from "lucide-react";
import { useAskAssistant } from "@/hooks/use-weather";
import { cn } from "@/lib/cn";

const SUGGESTIONS = [
  "Should I carry an umbrella?",
  "Is tomorrow good for hiking?",
  "Can I go jogging today?",
  "Should I postpone my trip?",
];

const RECOMMENDATION_STYLE = {
  favorable: { icon: CheckCircle2, className: "text-teal", bg: "bg-teal-soft" },
  caution: { icon: MinusCircle, className: "text-amber", bg: "bg-amber-soft" },
  unfavorable: { icon: AlertCircle, className: "text-rose", bg: "bg-rose-soft" },
} as const;

export function AssistantPanel({
  lat,
  lon,
  locationName,
}: {
  lat?: number;
  lon?: number;
  locationName?: string;
}) {
  const [question, setQuestion] = useState("");
  const { mutate, data, isPending, error } = useAskAssistant();

  const ask = (q: string) => {
    setQuestion(q);
    mutate({
      question: q,
      location: { latitude: lat, longitude: lon, location_name: locationName },
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (question.trim()) ask(question.trim());
  };

  const style = data ? RECOMMENDATION_STYLE[data.recommendation] : null;
  const RecIcon = style?.icon;

  return (
    <div className="rounded-2xl border border-border bg-surface p-5 shadow-[var(--shadow-card)]">
      <div className="flex items-center gap-2">
        <Sparkles size={16} className="text-sky" />
        <h2 className="font-display text-sm font-semibold text-ink-soft">AI Weather Assistant</h2>
      </div>

      <div className="mt-3 flex flex-wrap gap-2">
        {SUGGESTIONS.map((s) => (
          <button
            key={s}
            onClick={() => ask(s)}
            className="rounded-full border border-border bg-surface-muted px-3 py-1.5 text-xs text-ink-soft transition hover:border-sky/40 hover:text-sky"
          >
            {s}
          </button>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="mt-3 flex gap-2">
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask about your plans…"
          className="flex-1 rounded-xl border border-border bg-canvas px-3 py-2.5 text-sm text-ink placeholder:text-ink-faint focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky/40"
        />
        <button
          type="submit"
          disabled={isPending || !question.trim()}
          className="flex items-center justify-center rounded-xl bg-sky px-3.5 py-2.5 text-white transition hover:opacity-90 disabled:opacity-50"
        >
          {isPending ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
        </button>
      </form>

      {error && (
        <p className="mt-3 text-xs text-rose">
          Couldn&apos;t reach the assistant right now — please try again.
        </p>
      )}

      {data && (
        <div className={cn("mt-4 rounded-xl p-4", style?.bg)}>
          <div className={cn("flex items-center gap-2 text-sm font-medium", style?.className)}>
            {RecIcon && <RecIcon size={16} />}
            <span className="capitalize">{data.recommendation}</span>
          </div>
          <p className="mt-1.5 text-sm text-ink">{data.answer}</p>
          {data.reasoning.length > 0 && (
            <ul className="mt-2 space-y-0.5 text-xs text-ink-soft">
              {data.reasoning.map((r, i) => (
                <li key={i}>• {r}</li>
              ))}
            </ul>
          )}
          <p className="mt-2 text-[10px] uppercase tracking-wide text-ink-faint">
            {data.source === "rule_based" ? "Rule-based engine" : `AI-generated (${data.source})`}
          </p>
        </div>
      )}
    </div>
  );
}
