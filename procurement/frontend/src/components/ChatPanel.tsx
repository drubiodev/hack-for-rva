"use client";

import { useRef, useEffect, useCallback } from "react";
import Link from "next/link";
import { useMutation } from "@tanstack/react-query";
import { useChatPanel, type ChatPage } from "./ChatPanelContext";
import { sendChatMessage } from "@/lib/api";
import type { ChatMessage, ChatSource } from "@/lib/types";
import {
  MessageSquare,
  Send,
  Loader2,
  FileText,
  X,
  RotateCw,
  Sparkles,
} from "lucide-react";

/* ------------------------------------------------------------------ */
/*  Suggested questions by page context                                */
/* ------------------------------------------------------------------ */

const SUGGESTIONS: Record<ChatPage, string[]> = {
  dashboard: [
    "What contracts expire this month?",
    "Which department has the highest spend?",
    "Any compliance issues I should know about?",
    "Show me sole-source contracts over $50K",
  ],
  documents: [
    "Find water infrastructure contracts",
    "Show me contracts over $1M",
    "Which vendors have the most contracts?",
    "Contracts missing MBE/WBE certification",
  ],
  "document-detail": [
    "Summarize this contract",
    "Any compliance risks?",
    "When does this expire and what's the renewal clause?",
    "Find similar contracts",
  ],
  analytics: [
    "Total spend by department?",
    "Spending trends for Public Utilities?",
    "Vendor concentration risk?",
    "How many contracts expire in 90 days?",
  ],
  governance: [
    "Which contracts have compliance gaps?",
    "Federal funding contracts without compliance flags?",
    "Contracts over $100K without insurance?",
    "Which rules are triggered most often?",
  ],
};

/* ------------------------------------------------------------------ */
/*  Intent badge colors                                                */
/* ------------------------------------------------------------------ */

const INTENT_STYLES: Record<string, string> = {
  semantic_search: "bg-blue-900/40 text-blue-300",
  aggregation: "bg-green-900/40 text-green-300",
  compliance_check: "bg-red-900/40 text-red-300",
  expiration_alert: "bg-amber-900/40 text-amber-300",
  filter_list: "bg-purple-900/40 text-purple-300",
  vendor_lookup: "bg-cyan-900/40 text-cyan-300",
  comparison: "bg-indigo-900/40 text-indigo-300",
  general_knowledge: "bg-slate-700/40 text-slate-300",
};

function intentLabel(intent: string): string {
  return intent.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

/* ------------------------------------------------------------------ */
/*  ChatPanel component                                                */
/* ------------------------------------------------------------------ */

export function ChatPanel() {
  const {
    isOpen,
    close,
    messages,
    setMessages,
    conversationId,
    setConversationId,
    pendingQuery,
    clearPendingQuery,
    documentContext,
    clearDocumentContext,
    newConversation,
    activePage,
  } = useChatPanel();

  const inputRef = useRef<HTMLInputElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  const mutation = useMutation({
    mutationFn: (question: string) =>
      sendChatMessage(question, conversationId),
    onSuccess: (data) => {
      setConversationId(data.conversation_id);
      setMessages((prev: ChatMessage[]) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer,
          sources: data.sources,
          intent: data.intent ?? undefined,
        },
      ]);
    },
    onError: (error: Error) => {
      setMessages((prev: ChatMessage[]) => [
        ...prev,
        { role: "assistant", content: `Error: ${error.message}` },
      ]);
    },
  });

  // Auto-scroll on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, mutation.isPending]);

  // Focus input when panel opens
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 200);
    }
  }, [isOpen]);

  // Handle pending query (auto-send when opened via openWithQuery)
  useEffect(() => {
    if (pendingQuery && isOpen && !mutation.isPending) {
      const q = pendingQuery;
      clearPendingQuery();
      sendQuestion(q);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pendingQuery, isOpen]);

  const sendQuestion = useCallback(
    (question: string) => {
      if (!question.trim() || mutation.isPending) return;
      // If document context is active, prepend it
      let fullQuestion = question;
      if (documentContext && messages.length === 0) {
        fullQuestion = `[Regarding document: "${documentContext.title}"${documentContext.vendorName ? ` by ${documentContext.vendorName}` : ""}] ${question}`;
      }
      setMessages((prev: ChatMessage[]) => [
        ...prev,
        { role: "user", content: question },
      ]);
      mutation.mutate(fullQuestion);
    },
    [mutation, documentContext, messages.length, setMessages],
  );

  function handleSend() {
    const question = inputRef.current?.value?.trim();
    if (!question) return;
    if (inputRef.current) inputRef.current.value = "";
    sendQuestion(question);
  }

  function handleNewConversation() {
    newConversation();
  }

  const suggestions = SUGGESTIONS[activePage] ?? SUGGESTIONS.dashboard;
  const showSuggestions = messages.length === 0 && !mutation.isPending;

  return (
    <>
      {/* Backdrop */}
      {isOpen && (
        <div className="fixed inset-0 z-40 bg-black/10" onClick={close} />
      )}

      {/* Panel */}
      <div
        className={`fixed inset-y-0 right-0 z-50 flex w-[400px] flex-col border-l border-[#2e3248] bg-[#1a1d27] shadow-2xl transition-transform duration-200 ${
          isOpen ? "translate-x-0" : "translate-x-full"
        }`}
      >
        {/* Header */}
        <div className="flex h-[52px] items-center gap-2.5 border-b border-[#2e3248] px-4">
          <Sparkles size={15} className="text-[#4f8ef7]" />
          <span
            className="flex-1 text-[13px] font-semibold text-white"
            style={{
              fontFamily:
                "'Bricolage Grotesque', var(--font-heading), sans-serif",
            }}
          >
            ContractIQ
          </span>
          {messages.length > 0 && (
            <button
              onClick={handleNewConversation}
              className="rounded-md p-1.5 text-[#64748b] hover:bg-[#22263a] hover:text-white transition-colors"
              title="New conversation"
            >
              <RotateCw size={14} />
            </button>
          )}
          <button
            onClick={close}
            className="rounded-md p-1.5 text-[#64748b] hover:bg-[#22263a] hover:text-white transition-colors"
          >
            <X size={14} />
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {/* AI disclaimer */}
          <div className="rounded-lg bg-[#4f8ef7]/10 border border-[#4f8ef7]/20 px-3 py-2 text-[11px] text-[#94a3b8]">
            AI-assisted · requires human review
          </div>

          {/* Document context banner */}
          {documentContext && messages.length === 0 && (
            <div className="rounded-lg bg-[#22263a] border border-[#2e3248] px-3 py-2.5">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <FileText size={12} className="text-[#4f8ef7] shrink-0" />
                  <span className="text-[11px] text-[#94a3b8]">
                    Asking about:
                  </span>
                </div>
                <button
                  onClick={clearDocumentContext}
                  className="text-[#64748b] hover:text-white"
                >
                  <X size={10} />
                </button>
              </div>
              <p className="text-[12px] text-white font-medium mt-1 truncate">
                {documentContext.title}
              </p>
              {documentContext.vendorName && (
                <p className="text-[11px] text-[#64748b] truncate">
                  {documentContext.vendorName}
                </p>
              )}
            </div>
          )}

          {/* Suggested questions */}
          {showSuggestions && (
            <div className="py-4">
              <div className="flex flex-col items-center text-center mb-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#4f8ef7]/10 mb-2">
                  <MessageSquare className="h-5 w-5 text-[#4f8ef7]" />
                </div>
                <p className="text-[13px] font-medium text-white mb-0.5">
                  {documentContext
                    ? "Ask about this document"
                    : "Ask ContractIQ"}
                </p>
                <p className="text-[11px] text-[#64748b] max-w-[280px]">
                  {documentContext
                    ? "Get insights about this specific contract"
                    : "Search contracts, analyze spend, check compliance"}
                </p>
              </div>
              <div className="space-y-1.5">
                {suggestions.map((q) => (
                  <button
                    key={q}
                    onClick={() => sendQuestion(q)}
                    className="w-full text-left rounded-lg border border-[#2e3248] bg-[#22263a] px-3 py-2 text-[12px] text-[#e2e8f0] hover:border-[#4f8ef7]/40 hover:bg-[#2a2e42] transition-colors"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Message history */}
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[85%] rounded-lg px-3 py-2 text-[13px] ${
                  msg.role === "user"
                    ? "bg-[#4f8ef7] text-white"
                    : "bg-[#22263a] text-[#e2e8f0]"
                }`}
              >
                {/* Intent badge */}
                {msg.role === "assistant" && msg.intent && (
                  <span
                    className={`inline-block rounded px-1.5 py-0.5 text-[9px] font-medium mb-1.5 ${
                      INTENT_STYLES[msg.intent] ?? INTENT_STYLES.general_knowledge
                    }`}
                  >
                    {intentLabel(msg.intent)}
                  </span>
                )}
                <p className="whitespace-pre-wrap leading-relaxed">
                  {msg.content}
                </p>
                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-white/10">
                    <p className="text-[9px] font-medium mb-1 opacity-60">
                      Sources
                    </p>
                    <div className="flex flex-wrap gap-1">
                      {msg.sources.map((source) => (
                        <SourceChip
                          key={source.document_id}
                          source={source}
                        />
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}

          {mutation.isPending && (
            <div className="flex justify-start">
              <div className="rounded-lg bg-[#22263a] px-3 py-2 flex items-center gap-2">
                <Loader2 className="h-3.5 w-3.5 animate-spin text-[#4f8ef7]" />
                <span className="text-[11px] text-[#64748b]">
                  Searching contracts...
                </span>
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div className="border-t border-[#2e3248] p-3">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="flex gap-2"
          >
            <input
              ref={inputRef}
              placeholder="Ask about contracts..."
              disabled={mutation.isPending}
              className="flex-1 rounded-lg border border-[#2e3248] bg-[#22263a] px-3 py-2 text-[13px] text-white placeholder:text-[#64748b] focus:border-[#4f8ef7] focus:outline-none disabled:opacity-50"
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
            />
            <button
              type="submit"
              disabled={mutation.isPending}
              className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-[#4f8ef7] text-white hover:bg-[#3d7ce5] disabled:opacity-40 transition-colors"
            >
              {mutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </button>
          </form>
        </div>
      </div>
    </>
  );
}

/* ------------------------------------------------------------------ */
/*  Source chip                                                         */
/* ------------------------------------------------------------------ */

function SourceChip({ source }: { source: ChatSource }) {
  const relevancePct = Math.min(Math.round(source.relevance * 100), 100);
  return (
    <Link
      href={`/dashboard/documents/${source.document_id}`}
      className="inline-flex items-center gap-1 rounded bg-[#4f8ef7]/10 px-1.5 py-0.5 text-[10px] text-[#4f8ef7] hover:bg-[#4f8ef7]/20 transition-colors"
      title={source.snippet ?? `Relevance: ${relevancePct}%`}
    >
      <FileText className="h-2.5 w-2.5 shrink-0" />
      <span className="truncate max-w-[140px]">
        {source.title ?? source.document_id.slice(0, 8)}
      </span>
      {source.relevance > 0 && source.relevance < 1 && (
        <span className="text-[8px] opacity-60 ml-0.5">{relevancePct}%</span>
      )}
    </Link>
  );
}
