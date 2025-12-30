import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Utility function to merge Tailwind CSS classes
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Format date to readable string
 */
export function formatDate(date: string | Date): string {
  const d = typeof date === "string" ? new Date(date) : date;
  return new Intl.DateTimeFormat("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(d);
}

/**
 * Format file size to human-readable string
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + " " + sizes[i];
}

/**
 * Get risk level color
 */
export function getRiskColor(level: string): string {
  switch (level.toLowerCase()) {
    case "critical":
      return "text-red-600 bg-red-50 border-red-200";
    case "high":
      return "text-orange-600 bg-orange-50 border-orange-200";
    case "medium":
      return "text-yellow-600 bg-yellow-50 border-yellow-200";
    case "low":
      return "text-green-600 bg-green-50 border-green-200";
    default:
      return "text-gray-600 bg-gray-50 border-gray-200";
  }
}

/**
 * Get status color classes for badges
 */
export function getStatusColor(status: string): string {
  switch (status.toLowerCase()) {
    case "processed":
      return "text-green-700 bg-green-50 border-green-200";
    case "processing":
      return "text-blue-700 bg-blue-50 border-blue-200";
    case "failed":
      return "text-red-700 bg-red-50 border-red-200";
    case "uploaded":
      return "text-gray-700 bg-gray-50 border-gray-200";
    default:
      return "text-gray-700 bg-gray-50 border-gray-200";
  }
}

/**
 * Truncate text to specified length
 */
export function truncate(text: string, length: number): string {
  if (text.length <= length) return text;
  return text.slice(0, length) + "...";
}

/**
 * Get risk level from risk flags
 */
export function getRiskLevel(riskFlags: string[] | string | null | undefined): "critical" | "high" | "medium" | "low" | null {
  if (!riskFlags) return null;
  
  const flagsStr = Array.isArray(riskFlags) ? riskFlags.join(" ") : riskFlags;
  const flagsLower = flagsStr.toLowerCase();

  if (flagsLower.includes("critical")) return "critical";
  if (flagsLower.includes("high")) return "high";
  if (flagsLower.includes("medium")) return "medium";
  if (flagsLower.includes("low")) return "low";
  
  return null;
}

