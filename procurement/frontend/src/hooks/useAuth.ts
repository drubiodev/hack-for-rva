"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import type { ProcurementUser } from "@/lib/types";

const STORAGE_KEY = "procurement_user";

export function useAuth({ redirectTo = "/" }: { redirectTo?: string } = {}) {
  const router = useRouter();
  const [user, setUser] = useState<ProcurementUser | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) {
      router.replace(redirectTo);
      return;
    }
    try {
      const parsed: ProcurementUser = JSON.parse(stored);
      if (!parsed.name || !parsed.role) {
        router.replace(redirectTo);
        return;
      }
      setUser(parsed);
      setIsAuthenticated(true);
    } catch {
      router.replace(redirectTo);
    }
  }, [router, redirectTo]);

  const login = useCallback(
    (name: string, role: "analyst" | "supervisor") => {
      const u: ProcurementUser = { name, role };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(u));
      setUser(u);
      setIsAuthenticated(true);
      router.push("/dashboard");
    },
    [router],
  );

  const logout = useCallback(() => {
    localStorage.removeItem(STORAGE_KEY);
    setUser(null);
    setIsAuthenticated(false);
    router.replace("/");
  }, [router]);

  return { user, isAuthenticated, mounted, login, logout };
}
