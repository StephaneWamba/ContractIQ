import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { DashboardStats } from "@/components/dashboard/DashboardStats";
import { RecentDocuments } from "@/components/documents/RecentDocuments";

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <Breadcrumbs items={[{ label: "Dashboard" }]} />
        <h1 className="text-3xl font-bold mt-4">Dashboard</h1>
        <p className="text-muted-foreground mt-2">
          Welcome back! Here's an overview of your contracts.
        </p>
      </div>

      <DashboardStats />
      <RecentDocuments />
    </div>
  );
}


