import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { QAChatInterface } from "@/components/qa/QAChatInterface";

export default function QAPage() {
  return (
    <div className="space-y-6">
      <div>
        <Breadcrumbs
          items={[
            { label: "Q&A", href: "/qa" },
            { label: "Ask Questions" },
          ]}
        />
        <h1 className="text-3xl font-bold mt-4">Q&A Assistant</h1>
        <p className="text-muted-foreground mt-2">
          Ask questions about your documents and get answers with citations.
        </p>
      </div>
      <QAChatInterface />
    </div>
  );
}


