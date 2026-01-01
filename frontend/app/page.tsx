"use client";

import { MainLayout } from "@/components/layout/main-layout";
import { AuthGuard } from "@/components/auth/auth-guard";
import { WorkspaceList } from "@/components/workspace/workspace-list";
import { useRouter } from "next/navigation";

export default function HomePage() {
  const router = useRouter();

  const handleWorkspaceSelect = (workspaceId: string) => {
    router.push(`/documents?workspaceId=${workspaceId}`);
  };

  return (
    <AuthGuard>
      <MainLayout>
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold">Workspaces</h1>
            <p className="text-muted-foreground">
              Organize your contracts by project, client, or category. Select a workspace to manage documents.
            </p>
          </div>

          <WorkspaceList onWorkspaceSelect={handleWorkspaceSelect} />
        </div>
      </MainLayout>
    </AuthGuard>
  );
}
