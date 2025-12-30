"use client"

import { useState, useEffect } from "react"
import { ChevronDown, Plus } from "lucide-react"
import { Button } from "@/components/ui/button"
import { workspacesApi, type Workspace } from "@/lib/api"

interface WorkspaceSelectorProps {
  onWorkspaceChange: (workspace: Workspace | null) => void
}

export function WorkspaceSelector({ onWorkspaceChange }: WorkspaceSelectorProps) {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([])
  const [selectedWorkspace, setSelectedWorkspace] = useState<Workspace | null>(null)
  const [isOpen, setIsOpen] = useState(false)
  const [isCreating, setIsCreating] = useState(false)

  useEffect(() => {
    loadWorkspaces()
  }, [])

  const loadWorkspaces = async () => {
    try {
      const response = await workspacesApi.list()
      setWorkspaces(response.data)
      if (response.data.length > 0 && !selectedWorkspace) {
        setSelectedWorkspace(response.data[0])
        onWorkspaceChange(response.data[0])
      }
    } catch (error) {
      console.error("Failed to load workspaces:", error)
    }
  }

  const createWorkspace = async () => {
    setIsCreating(true)
    try {
      const name = `Workspace ${new Date().toLocaleDateString()}`
      const response = await workspacesApi.create(name, true)
      await loadWorkspaces()
      setSelectedWorkspace(response.data)
      onWorkspaceChange(response.data)
      setIsOpen(false)
    } catch (error) {
      console.error("Failed to create workspace:", error)
    } finally {
      setIsCreating(false)
    }
  }

  const handleSelect = (workspace: Workspace) => {
    setSelectedWorkspace(workspace)
    onWorkspaceChange(workspace)
    setIsOpen(false)
  }

  return (
    <div className="relative">
      <Button
        variant="outline"
        onClick={() => setIsOpen(!isOpen)}
        className="h-9 min-w-[180px] justify-between border-[#E5E5E5] bg-white text-sm text-black"
      >
        <span className="truncate text-black">
          {selectedWorkspace?.name || "Select Workspace"}
        </span>
        <ChevronDown className="ml-2 h-3.5 w-3.5 shrink-0 text-[#404040]" />
      </Button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute top-full z-20 mt-1.5 w-full rounded-md border border-[#E5E5E5] bg-white shadow-md">
            <div className="p-1">
              <Button
                variant="ghost"
                className="w-full justify-start h-8 text-sm"
                onClick={createWorkspace}
                disabled={isCreating}
              >
                <Plus className="mr-2 h-3.5 w-3.5" />
                {isCreating ? "Creating..." : "New Workspace"}
              </Button>
            </div>
            <div className="max-h-60 overflow-auto border-t border-border">
              {workspaces.map((workspace) => (
                <button
                  key={workspace.id}
                  onClick={() => handleSelect(workspace)}
                  className={`w-full px-3 py-2 text-left text-sm transition-colors ${
                    selectedWorkspace?.id === workspace.id
                      ? "bg-[#F5F5F5] text-black"
                      : "text-black hover:bg-[#F5F5F5]"
                  }`}
                >
                  <div className="font-medium">{workspace.name}</div>
                  <div className="text-xs text-[#404040]">
                    {workspace.is_temporary ? "Temporary" : "Saved"}
                  </div>
                </button>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  )
}

