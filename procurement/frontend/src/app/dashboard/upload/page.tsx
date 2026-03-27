"use client";

import { useState, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { Upload, FileText, X, Loader2 } from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";
import { uploadDocument } from "@/lib/api";

const ACCEPTED_TYPES = [
  "application/pdf",
  "image/png",
  "image/jpeg",
  "image/tiff",
];
const ACCEPTED_EXTENSIONS = [".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".tif"];
const MAX_SIZE_BYTES = 50 * 1024 * 1024; // 50 MB

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function isValidFile(file: File): string | null {
  const ext = "." + file.name.split(".").pop()?.toLowerCase();
  if (!ACCEPTED_EXTENSIONS.includes(ext) && !ACCEPTED_TYPES.includes(file.type)) {
    return `Invalid file type. Supported: PDF, PNG, JPG, TIFF`;
  }
  if (file.size > MAX_SIZE_BYTES) {
    return `File too large. Maximum size is 50 MB.`;
  }
  return null;
}

export default function UploadPage() {
  const router = useRouter();
  const { user } = useAuth();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: (file: File) => uploadDocument(file, user?.name ?? "unknown"),
    onSuccess: (result) => {
      router.push(`/dashboard/documents/${result.id}`);
    },
  });

  const handleFile = useCallback((file: File) => {
    const error = isValidFile(file);
    if (error) {
      setValidationError(error);
      setSelectedFile(null);
      return;
    }
    setValidationError(null);
    setSelectedFile(file);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      const file = e.dataTransfer.files[0];
      if (file) handleFile(file);
    },
    [handleFile],
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
  }, []);

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) handleFile(file);
    },
    [handleFile],
  );

  const clearFile = useCallback(() => {
    setSelectedFile(null);
    setValidationError(null);
    mutation.reset();
    if (fileInputRef.current) fileInputRef.current.value = "";
  }, [mutation]);

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Upload Document</h1>
      <Card>
        <CardHeader>
          <CardTitle>Upload a Procurement Document</CardTitle>
          <CardDescription>
            Upload a scanned contract, RFP, invoice, or other procurement
            document for AI-assisted extraction and review.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Drop zone */}
          <div
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onClick={() => fileInputRef.current?.click()}
            className={`flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed py-16 transition-colors ${
              dragOver
                ? "border-primary bg-primary/5"
                : "border-muted-foreground/25 hover:border-muted-foreground/50"
            }`}
          >
            <Upload className="mb-3 h-10 w-10 text-muted-foreground/50" />
            <p className="text-sm text-muted-foreground">
              Drag and drop a file here, or click to browse
            </p>
            <p className="mt-1 text-xs text-muted-foreground">
              Supported: PDF, PNG, JPG, TIFF (max 50 MB)
            </p>
          </div>
          <input
            ref={fileInputRef}
            type="file"
            accept={ACCEPTED_EXTENSIONS.join(",")}
            onChange={handleInputChange}
            className="hidden"
          />

          {/* Validation error */}
          {validationError && (
            <div className="rounded-md bg-destructive/10 px-4 py-3 text-sm text-destructive">
              {validationError}
            </div>
          )}

          {/* File preview */}
          {selectedFile && (
            <div className="flex items-center gap-3 rounded-md border px-4 py-3">
              <FileText className="h-5 w-5 shrink-0 text-muted-foreground" />
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium">
                  {selectedFile.name}
                </p>
                <p className="text-xs text-muted-foreground">
                  {formatFileSize(selectedFile.size)} &middot;{" "}
                  {selectedFile.type || "unknown type"}
                </p>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={(e) => {
                  e.stopPropagation();
                  clearFile();
                }}
                disabled={mutation.isPending}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          )}

          {/* Upload error */}
          {mutation.isError && (
            <div className="rounded-md bg-destructive/10 px-4 py-3 text-sm text-destructive">
              Upload failed:{" "}
              {mutation.error instanceof Error
                ? mutation.error.message
                : "Unknown error"}
            </div>
          )}

          {/* Upload button */}
          {selectedFile && (
            <Button
              onClick={() => mutation.mutate(selectedFile)}
              disabled={mutation.isPending}
              className="w-full"
            >
              {mutation.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Uploading...
                </>
              ) : (
                <>
                  <Upload className="mr-2 h-4 w-4" />
                  Upload Document
                </>
              )}
            </Button>
          )}

          <p className="text-xs text-muted-foreground text-center">
            AI-assisted extraction &mdash; requires human review
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
