"use client"

import { useState, useEffect } from "react"
import { Sidebar } from "@/components/sidebar"
import { Header } from "@/components/header"
import { WorkspaceSelector } from "@/components/workspace-selector"
import { DocumentUpload } from "@/components/document-upload"
import { DocumentTable } from "@/components/document-table"
import { MatchingResults } from "@/components/matching-results"
import { StatsDashboard } from "@/components/stats-dashboard"
import { CollapsibleSection } from "@/components/collapsible-section"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Play, RefreshCw, Download } from "lucide-react"
import { matchingApi, reportsApi, type Workspace } from "@/lib/api"

export default function Home() {
  const [workspace, setWorkspace] = useState<Workspace | null>(null)
  const [refreshKey, setRefreshKey] = useState(0)
  const [exportingWorkspace, setExportingWorkspace] = useState(false)

  const handleWorkspaceChange = (ws: Workspace | null) => {
    setWorkspace(ws)
  }

  const handleUploadComplete = () => {
    setRefreshKey((k) => k + 1)
  }

  const [matchingInProgress, setMatchingInProgress] = useState(false)

  const handleRunMatching = async () => {
    if (!workspace) return
    setMatchingInProgress(true)
    try {
      const response = await matchingApi.match(workspace.id)
      setRefreshKey((k) => k + 1)
      const matchCount = response.data?.length || 0
      if (matchCount > 0) {
        alert(`Matching completed! Found ${matchCount} matched group(s).`)
      } else {
        alert("Matching completed, but no matches were found.")
      }
    } catch (error: any) {
      console.error("Matching failed:", error)
      const errorMessage = error.response?.data?.detail || error.message || "Matching failed. Please try again."
      
      // Show detailed error message
      if (error.response?.status === 400 || error.response?.status === 404) {
        alert(`Matching Error:\n\n${errorMessage}\n\nPlease check:\n- Documents are fully processed (status: Processed)\n- You have at least a PO and Invoice\n- Documents have extracted PO numbers or vendor names`)
      } else {
        alert(`Matching failed: ${errorMessage}`)
      }
    } finally {
      setMatchingInProgress(false)
    }
  }

  const handleExportWorkspace = async (format: 'json' | 'csv') => {
    if (!workspace) return
    setExportingWorkspace(true)
    try {
      const response = await reportsApi.exportWorkspace(workspace.id, format)
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `workspace-reports-${workspace.id.slice(0, 8)}.${format}`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (error: any) {
      console.error("Export failed:", error)
      alert(`Failed to export workspace reports: ${error.response?.data?.detail || error.message}`)
    } finally {
      setExportingWorkspace(false)
    }
  }

  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header workspaceName={workspace?.name} />
        <main className="flex-1 overflow-y-auto bg-white p-6">
          <div className="max-w-7xl mx-auto space-y-3">
            {/* Workspace Selector */}
            <div className="flex items-center justify-between">
              <h1 className="text-2xl font-semibold tracking-tight text-black">Dashboard</h1>
              <WorkspaceSelector onWorkspaceChange={handleWorkspaceChange} />
            </div>

            {workspace && (
              <>
                {/* Quick Stats */}
                <StatsDashboard workspaceId={workspace.id} refreshKey={refreshKey} />

                {/* Quick Actions */}
                <div className="flex gap-2">
                  <Button 
                    onClick={handleRunMatching} 
                    className="h-9"
                    disabled={matchingInProgress}
                  >
                    <Play className={`mr-2 h-3.5 w-3.5 ${matchingInProgress ? 'animate-spin' : ''}`} />
                    {matchingInProgress ? "Matching..." : "Run Matching"}
                  </Button>
                  <Button 
                    variant="outline" 
                    onClick={() => setRefreshKey((k) => k + 1)} 
                    className="h-9"
                    disabled={matchingInProgress || exportingWorkspace}
                  >
                    <RefreshCw className="mr-2 h-3.5 w-3.5" />
                    Refresh
                  </Button>
                  <Button 
                    variant="outline" 
                    onClick={() => handleExportWorkspace('json')} 
                    className="h-9"
                    disabled={exportingWorkspace || matchingInProgress}
                  >
                    <Download className="mr-2 h-3.5 w-3.5" />
                    {exportingWorkspace ? "Exporting..." : "Export JSON"}
                  </Button>
                  <Button 
                    variant="outline" 
                    onClick={() => handleExportWorkspace('csv')} 
                    className="h-9"
                    disabled={exportingWorkspace || matchingInProgress}
                  >
                    <Download className="mr-2 h-3.5 w-3.5" />
                    Export CSV
                  </Button>
                </div>

                {/* Document Upload */}
                <CollapsibleSection title="Upload Documents" defaultCollapsed={false}>
                  <DocumentUpload
                    workspaceId={workspace.id}
                    onUploadComplete={handleUploadComplete}
                  />
                </CollapsibleSection>

                {/* Documents Table - Collapsible */}
                <CollapsibleSection
                  title="Documents"
                  defaultCollapsed={false}
                  count={undefined}
                >
                  <DocumentTable key={refreshKey} workspaceId={workspace.id} />
                </CollapsibleSection>

                {/* Matching Results */}
                <MatchingResults workspaceId={workspace.id} refreshKey={refreshKey} />
              </>
            )}

            {!workspace && (
              <Card className="border border-[#E5E5E5] bg-white">
                <div className="p-12 text-center">
                  <p className="text-[#404040]">
                    Please select or create a workspace to get started.
                  </p>
                </div>
              </Card>
            )}
          </div>
        </main>
      </div>
    </div>
  )
}
