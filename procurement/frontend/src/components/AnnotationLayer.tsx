"use client";

import { useState, useRef, useCallback } from "react";
import type { Annotation } from "@/lib/types";

const COLOR_PALETTE = [
  "#4f8ef7",
  "#a78bfa",
  "#f87171",
  "#fbbf24",
  "#34d399",
  "#fb923c",
  "#ec4899",
  "#06b6d4",
];

function initialsColor(initials: string): string {
  let sum = 0;
  for (let i = 0; i < initials.length; i++) {
    sum += initials.charCodeAt(i);
  }
  return COLOR_PALETTE[sum % COLOR_PALETTE.length];
}

function formatAnnotationTime(time: string): string {
  try {
    return new Date(time).toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
    });
  } catch {
    return time;
  }
}

interface AnnotationLayerProps {
  annotations: Annotation[];
  onAnnotationCreate: (data: { x: number; y: number; text: string }) => void;
  disabled?: boolean;
}

interface PendingAnnotation {
  x: number;
  y: number;
  screenX: number;
  screenY: number;
}

export default function AnnotationLayer({
  annotations,
  onAnnotationCreate,
  disabled = false,
}: AnnotationLayerProps) {
  const overlayRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const [pending, setPending] = useState<PendingAnnotation | null>(null);
  const [pendingText, setPendingText] = useState("");
  const [hoveredId, setHoveredId] = useState<string | null>(null);

  const handleOverlayClick = useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      if (disabled) return;
      // Only handle clicks directly on the overlay, not on pins or input
      if (e.target !== e.currentTarget) return;

      const rect = overlayRef.current?.getBoundingClientRect();
      if (!rect) return;

      const x = ((e.clientX - rect.left) / rect.width) * 100;
      const y = ((e.clientY - rect.top) / rect.height) * 100;

      setPending({
        x,
        y,
        screenX: e.clientX - rect.left,
        screenY: e.clientY - rect.top,
      });
      setPendingText("");

      // Focus input after render
      setTimeout(() => inputRef.current?.focus(), 0);
    },
    [disabled],
  );

  const submitAnnotation = useCallback(() => {
    if (!pending || !pendingText.trim()) {
      setPending(null);
      setPendingText("");
      return;
    }
    onAnnotationCreate({
      x: pending.x,
      y: pending.y,
      text: pendingText.trim(),
    });
    setPending(null);
    setPendingText("");
  }, [pending, pendingText, onAnnotationCreate]);

  const cancelAnnotation = useCallback(() => {
    setPending(null);
    setPendingText("");
  }, []);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (e.key === "Enter") {
        e.preventDefault();
        submitAnnotation();
      } else if (e.key === "Escape") {
        e.preventDefault();
        cancelAnnotation();
      }
    },
    [submitAnnotation, cancelAnnotation],
  );

  return (
    <div
      ref={overlayRef}
      className="absolute inset-0 pointer-events-auto z-10"
      onClick={handleOverlayClick}
    >
      {/* Existing annotation pins */}
      {annotations.map((annotation) => {
        const color = initialsColor(annotation.initials);
        const isHovered = hoveredId === annotation.id;

        return (
          <div
            key={annotation.id}
            className="absolute pointer-events-auto"
            style={{
              left: `${annotation.x}%`,
              top: `${annotation.y}%`,
              transform: "translate(-50%, -50%)",
            }}
            onMouseEnter={() => setHoveredId(annotation.id)}
            onMouseLeave={() => setHoveredId(null)}
          >
            {/* Pin circle */}
            <div
              className="flex items-center justify-center w-6 h-6 rounded-full text-[10px] font-bold text-white cursor-pointer transition-transform hover:scale-110 shadow-md"
              style={{ backgroundColor: color }}
              title={annotation.text}
            >
              {annotation.initials}
            </div>

            {/* Tooltip on hover */}
            {isHovered && (
              <div className="absolute left-8 top-1/2 -translate-y-1/2 z-20 w-56 rounded-md border border-[#2e3248] bg-[#1a1d27] p-3 shadow-lg pointer-events-none">
                <p className="text-xs text-[#94a3b8] mb-1">
                  <span className="font-medium text-white">
                    {annotation.author}
                  </span>{" "}
                  &middot; {formatAnnotationTime(annotation.time)}
                </p>
                <p className="text-sm text-[#94a3b8]">{annotation.text}</p>
              </div>
            )}
          </div>
        );
      })}

      {/* Pending annotation input */}
      {pending && (
        <div
          className="absolute z-20 pointer-events-auto"
          style={{
            left: `${pending.x}%`,
            top: `${pending.y}%`,
          }}
        >
          {/* Small pin indicator */}
          <div className="flex items-center justify-center w-6 h-6 rounded-full bg-[#4f8ef7] text-[10px] font-bold text-white shadow-md -translate-x-1/2 -translate-y-1/2">
            +
          </div>

          {/* Input box */}
          <div className="mt-1 w-56 rounded-md border border-[#2e3248] bg-[#1a1d27] p-2 shadow-lg">
            <input
              ref={inputRef}
              type="text"
              placeholder="Add a note..."
              value={pendingText}
              onChange={(e) => setPendingText(e.target.value)}
              onKeyDown={handleKeyDown}
              onBlur={submitAnnotation}
              className="w-full bg-[#111318] border border-[#2e3248] rounded px-2 py-1.5 text-xs text-[#94a3b8] placeholder-[#64748b] outline-none focus:border-[#4f8ef7] transition-colors"
            />
            <p className="mt-1 text-[10px] text-[#64748b]">
              Enter to save, Esc to cancel
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
