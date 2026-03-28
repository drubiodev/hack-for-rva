"use client";

import {
  createContext,
  useCallback,
  useContext,
  useState,
  type ReactNode,
} from "react";
import type { ChatMessage } from "@/lib/types";

/** Context about a specific document the user is viewing. */
export interface DocumentChatContext {
  documentId: string;
  title: string;
  vendorName?: string;
}

/** Which page the panel was opened from — drives suggested questions. */
export type ChatPage =
  | "dashboard"
  | "documents"
  | "document-detail"
  | "analytics"
  | "governance";

interface ChatPanelContextType {
  isOpen: boolean;
  toggle: () => void;
  open: () => void;
  close: () => void;
  /** Open panel and immediately send a query. */
  openWithQuery: (query: string) => void;
  /** Open panel with document context loaded. */
  openWithContext: (ctx: DocumentChatContext) => void;
  /** Pending query to auto-send when panel mounts. */
  pendingQuery: string | null;
  clearPendingQuery: () => void;
  /** Active document context (set from detail page). */
  documentContext: DocumentChatContext | null;
  clearDocumentContext: () => void;
  /** Chat history — persists across page navigations. */
  messages: ChatMessage[];
  setMessages: React.Dispatch<React.SetStateAction<ChatMessage[]>>;
  conversationId: string | undefined;
  setConversationId: React.Dispatch<React.SetStateAction<string | undefined>>;
  /** Start a fresh conversation. */
  newConversation: () => void;
  /** Which page opened the panel — for suggested questions. */
  activePage: ChatPage;
  setActivePage: (page: ChatPage) => void;
}

const ChatPanelContext = createContext<ChatPanelContextType>({
  isOpen: false,
  toggle: () => {},
  open: () => {},
  close: () => {},
  openWithQuery: () => {},
  openWithContext: () => {},
  pendingQuery: null,
  clearPendingQuery: () => {},
  documentContext: null,
  clearDocumentContext: () => {},
  messages: [],
  setMessages: () => {},
  conversationId: undefined,
  setConversationId: () => {},
  newConversation: () => {},
  activePage: "dashboard",
  setActivePage: () => {},
});

export function ChatPanelProvider({ children }: { children: ReactNode }) {
  const [isOpen, setIsOpen] = useState(false);
  const [pendingQuery, setPendingQuery] = useState<string | null>(null);
  const [documentContext, setDocumentContext] =
    useState<DocumentChatContext | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [activePage, setActivePage] = useState<ChatPage>("dashboard");

  const open = useCallback(() => setIsOpen(true), []);
  const close = useCallback(() => setIsOpen(false), []);
  const toggle = useCallback(() => setIsOpen((v) => !v), []);

  const openWithQuery = useCallback((query: string) => {
    setPendingQuery(query);
    setIsOpen(true);
  }, []);

  const openWithContext = useCallback((ctx: DocumentChatContext) => {
    setDocumentContext(ctx);
    setIsOpen(true);
  }, []);

  const clearPendingQuery = useCallback(() => setPendingQuery(null), []);
  const clearDocumentContext = useCallback(
    () => setDocumentContext(null),
    [],
  );

  const newConversation = useCallback(() => {
    setMessages([]);
    setConversationId(undefined);
    setDocumentContext(null);
    setPendingQuery(null);
  }, []);

  return (
    <ChatPanelContext.Provider
      value={{
        isOpen,
        toggle,
        open,
        close,
        openWithQuery,
        openWithContext,
        pendingQuery,
        clearPendingQuery,
        documentContext,
        clearDocumentContext,
        messages,
        setMessages,
        conversationId,
        setConversationId,
        newConversation,
        activePage,
        setActivePage,
      }}
    >
      {children}
    </ChatPanelContext.Provider>
  );
}

export function useChatPanel() {
  return useContext(ChatPanelContext);
}
