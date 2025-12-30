"use client"

import { useEffect, useState } from "react"
import { Card } from "@/components/ui/card"
import { matchingApi, documentsApi, type MatchingResult, type Document } from "@/lib/api"

interface StatsDashboardProps {
  workspaceId: string
  refreshKey?: number
}

export function StatsDashboard({ workspaceId, refreshKey }: StatsDashboardProps) {
  const [stats, setStats] = useState({
    matchedGroups: 0,
    totalDiscrepancies: 0,
    criticalIssues: 0,
    warnings: 0,
    status: "Unknown",
  })

  useEffect(() => {
    loadStats()
  }, [workspaceId, refreshKey])

  // Only poll when refreshKey changes (manual refresh) or on initial load
  // Don't auto-poll to avoid UI blinking

  const loadStats = async () => {
    try {
      const [resultsRes, docsRes] = await Promise.all([
        matchingApi.getResults(workspaceId).catch((err) => {
          console.error("Failed to load matching results for stats:", err)
          return { data: [] }
        }),
        documentsApi.list(workspaceId).catch((err) => {
          console.error("Failed to load documents for stats:", err)
          return { data: [] }
        }),
      ])

      const results: MatchingResult[] = resultsRes.data || []
      const documents: Document[] = docsRes.data || []

      const totalDiscrepancies = results.reduce(
        (sum, r) => sum + r.discrepancies.length,
        0
      )
      const criticalIssues = results.reduce(
        (sum, r) =>
          sum +
          r.discrepancies.filter((d) => d.severity === "critical" || d.severity === "high")
            .length,
        0
      )
      const warnings = results.reduce(
        (sum, r) =>
          sum + r.discrepancies.filter((d) => d.severity === "medium" || d.severity === "low")
            .length,
        0
      )

      const perfectMatches = results.filter((r) => r.discrepancies.length === 0).length
      const partialMatches = results.filter((r) => r.discrepancies.length > 0).length

      let status = "Unknown"
      if (results.length > 0) {
        if (perfectMatches === results.length) {
          status = "Perfect"
        } else if (partialMatches > 0) {
          status = "Partial"
        }
      }

      setStats({
        matchedGroups: results.length,
        totalDiscrepancies,
        criticalIssues,
        warnings,
        status,
      })
    } catch (error) {
      console.error("Failed to load stats:", error)
    }
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
      <Card className="border border-[#E5E5E5] bg-white">
        <div className="p-5">
          <div className="text-2xl font-semibold text-black">{stats.matchedGroups}</div>
          <div className="text-xs text-[#404040] mt-1.5">Matched Groups</div>
        </div>
      </Card>
      <Card className="border border-[#E5E5E5] bg-white">
        <div className="p-5">
          <div className="text-2xl font-semibold text-black">{stats.totalDiscrepancies}</div>
          <div className="text-xs text-[#404040] mt-1.5">Total Discrepancies</div>
        </div>
      </Card>
      <Card className="border border-[#E5E5E5] bg-white">
        <div className="p-5">
          <div className="text-2xl font-semibold text-black">{stats.criticalIssues}</div>
          <div className="text-xs text-[#404040] mt-1.5">Critical Issues</div>
        </div>
      </Card>
      <Card className="border border-[#E5E5E5] bg-white">
        <div className="p-5">
          <div className="text-2xl font-semibold text-black">{stats.status}</div>
          <div className="text-xs text-[#404040] mt-1.5">Status</div>
        </div>
      </Card>
    </div>
  )
}

