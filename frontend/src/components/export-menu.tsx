"use client";

import { useState } from "react";
import { Download, ChevronDown } from "lucide-react";
import { exportUrl } from "@/lib/weather-api";

export function ExportMenu({ location }: { location?: string }) {
  const [open, setOpen] = useState(false);
  const formats: Array<{ label: string; format: "csv" | "json" | "pdf" }> = [
    { label: "CSV", format: "csv" },
    { label: "JSON", format: "json" },
    { label: "PDF", format: "pdf" },
  ];

  return (
    <div className="relative">
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex items-center gap-1.5 rounded-xl border border-border bg-surface px-3.5 py-2 text-sm text-ink-soft transition hover:text-sky"
      >
        <Download size={16} />
        Export
        <ChevronDown size={14} />
      </button>
      {open && (
        <>
          <div className="fixed inset-0 z-10" onClick={() => setOpen(false)} />
          <div className="absolute right-0 z-20 mt-1 w-32 overflow-hidden rounded-xl border border-border bg-surface shadow-[var(--shadow-card)]">
            {formats.map((f) => (
              <a
                key={f.format}
                href={exportUrl(f.format, location)}
                onClick={() => setOpen(false)}
                className="block px-4 py-2.5 text-sm text-ink-soft transition hover:bg-surface-muted hover:text-sky"
              >
                {f.label}
              </a>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
