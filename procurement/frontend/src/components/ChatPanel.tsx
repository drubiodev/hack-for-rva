"use client";

import { useState, useRef, useEffect } from "react";
import Link from "next/link";
import { useMutation } from "@tanstack/react-query";
import { useChatPanel } from "./ChatPanelContext";
import { sendChatMessage } from "@/lib/api";
import type { ChatMessage, ChatSource } from "@/lib/types";
import { MessageSquare, Send, Loader2, FileText, X } from "lucide-react";

export function ChatPanel() {
  const { isOpen, close } = useChatPanel();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [conversationId, setConversationId] = useState<string>();
  const bottomRef = useRef<HTMLDivElement>(null);

  const mutation = useMutation({
    mutationFn: (question: string) =>
      sendChatMessage(question, conversationId),
    onSuccess: (data) => {
      setConversationId(data.conversation_id);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.answer, sources: data.sources },
      ]);
    },
    onError: (error: Error) => {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `Error: ${error.message}` },
      ]);
    },
  });

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, mutation.isPending]);

  function handleSend() {
    const question = input.trim();
    if (!question || mutation.isPending) return;
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setInput("");
    mutation.mutate(question);
  }

  return (
    <>
      {/* Backdrop */}
      {isOpen && (
        <div className="fixed inset-0 z-40" onClick={close} />
      )}

      {/* Panel */}
      <div
        className={`fixed inset-y-0 right-0 z-50 flex w-[380px] flex-col border-l border-[#2e3248] bg-[#1a1d27] transition-transform duration-200 ${
          isOpen ? "translate-x-0" : "translate-x-full"
        }`}
      >
        {/* Header */}
        <div className="flex h-[60px] items-center gap-2.5 border-b border-[#2e3248] px-4">
          <MessageSquare size={16} className="text-[#4f8ef7]" />
          <span className="flex-1 text-sm font-semibold text-white">
            Chat with Documents
          </span>
          <button
            onClick={close}
            className="rounded-md p-1 text-[#64748b] hover:bg-[#22263a] hover:text-white"
          >
            <X size={16} />
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {/* AI disclaimer */}
          <div className="rounded-lg bg-[#4f8ef7]/10 border border-[#4f8ef7]/20 p-2.5 text-xs text-[#94a3b8]">
            AI-assisted · requires human review
          </div>

          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center py-12 text-center text-[#64748b]">
              <MessageSquare className="h-10 w-10 mb-3 opacity-30" />
              <p className="text-sm font-medium mb-1">Procurement Chat</p>
              <p className="text-xs max-w-[280px]">
                Ask questions about procurement documents, contracts, and
                vendors.
              </p>
            </div>
          )}

          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[85%] rounded-lg px-3 py-2 text-sm ${
                  msg.role === "user"
                    ? "bg-[#4f8ef7] text-white"
                    : "bg-[#22263a] text-[#e2e8f0]"
                }`}
              >
                <p className="whitespace-pre-wrap">{msg.content}</p>
                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-white/10">
                    <p className="text-[10px] font-medium mb-1 opacity-70">
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
                <span className="text-xs text-[#64748b]">Thinking...</span>
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
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about documents..."
              disabled={mutation.isPending}
              className="flex-1 rounded-lg border border-[#2e3248] bg-[#22263a] px-3 py-2 text-sm text-white placeholder:text-[#64748b] focus:border-[#4f8ef7] focus:outline-none disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={!input.trim() || mutation.isPending}
              className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-[#4f8ef7] text-white disabled:opacity-40"
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

function SourceChip({ source }: { source: ChatSource }) {
  return (
    <Link
      href={`/dashboard/documents/${source.document_id}`}
      className="inline-flex items-center gap-1 rounded bg-[#4f8ef7]/10 px-1.5 py-0.5 text-[10px] text-[#4f8ef7] hover:bg-[#4f8ef7]/20"
    >
      <FileText className="h-2.5 w-2.5" />
      {source.title ?? source.document_id.slice(0, 8)}
    </Link>
  );
}
