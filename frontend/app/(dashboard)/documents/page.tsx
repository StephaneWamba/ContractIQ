import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { DocumentsList } from "@/components/documents/DocumentsList";

export default function DocumentsPage() {
  return (
    <div className="space-y-6">
      <div>
        <Breadcrumbs
          items={[
            { label: "Documents", href: "/documents" },
            { label: "All Documents" },
          ]}
        />
        <h1 className="text-3xl font-bold mt-4">Documents</h1>
        <p className="text-muted-foreground mt-2">
          Manage and review your contract documents.
        </p>
      </div>
      <DocumentsList />
    </div>
  );
}


