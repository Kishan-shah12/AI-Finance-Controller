"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { BrainCircuit, ArrowRight, MessageSquareText, FileText, Search } from "lucide-react";

export default function SettlementIntelligence() {
  const router = useRouter();
  const [exceptionId, setExceptionId] = useState<string | null>(null);
  const [loadingEv, setLoadingEv] = useState(true);

  useEffect(() => {
    async function loadEvidence() {
      try {
        const demoRun = await api.getLatestDemoRun();
        if (demoRun && demoRun.run_id) {
          const exId = await api.getHighestPriorityExceptionId(demoRun.run_id);
          setExceptionId(exId);
        }
      } catch (e) {
        console.error("Failed to load evidence ID", e);
      } finally {
        setLoadingEv(false);
      }
    }
    loadEvidence();
  }, []);

  const handleViewEvidence = () => {
    if (exceptionId) {
      router.push(`/exceptions/${exceptionId}`);
    }
  };

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8 animate-in fade-in duration-500">
      
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold tracking-tight">Settlement Intelligence</h1>
            <Badge variant="outline" className="bg-ai/10 text-ai border-ai/20">AI ANALYSIS</Badge>
          </div>
          <p className="text-muted-foreground mt-1">Variance decomposition and evidence-backed explanations.</p>
        </div>
        <div className="text-sm font-medium text-muted-foreground bg-muted/30 px-3 py-1.5 rounded-md border">
          Settlement Cycle: Aug 25 - Aug 26, 2026
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="bg-primary/5 border-primary/20">
          <CardContent className="p-6">
            <div className="text-sm font-semibold uppercase tracking-widest text-muted-foreground mb-2">Expected Settlement</div>
            <div className="text-3xl font-bold tabular-nums">₹8.72L</div>
            <div className="text-xs text-muted-foreground mt-1">Based on matched orders and payments</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="text-sm font-semibold uppercase tracking-widest text-muted-foreground mb-2">Actual Settlement</div>
            <div className="text-3xl font-bold tabular-nums text-foreground">₹8.60L</div>
            <div className="text-xs text-muted-foreground mt-1">Bank credit received</div>
          </CardContent>
        </Card>
        <Card className="bg-destructive/5 border-destructive/20">
          <CardContent className="p-6">
            <div className="text-sm font-semibold uppercase tracking-widest text-muted-foreground mb-2">Variance</div>
            <div className="text-3xl font-bold tabular-nums text-destructive">-₹12.4K</div>
            <div className="text-xs text-destructive/80 mt-1 font-medium">1.4% Shortfall</div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* WATERFALL DECOMPOSITION */}
        <Card className="border-border/60">
          <CardHeader>
            <CardTitle>Variance Decomposition</CardTitle>
            <CardDescription>Mathematical breakdown of the shortfall.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4 font-mono text-sm">
              <div className="flex justify-between items-center py-2 border-b">
                <span>Gross Expected Settlement</span>
                <span className="font-semibold">₹8,72,000</span>
              </div>
              <div className="flex justify-between items-center py-2 text-muted-foreground">
                <span>Payment Gateway Fees</span>
                <span>-₹6,400</span>
              </div>
              <div className="flex justify-between items-center py-2 text-muted-foreground border-b">
                <span>Platform Taxes (GST)</span>
                <span>-₹1,152</span>
              </div>
              <div className="flex justify-between items-center py-2 text-destructive font-medium border-b border-destructive/20">
                <span>Unresolved Transactions (Exceptions)</span>
                <span>-₹4,848</span>
              </div>
              <div className="flex justify-between items-center pt-2 font-bold text-lg">
                <span className="font-sans">Actual Bank Settlement</span>
                <span>₹8,60,000</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* AI EXPLANATION */}
        <Card className="border-ai/30 shadow-md shadow-ai/5 bg-ai/5">
          <CardHeader>
            <CardTitle className="text-ai flex items-center gap-2">
              <BrainCircuit className="h-5 w-5" />
              AI Explanation
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="text-lg leading-relaxed">
              ReconAI identified <span className="font-bold">three primary drivers</span> behind today's ₹12.4K variance.
              <br/><br/>
              Standard gateway fees and taxes account for the majority (-₹7,552). However, <span className="font-semibold text-destructive">four transactions remain unresolved</span> due to missing fee evidence, contributing exactly ₹4,848 to the shortfall.
            </div>
            
            <Button 
              className="bg-ai text-white hover:bg-ai/90 font-semibold w-full sm:w-auto"
              onClick={handleViewEvidence}
              disabled={loadingEv || !exceptionId}
            >
              <FileText className="mr-2 h-4 w-4" /> 
              {loadingEv ? "Loading Evidence..." : "View Evidence"}
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* AI Q&A */}
      <div>
        <h3 className="text-sm font-semibold uppercase tracking-widest text-muted-foreground mb-4 flex items-center gap-2">
          <MessageSquareText className="h-4 w-4" />
          Ask ReconAI
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <QuestionCard q="Why is today's settlement short?" />
          <QuestionCard q="Which settlement has the largest unexplained variance?" />
          <QuestionCard q="How much remains unreconciled?" />
          <QuestionCard q="Which exceptions impact cash the most?" />
        </div>
      </div>
    </div>
  );
}

function QuestionCard({ q }: { q: string }) {
  return (
    <div className="p-4 border rounded-lg bg-card hover:border-ai/50 hover:bg-ai/5 transition-colors cursor-pointer group flex items-start justify-between">
      <span className="text-sm font-medium group-hover:text-ai transition-colors">{q}</span>
      <ArrowRight className="h-4 w-4 text-muted-foreground group-hover:text-ai shrink-0 mt-0.5" />
    </div>
  );
}
