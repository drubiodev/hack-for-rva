"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";
import { ChatPanelProvider, useChatPanel } from "@/components/ChatPanelContext";
import { ChatPanel } from "@/components/ChatPanel";
import {
  LayoutDashboard,
  Upload,
  FolderOpen,
  BarChart3,
  LogOut,
  Shield,
  Activity,
  MessageSquare,
} from "lucide-react";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard Overview", icon: LayoutDashboard },
  { href: "/dashboard/documents", label: "Unified Portfolio", icon: FolderOpen },
  { href: "/dashboard/upload", label: "Upload", icon: Upload },
  { href: "/dashboard/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/dashboard/governance", label: "Governance", icon: Shield },
];

function ChatFAB() {
  const { toggle, isOpen } = useChatPanel();
  if (isOpen) return null;
  return (
    <button
      onClick={toggle}
      className="fixed bottom-6 right-6 z-30 flex h-14 w-14 items-center justify-center rounded-full bg-[#4f8ef7] text-white shadow-lg hover:bg-[#3d7ce5] hover:scale-105 transition-all duration-200"
      style={{ boxShadow: "0 4px 16px rgba(79, 142, 247, 0.35)" }}
      title="Chat with ContractIQ"
    >
      <MessageSquare className="h-6 w-6" />
    </button>
  );
}

function DashboardLayoutInner({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { user, mounted, logout } = useAuth();

  if (!mounted || !user) return null;

  const isActive = (href: string) => {
    if (href === "/dashboard") return pathname === "/dashboard";
    return pathname.startsWith(href);
  };

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <aside className="flex w-[250px] flex-col border-r border-[#E7E5E4] bg-white">
        {/* Logo */}
        <div className="flex items-center gap-2.5 px-5 py-5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#0F2537]">
            <Activity className="h-4 w-4 text-white" />
          </div>
          <div>
            <span className="text-sm font-semibold tracking-tight text-[#292524]" style={{ fontFamily: "'Bricolage Grotesque', var(--font-heading), sans-serif" }}>
              ContractIQ
            </span>
            <p className="text-[10px] leading-tight text-[#A8A29E]">
              City of Richmond
            </p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-2">
          <ul className="space-y-0.5">
            {NAV_ITEMS.map((item) => {
              const active = isActive(item.href);
              return (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    className={`flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors ${
                      active
                        ? "bg-[#F7F5F2] font-medium text-[#0F2537]"
                        : "text-[#A8A29E] hover:bg-[#F7F5F2] hover:text-[#292524]"
                    }`}
                  >
                    <item.icon className={`h-4 w-4 ${active ? "text-[#0F2537]" : ""}`} />
                    <span>{item.label}</span>
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* Bottom section */}
        <div className="border-t border-[#E7E5E4] px-3 py-3">
          <div className="flex items-center gap-3 rounded-lg px-3 py-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[#0F2537] text-xs font-medium text-white">
              {user.name
                .split(" ")
                .map((n) => n[0])
                .join("")
                .toUpperCase()
                .slice(0, 2)}
            </div>
            <div className="flex-1 min-w-0">
              <p className="truncate text-sm font-medium text-[#292524]">
                {user.name}
              </p>
              <Badge
                variant="secondary"
                className={`text-[10px] px-1.5 py-0 ${
                  user.role === "supervisor"
                    ? "bg-green-100 text-green-800"
                    : "bg-blue-100 text-blue-800"
                }`}
              >
                {user.role === "supervisor" ? "Supervisor" : "Analyst"}
              </Badge>
            </div>
          </div>

          <Button
            variant="ghost"
            size="sm"
            className="mt-1 w-full justify-start text-[#A8A29E] hover:text-[#292524]"
            onClick={logout}
          >
            <LogOut className="h-4 w-4 mr-2" />
            Sign out
          </Button>
        </div>
      </aside>

      {/* Main content area */}
      <div className="flex flex-1 flex-col overflow-hidden min-w-0">
        {/* Header bar */}
        <header className="flex h-14 items-center gap-3 border-b border-[#E7E5E4] bg-white px-8">
          <span
            className="text-[10px] font-medium uppercase tracking-widest text-[#A8A29E]"
            style={{ fontFamily: "'DM Mono', var(--font-mono), monospace" }}
          >
            Procurement Intelligence
          </span>
          <span className="text-[#E7E5E4]">|</span>
          <span className="text-sm font-medium text-[#292524]">
            AI-assisted, requires human review
          </span>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto bg-[#F7F5F2] p-8">
          {children}
        </main>
      </div>

      {/* Chat sidebar — inline, pushes content over */}
      <ChatPanel />

      {/* Chat FAB */}
      <ChatFAB />
    </div>
  );
}

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ChatPanelProvider>
      <DashboardLayoutInner>{children}</DashboardLayoutInner>
    </ChatPanelProvider>
  );
}
