"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarInset,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { ThemeToggle } from "@/components/ThemeToggle";
import { useAuth } from "@/hooks/useAuth";
import {
  LayoutDashboard,
  Upload,
  FileText,
  BarChart3,
  LogOut,
} from "lucide-react";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/dashboard/documents", label: "Documents", icon: FileText },
  { href: "/dashboard/upload", label: "Upload", icon: Upload },
  { href: "/dashboard/analytics", label: "Analytics", icon: BarChart3 },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const { user, mounted, logout } = useAuth();

  if (!mounted || !user) return null;

  return (
    <SidebarProvider>
      <Sidebar>
        <SidebarHeader className="p-4">
          <h2 className="text-lg font-semibold">Procurement</h2>
          <p className="text-xs text-muted-foreground">City of Richmond</p>
        </SidebarHeader>
        <SidebarContent>
          <SidebarMenu>
            {NAV_ITEMS.map((item) => (
              <SidebarMenuItem key={item.href}>
                <SidebarMenuButton
                  render={<Link href={item.href} />}
                  isActive={pathname === item.href}
                  tooltip={item.label}
                >
                  <item.icon className="h-4 w-4" />
                  <span>{item.label}</span>
                </SidebarMenuButton>
              </SidebarMenuItem>
            ))}
          </SidebarMenu>
        </SidebarContent>
        <SidebarFooter className="p-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-sm font-medium truncate">{user.name}</span>
            <Badge
              variant={user.role === "supervisor" ? "default" : "secondary"}
              className={
                user.role === "supervisor"
                  ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                  : "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200"
              }
            >
              {user.role === "supervisor" ? "Supervisor" : "Analyst"}
            </Badge>
          </div>
          <Button
            variant="ghost"
            size="sm"
            className="w-full justify-start"
            onClick={logout}
          >
            <LogOut className="h-4 w-4 mr-2" />
            Sign out
          </Button>
        </SidebarFooter>
      </Sidebar>
      <SidebarInset>
        <header className="flex h-14 items-center gap-2 border-b px-4">
          <SidebarTrigger />
          <Separator orientation="vertical" className="h-6" />
          <div className="flex flex-col">
            <span className="text-sm font-semibold leading-tight">
              Procurement Document Processing
            </span>
            <span className="text-[10px] text-muted-foreground leading-tight">
              AI-assisted, requires human review
            </span>
          </div>
          <div className="flex-1" />
          <div className="flex items-center gap-2">
            <span className="hidden sm:inline text-xs text-muted-foreground">
              {user.name} — {user.role === "supervisor" ? "Supervisor" : "Analyst"}
            </span>
            <ThemeToggle />
          </div>
        </header>
        <main className="flex-1 p-6">{children}</main>
      </SidebarInset>
    </SidebarProvider>
  );
}
