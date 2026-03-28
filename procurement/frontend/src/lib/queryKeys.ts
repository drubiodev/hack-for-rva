// TanStack Query key constants — centralized to ensure cache invalidation consistency.

import type { FetchDocumentsParams } from "./api";

export const documentKeys = {
  all: ["documents"] as const,
  lists: () => [...documentKeys.all, "list"] as const,
  list: (filters?: FetchDocumentsParams) =>
    [...documentKeys.lists(), filters ?? {}] as const,
  details: () => [...documentKeys.all, "detail"] as const,
  detail: (id: string) => [...documentKeys.details(), id] as const,
};

export const analyticsKeys = {
  all: ["analytics"] as const,
  summary: () => [...analyticsKeys.all, "summary"] as const,
  risks: (days?: number) => [...analyticsKeys.all, "risks", days] as const,
};

export const reminderKeys = {
  all: ["reminders"] as const,
  list: (status?: string) => [...reminderKeys.all, "list", status] as const,
};

export const activityKeys = {
  all: ["activity"] as const,
  list: (limit?: number) => [...activityKeys.all, "list", limit] as const,
};

export const governanceKeys = {
  all: ["governance"] as const,
  rules: (filters?: Record<string, unknown>) =>
    [...governanceKeys.all, "rules", filters ?? {}] as const,
  compliance: () => [...governanceKeys.all, "compliance"] as const,
  auditLog: () => [...governanceKeys.all, "audit-log"] as const,
};
