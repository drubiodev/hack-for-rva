"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import type { ProcurementUser } from "@/lib/types";

const STORAGE_KEY = "procurement_user";

export default function RoleSelector() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      try {
        const user: ProcurementUser = JSON.parse(stored);
        if (user.name && user.role) {
          router.replace("/dashboard");
        }
      } catch {
        // invalid stored data, ignore
      }
    }
  }, [router]);

  function selectRole(role: "analyst" | "supervisor") {
    if (!name.trim()) return;
    const user: ProcurementUser = { name: name.trim(), role };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(user));
    router.push("/dashboard");
  }

  if (!mounted) return null;

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold">
            Procurement Document Processing
          </CardTitle>
          <CardDescription>
            AI-assisted decision-support tool for City of Richmond
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <label htmlFor="name" className="text-sm font-medium">
              Your Name
            </label>
            <Input
              id="name"
              placeholder="Enter your name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && name.trim()) selectRole("analyst");
              }}
            />
          </div>

          <div className="flex gap-3">
            <Button
              className="flex-1"
              variant="default"
              disabled={!name.trim()}
              onClick={() => selectRole("analyst")}
            >
              Sign in as Analyst
            </Button>
            <Button
              className="flex-1"
              variant="secondary"
              disabled={!name.trim()}
              onClick={() => selectRole("supervisor")}
            >
              Sign in as Supervisor
            </Button>
          </div>

          <p className="text-xs text-muted-foreground text-center">
            This is a decision-support tool. AI-assisted extractions require
            human review.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
