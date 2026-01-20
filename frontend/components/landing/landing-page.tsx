"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { 
  FileText, 
  Search, 
  Shield, 
  Zap, 
  CheckCircle2,
  ArrowRight,
  Github,
  Linkedin,
  Sparkles
} from "lucide-react";
import { TopNavLanding } from "@/components/layout/top-nav-landing";

export function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-background via-background to-muted/20">
      <TopNavLanding />
      
      {/* Hero Section */}
      <section className="container mx-auto px-6 py-20 md:py-32 relative">
        <div className="max-w-4xl mx-auto text-center space-y-8">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-medium mb-4">
            <Sparkles className="h-4 w-4" />
            <span>AI-Powered Contract Intelligence</span>
          </div>
          
          <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold tracking-tight">
            Analyze Contracts with
            <span className="block text-primary mt-2">Intelligent AI</span>
          </h1>
          
          <p className="text-xl md:text-2xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
            Extract clauses, assess risks, and get instant answers from your contract documents using advanced AI and semantic search.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-4">
            <Button asChild size="lg" className="text-lg px-8 py-6">
              <Link href="/login">
                Get Started
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
            </Button>
            <Button asChild variant="outline" size="lg" className="text-lg px-8 py-6">
              <Link href="https://github.com/StephaneWamba/ContractIQ" target="_blank" rel="noopener noreferrer">
                <Github className="mr-2 h-5 w-5" />
                View on GitHub
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-6 py-20">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Powerful Features for Contract Analysis
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Everything you need to understand, analyze, and manage your contracts efficiently.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="p-6 rounded-xl border bg-card hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                <FileText className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Intelligent Extraction</h3>
              <p className="text-muted-foreground">
                Automatically extract and categorize 15+ clause types with confidence scores and risk assessment.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="p-6 rounded-xl border bg-card hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                <Search className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Semantic Search</h3>
              <p className="text-muted-foreground">
                Ask natural language questions across multiple documents and get answers with accurate citations.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="p-6 rounded-xl border bg-card hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                <Shield className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Risk Analysis</h3>
              <p className="text-muted-foreground">
                Automated risk scoring (0-100) with detailed flags and reasoning for each identified clause.
              </p>
            </div>

            {/* Feature 4 */}
            <div className="p-6 rounded-xl border bg-card hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                <Zap className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Fast Processing</h3>
              <p className="text-muted-foreground">
                Background processing with real-time status updates. Documents ready in minutes, not hours.
              </p>
            </div>

            {/* Feature 5 */}
            <div className="p-6 rounded-xl border bg-card hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                <CheckCircle2 className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Evidence Packs</h3>
              <p className="text-muted-foreground">
                Generate PDF evidence packs with citations for negotiations, compliance, and legal reviews.
              </p>
            </div>

            {/* Feature 6 */}
            <div className="p-6 rounded-xl border bg-card hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                <FileText className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Multi-Document</h3>
              <p className="text-muted-foreground">
                Search and analyze across entire document sets with workspace-based organization.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="container mx-auto px-6 py-20 bg-muted/30">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              How It Works
            </h2>
            <p className="text-lg text-muted-foreground">
              Simple workflow for powerful contract analysis
            </p>
          </div>

          <div className="space-y-8">
            <div className="flex gap-6">
              <div className="flex-shrink-0 w-12 h-12 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-bold text-lg">
                1
              </div>
              <div>
                <h3 className="text-xl font-semibold mb-2">Upload Documents</h3>
                <p className="text-muted-foreground">
                  Upload PDF or DOCX files. The system automatically extracts text, structures content, and indexes for search.
                </p>
              </div>
            </div>

            <div className="flex gap-6">
              <div className="flex-shrink-0 w-12 h-12 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-bold text-lg">
                2
              </div>
              <div>
                <h3 className="text-xl font-semibold mb-2">Extract Clauses</h3>
                <p className="text-muted-foreground">
                  AI identifies and extracts key clauses with risk scores, flags, and detailed reasoning for each finding.
                </p>
              </div>
            </div>

            <div className="flex gap-6">
              <div className="flex-shrink-0 w-12 h-12 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-bold text-lg">
                3
              </div>
              <div>
                <h3 className="text-xl font-semibold mb-2">Ask Questions</h3>
                <p className="text-muted-foreground">
                  Use natural language to query your contracts. Get instant answers with citations and page references.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-6 py-20">
        <div className="max-w-3xl mx-auto text-center space-y-6">
          <h2 className="text-3xl md:text-4xl font-bold">
            Ready to Analyze Your Contracts?
          </h2>
          <p className="text-lg text-muted-foreground">
            Get started with ContractIQ and transform how you review contracts.
          </p>
          <Button asChild size="lg" className="text-lg px-8 py-6">
            <Link href="/login">
              Start Analyzing
              <ArrowRight className="ml-2 h-5 w-5" />
            </Link>
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t bg-muted/30 py-12">
        <div className="container mx-auto px-6">
          <div className="flex flex-col md:flex-row justify-between items-center gap-6">
            <div className="text-center md:text-left">
              <p className="font-semibold text-lg mb-2">ContractIQ</p>
              <p className="text-sm text-muted-foreground">
                AI-Powered Contract Intelligence Platform
              </p>
            </div>
            <div className="flex gap-4">
              <Button asChild variant="outline" size="sm">
                <Link href="https://github.com/StephaneWamba/ContractIQ" target="_blank" rel="noopener noreferrer">
                  <Github className="h-4 w-4 mr-2" />
                  GitHub
                </Link>
              </Button>
              <Button asChild variant="outline" size="sm">
                <Link href="https://www.linkedin.com/in/stephane-wamba/" target="_blank" rel="noopener noreferrer">
                  <Linkedin className="h-4 w-4 mr-2" />
                  LinkedIn
                </Link>
              </Button>
            </div>
          </div>
          <div className="mt-8 pt-8 border-t text-center text-sm text-muted-foreground">
            <p>© 2024 ContractIQ. Portfolio project by Stephane Wamba.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

