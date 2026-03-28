"use client";

import { useEffect, useRef, useCallback } from "react";
import type { SourceHighlight } from "@/lib/types";

// Category colors matching the Modern Analyst design
export const CATEGORY_COLORS: Record<string, { bg: string; border: string; label: string }> = {
  risk: { bg: "bg-red-100/70", border: "border-red-300", label: "Risk" },
  compliance: { bg: "bg-emerald-100/70", border: "border-emerald-300", label: "Compliance" },
  financial: { bg: "bg-blue-100/70", border: "border-blue-300", label: "Financial" },
  identity: { bg: "bg-purple-100/70", border: "border-purple-300", label: "Identity" },
  date: { bg: "bg-amber-100/70", border: "border-amber-300", label: "Date" },
};

interface Segment {
  text: string;
  highlight: SourceHighlight | null;
}

function buildSegments(text: string, highlights: SourceHighlight[]): Segment[] {
  if (!highlights.length) return [{ text, highlight: null }];

  const sorted = [...highlights].sort((a, b) => a.offset - b.offset);
  const segments: Segment[] = [];
  let cursor = 0;

  for (const hl of sorted) {
    // Skip if overlapping with previous
    if (hl.offset < cursor) continue;

    // Plain text before this highlight
    if (hl.offset > cursor) {
      segments.push({ text: text.slice(cursor, hl.offset), highlight: null });
    }

    // Highlighted segment
    const end = Math.min(hl.offset + hl.length, text.length);
    segments.push({ text: text.slice(hl.offset, end), highlight: hl });
    cursor = end;
  }

  // Remaining plain text
  if (cursor < text.length) {
    segments.push({ text: text.slice(cursor), highlight: null });
  }

  return segments;
}

interface Props {
  text: string;
  highlights: SourceHighlight[];
  activeField: string | null;
  onHighlightClick: (field: string) => void;
  className?: string;
  style?: React.CSSProperties;
}

export default function HighlightedText({
  text,
  highlights,
  activeField,
  onHighlightClick,
  className,
  style,
}: Props) {
  const activeRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (activeField && activeRef.current) {
      activeRef.current.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }, [activeField]);

  const setRef = useCallback(
    (field: string) => (el: HTMLElement | null) => {
      if (field === activeField) {
        activeRef.current = el;
      }
    },
    [activeField],
  );

  const segments = buildSegments(text, highlights);

  return (
    <pre className={className} style={style}>
      {segments.map((seg, i) => {
        if (!seg.highlight) {
          return <span key={i}>{seg.text}</span>;
        }

        const hl = seg.highlight;
        const colors = CATEGORY_COLORS[hl.category] ?? CATEGORY_COLORS.risk;
        const isActive = activeField === hl.field;

        return (
          <mark
            key={i}
            ref={setRef(hl.field)}
            data-field={hl.field}
            onClick={() => onHighlightClick(hl.field)}
            title={`${colors.label}: ${hl.field.replace(/_/g, " ")}`}
            className={[
              colors.bg,
              "cursor-pointer rounded-sm px-0.5 transition-all relative",
              isActive
                ? `ring-2 ring-offset-1 ${colors.border.replace("border-", "ring-")} animate-pulse`
                : "",
            ].join(" ")}
            style={{ backgroundColor: undefined }}
          >
            {seg.text}
          </mark>
        );
      })}
    </pre>
  );
}
