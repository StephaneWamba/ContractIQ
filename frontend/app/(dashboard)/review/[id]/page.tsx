import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { DocumentReview } from "@/components/review/DocumentReview";

export default function ReviewPage({
  params,
}: {
  params: { id: string };
}) {
  return (
    <div className="space-y-6">
      <Breadcrumbs
        items={[
          { label: "Documents", href: "/documents" },
          { label: "Review" },
        ]}
      />
      <DocumentReview documentId={params.id} />
    </div>
  );
}


