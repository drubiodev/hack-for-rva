"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { useAuth } from "@/hooks/useAuth";
import {
  fetchValidationRules,
  fetchComplianceSummary,
  fetchGlobalAuditLog,
  createValidationRule,
  toggleValidationRule,
  activateValidationRule,
  deprecateValidationRule,
  deleteValidationRule,
} from "@/lib/api";
import { governanceKeys } from "@/lib/queryKeys";
import type {
  ValidationRuleConfig,
  RuleType,
  RuleScope,
  RuleStatus,
  ValidationSeverity,
  DocumentType,
  ComplianceSummary,
  ValidationRuleAuditLog,
} from "@/lib/types";
import {
  Shield,
  Sparkles,
  Plus,
  X,
  AlertTriangle,
  AlertCircle,
  Info,
  Clock,
  CheckCircle2,
  Ban,
  Power,
  Trash2,
  Building2,
} from "lucide-react";

/* ------------------------------------------------------------------ */
/*  Constants                                                          */
/* ------------------------------------------------------------------ */

const RULE_TYPE_LABELS: Record<RuleType, string> = {
  threshold: "Threshold",
  required_field: "Required Field",
  semantic_policy: "Semantic Policy",
  district_check: "District Check",
  date_window: "Date Window",
};

const SEVERITY_CONFIG: Record<
  ValidationSeverity,
  { label: string; bg: string; text: string; icon: typeof AlertTriangle }
> = {
  error: { label: "Error", bg: "bg-red-100", text: "text-red-800", icon: AlertCircle },
  warning: { label: "Warning", bg: "bg-amber-100", text: "text-amber-800", icon: AlertTriangle },
  info: { label: "Info", bg: "bg-blue-100", text: "text-blue-800", icon: Info },
};

const STATUS_CONFIG: Record<
  RuleStatus,
  { label: string; bg: string; text: string }
> = {
  draft: { label: "Draft", bg: "bg-gray-100", text: "text-gray-700" },
  active: { label: "Active", bg: "bg-green-100", text: "text-green-800" },
  deprecated: { label: "Deprecated", bg: "bg-red-50", text: "text-red-600" },
};

const DEPARTMENT_OPTIONS = [
  "PUBLIC_WORKS",
  "TRANSPORTATION",
  "PUBLIC_SAFETY",
  "FINANCE",
  "INFORMATION_TECHNOLOGY",
  "PLANNING_DEVELOPMENT",
  "PUBLIC_UTILITIES",
  "PARKS_RECREATION",
  "HUMAN_RESOURCES",
  "RISK_MANAGEMENT",
  "COMMUNITY_DEVELOPMENT",
  "CITY_ASSESSOR",
  "PROCUREMENT",
  "OTHER",
];

const DOC_TYPE_OPTIONS: DocumentType[] = [
  "rfp",
  "rfq",
  "contract",
  "purchase_order",
  "invoice",
  "amendment",
  "cooperative",
  "other",
];

/* ------------------------------------------------------------------ */
/*  Helper Components                                                  */
/* ------------------------------------------------------------------ */

function FilterSelect({
  label,
  value,
  onChange,
  options,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  options: { value: string; label: string }[];
}) {
  return (
    <div className="flex flex-col gap-1">
      <label
        className="text-[10px] font-medium uppercase tracking-wider text-[#A8A29E]"
        style={{ fontFamily: "'DM Mono', var(--font-mono), monospace" }}
      >
        {label}
      </label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="h-8 rounded-lg border border-[#E7E5E4] bg-white px-2.5 text-sm text-[#292524] outline-none focus:border-[#0F2537] focus:ring-1 focus:ring-[#0F2537]"
      >
        <option value="">All</option>
        {options.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
    </div>
  );
}

function SeverityBadge({ severity }: { severity: ValidationSeverity }) {
  const cfg = SEVERITY_CONFIG[severity];
  const Icon = cfg.icon;
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-semibold ${cfg.bg} ${cfg.text}`}
    >
      <Icon className="h-3 w-3" />
      {cfg.label}
    </span>
  );
}

function StatusBadge({ status }: { status: RuleStatus }) {
  const cfg = STATUS_CONFIG[status];
  return (
    <span
      className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-semibold ${cfg.bg} ${cfg.text}`}
    >
      {cfg.label}
    </span>
  );
}

function RuleTypeBadge({ ruleType }: { ruleType: RuleType }) {
  const isAI = ruleType === "semantic_policy";
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-semibold ${
        isAI ? "bg-violet-100 text-violet-800" : "bg-[#F7F5F2] text-[#292524]"
      }`}
      style={{ fontFamily: "'DM Mono', var(--font-mono), monospace" }}
    >
      {isAI && <Sparkles className="h-3 w-3" />}
      {RULE_TYPE_LABELS[ruleType]}
    </span>
  );
}

function ScopeBadge({ scope, department }: { scope: RuleScope; department: string | null }) {
  if (scope === "global") {
    return (
      <span className="inline-flex items-center rounded-full bg-[#0F2537] px-2 py-0.5 text-[10px] font-semibold text-white">
        Global
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 rounded-full bg-teal-100 px-2 py-0.5 text-[10px] font-semibold text-teal-800">
      <Building2 className="h-3 w-3" />
      {department?.replace(/_/g, " ") ?? "Dept"}
    </span>
  );
}

function formatDept(d: string): string {
  return d
    .split("_")
    .map((w) => w.charAt(0) + w.slice(1).toLowerCase())
    .join(" ");
}

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

/* ------------------------------------------------------------------ */
/*  Tab 1 — Policy Rules                                               */
/* ------------------------------------------------------------------ */

function PolicyRulesTab() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const isSupervisor = user?.role === "supervisor";

  // Filters
  const [scopeFilter, setScopeFilter] = useState("");
  const [deptFilter, setDeptFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [typeFilter, setTypeFilter] = useState("");

  // Modal
  const [showModal, setShowModal] = useState(false);

  const ruleFilters = {
    scope: scopeFilter || undefined,
    department: deptFilter || undefined,
    status: statusFilter || undefined,
    rule_type: typeFilter || undefined,
  };

  const { data: rules, isLoading } = useQuery({
    queryKey: governanceKeys.rules(ruleFilters),
    queryFn: () =>
      fetchValidationRules({
        scope: scopeFilter as RuleScope | undefined || undefined,
        department: deptFilter || undefined,
        status: statusFilter as RuleStatus | undefined || undefined,
        rule_type: typeFilter as RuleType | undefined || undefined,
      }),
    refetchInterval: 30_000,
  });

  const toggleMutation = useMutation({
    mutationFn: (ruleId: string) =>
      toggleValidationRule(ruleId, user?.name ?? "unknown", user?.role ?? "analyst"),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: governanceKeys.all }),
  });

  const activateMutation = useMutation({
    mutationFn: (ruleId: string) =>
      activateValidationRule(ruleId, user?.name ?? "unknown", user?.role ?? "analyst"),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: governanceKeys.all }),
  });

  const deprecateMutation = useMutation({
    mutationFn: (ruleId: string) =>
      deprecateValidationRule(ruleId, user?.name ?? "unknown", user?.role ?? "analyst"),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: governanceKeys.all }),
  });

  const deleteMutation = useMutation({
    mutationFn: (ruleId: string) =>
      deleteValidationRule(ruleId, user?.role ?? "analyst"),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: governanceKeys.all }),
  });

  // Re-fetch when filters change
  const filteredRules = rules ?? [];

  return (
    <div className="space-y-4">
      {/* Filter bar */}
      <div className="flex flex-wrap items-end gap-3 rounded-[12px] border border-[#E7E5E4] bg-white p-4 shadow-[0_4px_24px_rgba(15,37,55,0.04)]">
        <FilterSelect
          label="Scope"
          value={scopeFilter}
          onChange={setScopeFilter}
          options={[
            { value: "global", label: "Global" },
            { value: "department", label: "Department" },
          ]}
        />
        <FilterSelect
          label="Department"
          value={deptFilter}
          onChange={setDeptFilter}
          options={DEPARTMENT_OPTIONS.map((d) => ({ value: d, label: formatDept(d) }))}
        />
        <FilterSelect
          label="Status"
          value={statusFilter}
          onChange={setStatusFilter}
          options={[
            { value: "draft", label: "Draft" },
            { value: "active", label: "Active" },
            { value: "deprecated", label: "Deprecated" },
          ]}
        />
        <FilterSelect
          label="Type"
          value={typeFilter}
          onChange={setTypeFilter}
          options={Object.entries(RULE_TYPE_LABELS).map(([k, v]) => ({
            value: k,
            label: v,
          }))}
        />
        <div className="flex-1" />
        {isSupervisor && (
          <Button
            onClick={() => setShowModal(true)}
            className="h-8 gap-1.5 rounded-lg bg-[#0F2537] text-sm text-white hover:bg-[#1a3a52]"
          >
            <Plus className="h-3.5 w-3.5" />
            New Rule
          </Button>
        )}
      </div>

      {/* Rules list */}
      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-28 rounded-[12px]" />
          ))}
        </div>
      ) : filteredRules.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-[12px] border border-[#E7E5E4] bg-white p-12 text-center shadow-[0_4px_24px_rgba(15,37,55,0.04)]">
          <Shield className="h-10 w-10 text-[#A8A29E]" />
          <p className="mt-3 text-sm font-medium text-[#292524]">No rules found</p>
          <p className="mt-1 text-xs text-[#A8A29E]">
            Adjust filters or create a new policy rule
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredRules.map((rule) => (
            <RuleCard
              key={rule.id}
              rule={rule}
              isSupervisor={isSupervisor}
              onToggle={() => toggleMutation.mutate(rule.id)}
              onActivate={() => activateMutation.mutate(rule.id)}
              onDeprecate={() => deprecateMutation.mutate(rule.id)}
              onDelete={() => {
                if (confirm("Delete this rule permanently?")) {
                  deleteMutation.mutate(rule.id);
                }
              }}
            />
          ))}
        </div>
      )}

      {/* Create rule modal */}
      {showModal && (
        <CreateRuleModal
          onClose={() => setShowModal(false)}
          userName={user?.name ?? "unknown"}
          userRole={user?.role ?? "analyst"}
        />
      )}
    </div>
  );
}

function RuleCard({
  rule,
  isSupervisor,
  onToggle,
  onActivate,
  onDeprecate,
  onDelete,
}: {
  rule: ValidationRuleConfig;
  isSupervisor: boolean;
  onToggle: () => void;
  onActivate: () => void;
  onDeprecate: () => void;
  onDelete: () => void;
}) {
  return (
    <div className="rounded-[12px] border border-[#E7E5E4] bg-white p-4 shadow-[0_4px_24px_rgba(15,37,55,0.04)] transition-shadow hover:shadow-[0_4px_24px_rgba(15,37,55,0.08)]">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <h3
              className="text-sm font-semibold text-[#0F2537]"
              style={{ fontFamily: "'Bricolage Grotesque', var(--font-heading), sans-serif" }}
            >
              {rule.name}
            </h3>
            <RuleTypeBadge ruleType={rule.rule_type} />
            <ScopeBadge scope={rule.scope} department={rule.department ?? null} />
            <SeverityBadge severity={rule.severity} />
            <StatusBadge status={rule.status} />
          </div>
          <p className="mt-1.5 line-clamp-2 text-xs text-[#78716C]">
            {rule.description}
          </p>
          {rule.policy_statement && (
            <p className="mt-1 line-clamp-1 text-[10px] italic text-[#A8A29E]">
              Policy: {rule.policy_statement}
            </p>
          )}
          <div className="mt-2 flex flex-wrap gap-1.5">
            {(rule.applies_to_doc_types ?? []).map((dt) => (
              <span
                key={dt}
                className="rounded bg-[#F7F5F2] px-1.5 py-0.5 text-[10px] text-[#78716C]"
                style={{ fontFamily: "'DM Mono', var(--font-mono), monospace" }}
              >
                {dt}
              </span>
            ))}
          </div>
        </div>

        {/* Supervisor actions */}
        {isSupervisor && (
          <div className="flex flex-shrink-0 items-center gap-1.5">
            {/* Enable/disable toggle */}
            <button
              onClick={onToggle}
              className={`flex h-7 items-center gap-1 rounded-lg px-2 text-[10px] font-medium transition-colors ${
                rule.enabled
                  ? "bg-green-100 text-green-800 hover:bg-green-200"
                  : "bg-gray-100 text-gray-500 hover:bg-gray-200"
              }`}
              title={rule.enabled ? "Disable rule" : "Enable rule"}
            >
              <Power className="h-3 w-3" />
              {rule.enabled ? "On" : "Off"}
            </button>

            {/* Status actions */}
            {rule.status === "draft" && (
              <button
                onClick={onActivate}
                className="flex h-7 items-center gap-1 rounded-lg bg-green-50 px-2 text-[10px] font-medium text-green-700 transition-colors hover:bg-green-100"
                title="Activate rule"
              >
                <CheckCircle2 className="h-3 w-3" />
                Activate
              </button>
            )}
            {rule.status === "active" && (
              <button
                onClick={onDeprecate}
                className="flex h-7 items-center gap-1 rounded-lg bg-amber-50 px-2 text-[10px] font-medium text-amber-700 transition-colors hover:bg-amber-100"
                title="Deprecate rule"
              >
                <Ban className="h-3 w-3" />
                Deprecate
              </button>
            )}

            {/* Delete */}
            <button
              onClick={onDelete}
              className="flex h-7 items-center rounded-lg px-1.5 text-[#A8A29E] transition-colors hover:bg-red-50 hover:text-red-600"
              title="Delete rule"
            >
              <Trash2 className="h-3.5 w-3.5" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Create Rule Modal                                                  */
/* ------------------------------------------------------------------ */

function CreateRuleModal({
  onClose,
  userName,
  userRole,
}: {
  onClose: () => void;
  userName: string;
  userRole: string;
}) {
  const queryClient = useQueryClient();

  const [form, setForm] = useState({
    name: "",
    description: "",
    rule_type: "threshold" as RuleType,
    scope: "global" as RuleScope,
    department: "",
    severity: "warning" as ValidationSeverity,
    status: "draft" as RuleStatus,
    policy_statement: "",
    field_name: "",
    operator: "",
    threshold_value: "",
    message_template: "",
    suggestion: "",
    applies_to_doc_types: [] as DocumentType[],
  });

  const createMutation = useMutation({
    mutationFn: () =>
      createValidationRule(
        {
          name: form.name,
          description: form.description,
          rule_type: form.rule_type,
          scope: form.scope,
          department: form.scope === "department" ? form.department : null,
          severity: form.severity,
          status: form.status,
          policy_statement: form.policy_statement || null,
          field_name: form.field_name || null,
          operator: form.operator || null,
          threshold_value: form.threshold_value || null,
          message_template: form.message_template,
          suggestion: form.suggestion || null,
          enabled: true,
          applies_to_doc_types: form.applies_to_doc_types,
          created_by: userName,
        },
        userRole,
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: governanceKeys.all });
      onClose();
    },
  });

  const set = (key: string, value: unknown) =>
    setForm((prev) => ({ ...prev, [key]: value }));

  const toggleDocType = (dt: DocumentType) => {
    setForm((prev) => ({
      ...prev,
      applies_to_doc_types: prev.applies_to_doc_types.includes(dt)
        ? prev.applies_to_doc_types.filter((t) => t !== dt)
        : [...prev.applies_to_doc_types, dt],
    }));
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="relative max-h-[85vh] w-full max-w-lg overflow-y-auto rounded-[16px] border border-[#E7E5E4] bg-white p-6 shadow-xl">
        <button
          onClick={onClose}
          className="absolute right-4 top-4 text-[#A8A29E] hover:text-[#292524]"
        >
          <X className="h-5 w-5" />
        </button>

        <h2
          className="text-lg font-semibold text-[#0F2537]"
          style={{ fontFamily: "'Bricolage Grotesque', var(--font-heading), sans-serif" }}
        >
          Create Policy Rule
        </h2>
        <p className="mt-1 text-xs text-[#A8A29E]">
          Define a new validation rule for procurement documents
        </p>

        <div className="mt-5 space-y-4">
          {/* Name */}
          <div>
            <label className="mb-1 block text-xs font-medium text-[#292524]">
              Rule Name
            </label>
            <Input
              value={form.name}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => set("name", e.target.value)}
              placeholder="e.g. Large Contract Threshold"
              className="h-9"
            />
          </div>

          {/* Description */}
          <div>
            <label className="mb-1 block text-xs font-medium text-[#292524]">
              Description
            </label>
            <Textarea
              value={form.description}
              onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => set("description", e.target.value)}
              placeholder="What does this rule check?"
              rows={2}
            />
          </div>

          {/* Type + Severity */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-xs font-medium text-[#292524]">
                Rule Type
              </label>
              <select
                value={form.rule_type}
                onChange={(e) => set("rule_type", e.target.value)}
                className="h-9 w-full rounded-lg border border-[#E7E5E4] bg-white px-2.5 text-sm"
              >
                {Object.entries(RULE_TYPE_LABELS).map(([k, v]) => (
                  <option key={k} value={k}>
                    {v}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-[#292524]">
                Severity
              </label>
              <select
                value={form.severity}
                onChange={(e) => set("severity", e.target.value)}
                className="h-9 w-full rounded-lg border border-[#E7E5E4] bg-white px-2.5 text-sm"
              >
                <option value="error">Error</option>
                <option value="warning">Warning</option>
                <option value="info">Info</option>
              </select>
            </div>
          </div>

          {/* Scope + Department */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-xs font-medium text-[#292524]">
                Scope
              </label>
              <select
                value={form.scope}
                onChange={(e) => set("scope", e.target.value)}
                className="h-9 w-full rounded-lg border border-[#E7E5E4] bg-white px-2.5 text-sm"
              >
                <option value="global">Global</option>
                <option value="department">Department</option>
              </select>
            </div>
            {form.scope === "department" && (
              <div>
                <label className="mb-1 block text-xs font-medium text-[#292524]">
                  Department
                </label>
                <select
                  value={form.department}
                  onChange={(e) => set("department", e.target.value)}
                  className="h-9 w-full rounded-lg border border-[#E7E5E4] bg-white px-2.5 text-sm"
                >
                  <option value="">Select...</option>
                  {DEPARTMENT_OPTIONS.map((d) => (
                    <option key={d} value={d}>
                      {formatDept(d)}
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>

          {/* Threshold fields (conditional) */}
          {form.rule_type === "threshold" && (
            <div className="grid grid-cols-3 gap-3">
              <div>
                <label className="mb-1 block text-xs font-medium text-[#292524]">
                  Field
                </label>
                <Input
                  value={form.field_name}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => set("field_name", e.target.value)}
                  placeholder="total_amount"
                  className="h-9"
                />
              </div>
              <div>
                <label className="mb-1 block text-xs font-medium text-[#292524]">
                  Operator
                </label>
                <select
                  value={form.operator}
                  onChange={(e) => set("operator", e.target.value)}
                  className="h-9 w-full rounded-lg border border-[#E7E5E4] bg-white px-2.5 text-sm"
                >
                  <option value="">Select...</option>
                  <option value=">">&gt;</option>
                  <option value=">=">&gt;=</option>
                  <option value="<">&lt;</option>
                  <option value="<=">&lt;=</option>
                  <option value="==">==</option>
                </select>
              </div>
              <div>
                <label className="mb-1 block text-xs font-medium text-[#292524]">
                  Threshold
                </label>
                <Input
                  type="number"
                  value={form.threshold_value}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => set("threshold_value", e.target.value)}
                  placeholder="100000"
                  className="h-9"
                />
              </div>
            </div>
          )}

          {/* Semantic policy statement (conditional) */}
          {form.rule_type === "semantic_policy" && (
            <div>
              <label className="mb-1 block text-xs font-medium text-[#292524]">
                Policy Statement (AI will evaluate against this)
              </label>
              <Textarea
                value={form.policy_statement}
                onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => set("policy_statement", e.target.value)}
                placeholder="All contracts over $50,000 must include performance bond requirements..."
                rows={3}
              />
            </div>
          )}

          {/* Message template */}
          <div>
            <label className="mb-1 block text-xs font-medium text-[#292524]">
              Message Template
            </label>
            <Input
              value={form.message_template}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => set("message_template", e.target.value)}
              placeholder="Contract value exceeds threshold of ${threshold_value}"
              className="h-9"
            />
          </div>

          {/* Suggestion */}
          <div>
            <label className="mb-1 block text-xs font-medium text-[#292524]">
              Suggestion (optional)
            </label>
            <Input
              value={form.suggestion}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => set("suggestion", e.target.value)}
              placeholder="Consider additional review for high-value contracts"
              className="h-9"
            />
          </div>

          {/* Document types */}
          <div>
            <label className="mb-1.5 block text-xs font-medium text-[#292524]">
              Applies to Document Types
            </label>
            <div className="flex flex-wrap gap-1.5">
              {DOC_TYPE_OPTIONS.map((dt) => (
                <button
                  key={dt}
                  onClick={() => toggleDocType(dt)}
                  className={`rounded-lg px-2.5 py-1 text-[11px] font-medium transition-colors ${
                    form.applies_to_doc_types.includes(dt)
                      ? "bg-[#0F2537] text-white"
                      : "bg-[#F7F5F2] text-[#78716C] hover:bg-[#E7E5E4]"
                  }`}
                >
                  {dt}
                </button>
              ))}
            </div>
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-2 pt-2">
            <Button
              variant="outline"
              onClick={onClose}
              className="h-9 rounded-lg text-sm"
            >
              Cancel
            </Button>
            <Button
              onClick={() => createMutation.mutate()}
              disabled={!form.name || !form.message_template || createMutation.isPending}
              className="h-9 rounded-lg bg-[#0F2537] text-sm text-white hover:bg-[#1a3a52]"
            >
              {createMutation.isPending ? "Creating..." : "Create Rule"}
            </Button>
          </div>
          {createMutation.isError && (
            <p className="text-xs text-red-600">
              {(createMutation.error as Error).message}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Tab 2 — Compliance Overview                                        */
/* ------------------------------------------------------------------ */

function ComplianceTab() {
  const { data: compliance, isLoading } = useQuery({
    queryKey: governanceKeys.compliance(),
    queryFn: fetchComplianceSummary,
    refetchInterval: 30_000,
  });

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-40 rounded-[12px]" />
        <Skeleton className="h-60 rounded-[12px]" />
      </div>
    );
  }

  if (!compliance) {
    return (
      <div className="flex flex-col items-center justify-center rounded-[12px] border border-[#E7E5E4] bg-white p-12 text-center shadow-[0_4px_24px_rgba(15,37,55,0.04)]">
        <Shield className="h-10 w-10 text-[#A8A29E]" />
        <p className="mt-3 text-sm font-medium text-[#292524]">
          No compliance data available
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-5">
      {/* Department compliance cards */}
      <div>
        <h3
          className="mb-3 text-sm font-semibold text-[#0F2537]"
          style={{ fontFamily: "'Bricolage Grotesque', var(--font-heading), sans-serif" }}
        >
          Department Compliance
        </h3>
        {compliance.department_cards.length === 0 ? (
          <p className="text-xs text-[#A8A29E]">No department data yet</p>
        ) : (
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {compliance.department_cards.map((dept) => (
              <div
                key={dept.department}
                className="rounded-[12px] border border-[#E7E5E4] bg-white p-4 shadow-[0_4px_24px_rgba(15,37,55,0.04)]"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-[#0F2537]">
                    {formatDept(dept.department)}
                  </span>
                  <span className="text-[10px] text-[#A8A29E]">
                    {dept.total_documents} docs
                  </span>
                </div>
                <div className="mt-3 flex items-end gap-4">
                  <div>
                    <p className="text-[10px] uppercase tracking-wider text-[#A8A29E]">
                      Violations
                    </p>
                    <p className="text-xl font-bold text-[#0F2537]">
                      {dept.error_count + dept.warning_count + dept.info_count}
                    </p>
                  </div>
                  <div className="flex gap-2 pb-0.5">
                    {dept.error_count > 0 && (
                      <span className="inline-flex items-center gap-0.5 text-[10px] font-medium text-red-600">
                        <AlertCircle className="h-3 w-3" /> {dept.error_count}
                      </span>
                    )}
                    {dept.warning_count > 0 && (
                      <span className="inline-flex items-center gap-0.5 text-[10px] font-medium text-amber-600">
                        <AlertTriangle className="h-3 w-3" /> {dept.warning_count}
                      </span>
                    )}
                  </div>
                </div>
                {/* Simple bar */}
                {(dept.total_documents ?? dept.document_count ?? 0) > 0 && (
                  <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-[#F7F5F2]">
                    <div
                      className="h-full rounded-full bg-red-400 transition-all"
                      style={{
                        width: `${Math.min(100, ((dept.error_count + dept.warning_count + dept.info_count) / Math.max(1, dept.total_documents ?? dept.document_count ?? 1)) * 100)}%`,
                      }}
                    />
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Top triggered rules */}
      <div>
        <h3
          className="mb-3 text-sm font-semibold text-[#0F2537]"
          style={{ fontFamily: "'Bricolage Grotesque', var(--font-heading), sans-serif" }}
        >
          Top Triggered Rules
        </h3>
        {compliance.top_triggered_rules.length === 0 ? (
          <p className="text-xs text-[#A8A29E]">No rule triggers recorded yet</p>
        ) : (
          <div className="rounded-[12px] border border-[#E7E5E4] bg-white shadow-[0_4px_24px_rgba(15,37,55,0.04)]">
            {compliance.top_triggered_rules.map((rule, idx) => {
              const maxCount = compliance.top_triggered_rules[0]?.trigger_count ?? 1;
              return (
                <div
                  key={rule.rule_id}
                  className={`flex items-center gap-3 px-4 py-3 ${
                    idx !== compliance.top_triggered_rules.length - 1
                      ? "border-b border-[#F7F5F2]"
                      : ""
                  }`}
                >
                  <span className="w-5 text-center text-xs font-bold text-[#A8A29E]">
                    {idx + 1}
                  </span>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <span className="truncate text-sm font-medium text-[#292524]">
                        {rule.rule_name}
                      </span>
                      <SeverityBadge severity={rule.severity as "error" | "warning" | "info"} />
                    </div>
                    <div className="mt-1 h-1.5 w-full overflow-hidden rounded-full bg-[#F7F5F2]">
                      <div
                        className={`h-full rounded-full transition-all ${
                          rule.severity === "error"
                            ? "bg-red-400"
                            : rule.severity === "warning"
                              ? "bg-amber-400"
                              : "bg-blue-400"
                        }`}
                        style={{
                          width: `${(rule.trigger_count / maxCount) * 100}%`,
                        }}
                      />
                    </div>
                  </div>
                  <span className="text-sm font-bold text-[#0F2537]">
                    {rule.trigger_count}
                  </span>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Recent violations */}
      <div>
        <h3
          className="mb-3 text-sm font-semibold text-[#0F2537]"
          style={{ fontFamily: "'Bricolage Grotesque', var(--font-heading), sans-serif" }}
        >
          Recent Violations
        </h3>
        {compliance.recent_violations.length === 0 ? (
          <p className="text-xs text-[#A8A29E]">No recent violations</p>
        ) : (
          <div className="overflow-hidden rounded-[12px] border border-[#E7E5E4] bg-white shadow-[0_4px_24px_rgba(15,37,55,0.04)]">
            <Table>
              <TableHeader>
                <TableRow className="border-[#F7F5F2]">
                  <TableHead className="text-[10px] uppercase tracking-wider text-[#A8A29E]">
                    Document
                  </TableHead>
                  <TableHead className="text-[10px] uppercase tracking-wider text-[#A8A29E]">
                    Rule
                  </TableHead>
                  <TableHead className="text-[10px] uppercase tracking-wider text-[#A8A29E]">
                    Severity
                  </TableHead>
                  <TableHead className="text-[10px] uppercase tracking-wider text-[#A8A29E]">
                    Message
                  </TableHead>
                  <TableHead className="text-[10px] uppercase tracking-wider text-[#A8A29E]">
                    When
                  </TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {compliance.recent_violations.map((v, idx) => (
                  <TableRow key={idx} className="border-[#F7F5F2]">
                    <TableCell className="max-w-[150px] truncate text-xs text-[#292524]">
                      {v.document_filename}
                    </TableCell>
                    <TableCell className="text-xs font-medium text-[#292524]">
                      {v.rule_name}
                    </TableCell>
                    <TableCell>
                      <SeverityBadge severity={v.severity as "error" | "warning" | "info"} />
                    </TableCell>
                    <TableCell className="max-w-[250px] truncate text-xs text-[#78716C]">
                      {v.message}
                    </TableCell>
                    <TableCell className="whitespace-nowrap text-xs text-[#A8A29E]">
                      {v.triggered_at ? timeAgo(v.triggered_at) : "--"}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        )}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Tab 3 — Audit Trail                                                */
/* ------------------------------------------------------------------ */

function AuditTrailTab() {
  const { data: auditLogs, isLoading } = useQuery({
    queryKey: governanceKeys.auditLog(),
    queryFn: fetchGlobalAuditLog,
    refetchInterval: 30_000,
  });

  if (isLoading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3, 4].map((i) => (
          <Skeleton key={i} className="h-16 rounded-[12px]" />
        ))}
      </div>
    );
  }

  const logs = auditLogs ?? [];

  if (logs.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center rounded-[12px] border border-[#E7E5E4] bg-white p-12 text-center shadow-[0_4px_24px_rgba(15,37,55,0.04)]">
        <Clock className="h-10 w-10 text-[#A8A29E]" />
        <p className="mt-3 text-sm font-medium text-[#292524]">No audit log entries</p>
        <p className="mt-1 text-xs text-[#A8A29E]">
          Changes to policy rules will appear here
        </p>
      </div>
    );
  }

  const ACTION_CONFIG: Record<string, { label: string; bg: string; text: string }> = {
    created: { label: "Created", bg: "bg-green-100", text: "text-green-800" },
    updated: { label: "Updated", bg: "bg-blue-100", text: "text-blue-800" },
    deleted: { label: "Deleted", bg: "bg-red-100", text: "text-red-800" },
    toggled: { label: "Toggled", bg: "bg-amber-100", text: "text-amber-800" },
    activated: { label: "Activated", bg: "bg-green-100", text: "text-green-800" },
    deprecated: { label: "Deprecated", bg: "bg-red-50", text: "text-red-600" },
  };

  return (
    <div className="space-y-2">
      {logs.map((log) => {
        const actionCfg = ACTION_CONFIG[log.action] ?? {
          label: log.action,
          bg: "bg-gray-100",
          text: "text-gray-700",
        };

        // Build diff summary
        const changes: string[] = [];
        if (log.old_values && log.new_values) {
          for (const key of Object.keys(log.new_values)) {
            const oldVal = log.old_values[key];
            const newVal = log.new_values[key];
            if (JSON.stringify(oldVal) !== JSON.stringify(newVal)) {
              changes.push(`${key}: ${JSON.stringify(oldVal)} -> ${JSON.stringify(newVal)}`);
            }
          }
        }

        return (
          <div
            key={log.id}
            className="rounded-[12px] border border-[#E7E5E4] bg-white p-4 shadow-[0_4px_24px_rgba(15,37,55,0.04)]"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <span
                    className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-semibold ${actionCfg.bg} ${actionCfg.text}`}
                  >
                    {actionCfg.label}
                  </span>
                  <span className="text-sm font-medium text-[#0F2537]">
                    {log.rule_name}
                  </span>
                </div>
                <p className="mt-1 text-xs text-[#78716C]">
                  by{" "}
                  <span className="font-medium text-[#292524]">{log.changed_by}</span>
                </p>
                {changes.length > 0 && (
                  <div className="mt-2 space-y-0.5">
                    {changes.slice(0, 3).map((ch, i) => (
                      <p
                        key={i}
                        className="truncate text-[10px] text-[#A8A29E]"
                        style={{ fontFamily: "'DM Mono', var(--font-mono), monospace" }}
                      >
                        {ch}
                      </p>
                    ))}
                    {changes.length > 3 && (
                      <p className="text-[10px] text-[#A8A29E]">
                        +{changes.length - 3} more changes
                      </p>
                    )}
                  </div>
                )}
              </div>
              <span className="whitespace-nowrap text-xs text-[#A8A29E]">
                {timeAgo(log.changed_at)}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Main Page                                                          */
/* ------------------------------------------------------------------ */

export default function GovernancePage() {
  const [activeTab, setActiveTab] = useState<number>(0);

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      {/* Page header */}
      <div>
        <h1
          className="text-xl font-bold text-[#0F2537]"
          style={{ fontFamily: "'Bricolage Grotesque', var(--font-heading), sans-serif" }}
        >
          Governance, Risk & Compliance
        </h1>
        <p className="mt-1 text-sm text-[#A8A29E]">
          Manage validation policy rules, view compliance status, and audit changes
        </p>
      </div>

      {/* Tabs */}
      <Tabs defaultValue={0} onValueChange={(val) => setActiveTab(val as number)}>
        <TabsList variant="line" className="border-b border-[#E7E5E4] bg-transparent">
          <TabsTrigger
            value={0}
            className="px-4 py-2 text-sm"
          >
            <Shield className="mr-1.5 h-3.5 w-3.5" />
            Policy Rules
          </TabsTrigger>
          <TabsTrigger
            value={1}
            className="px-4 py-2 text-sm"
          >
            <AlertTriangle className="mr-1.5 h-3.5 w-3.5" />
            Compliance Overview
          </TabsTrigger>
          <TabsTrigger
            value={2}
            className="px-4 py-2 text-sm"
          >
            <Clock className="mr-1.5 h-3.5 w-3.5" />
            Audit Trail
          </TabsTrigger>
        </TabsList>

        <TabsContent value={0} className="mt-4">
          <PolicyRulesTab />
        </TabsContent>

        <TabsContent value={1} className="mt-4">
          <ComplianceTab />
        </TabsContent>

        <TabsContent value={2} className="mt-4">
          <AuditTrailTab />
        </TabsContent>
      </Tabs>
    </div>
  );
}
