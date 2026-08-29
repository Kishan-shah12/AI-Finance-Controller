"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { BrainCircuit, ArrowRight, MessageSquareText, FileText, CheckCircle2, AlertTriangle, Clock } from "lucide-react";
import { formatINR, formatPercent } from "@/lib/utils";
import { ExceptionItem } from "@/lib/types";

export default function SettlementIntelligence() {
  const router = useRouter();
  const [exceptionId, setExceptionId] = useState<string | null>(null);
  const [topException, setTopException] = useState<ExceptionItem | null>(null);
  const [demoRun, setDemoRun] = useState<any>(null);
  const [exceptions, setExceptions] = useState<ExceptionItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [run, exList] = await Promise.all([
          api.getLatestDemoRun().catch(() => null),
          api.getExceptions().catch(() => [])
        ]);
        setDemoRun(run);
        setExceptions(exList);

        if (run && run.run_id) {
          const exId = await api.getHighestPriorityExceptionId(run.run_id);
          setExceptionId(exId);
          if (exId) {
            const detail = await api.getExceptionDetail(exId).catch(() => null);
            setTopException(detail);
          }
        } else if (exList.length > 0) {
          setExceptionId(exList[0].id || null);
          setTopException(exList[0]);
        }
      } catch (e) {
        console.error("Failed to load settlement intelligence data", e);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const handleViewEvidence = () => {
    if (exceptionId) {
      router.push(`/exceptions/${exceptionId}`);
    }
  };

  const totalVariance = exceptions.reduce((sum, item) => {
    const diff = item.variance_details?.amount_difference ?? item.variance_details?.difference ?? 0;
    return sum + Math.abs(diff);
  }, 0);

  const verifiedMatches = demoRun?.verified_match ?? 0;
  const explainableVar = demoRun?.explainable_variance ?? 0;
  const manualReview = demoRun?.review ?? 0;
  const unresolved = demoRun?.unresolved ?? exceptions.length;
  const totalScenarios = demoRun?.scenario_count ?? (verifiedMatches + explainableVar + manualReview + unresolved);

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
          {demoRun ? `Run ID: ${demoRun.run_id?.slice(0, 8)}` : "Frozen Demo Distribution"}
        </div>
      </div>

      {loading ? (
        <div className="py-16 text-center text-muted-foreground flex items-center justify-center gap-2">
          <Clock className="h-5 w-5 animate-spin" /> Loading settlement analysis...
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card className="bg-primary/5 border-primary/20">
              <CardContent className="p-6">
                <div className="text-sm font-semibold uppercase tracking-widest text-muted-foreground mb-2">Evaluated Scenarios</div>
                <div className="text-3xl font-bold tabular-nums">
                  {totalScenarios > 0 ? totalScenarios.toLocaleString() : "—"}
                </div>
                <div className="text-xs text-muted-foreground mt-1">Total ingested financial chains</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="text-sm font-semibold uppercase tracking-widest text-muted-foreground mb-2">Auto-Resolved Rate</div>
                <div className="text-3xl font-bold tabular-nums text-foreground">
                  {totalScenarios > 0 ? formatPercent((verifiedMatches + explainableVar) / totalScenarios) : "—"}
                </div>
                <div className="text-xs text-muted-foreground mt-1">{verifiedMatches} exact + {explainableVar} explainable</div>
              </CardContent>
            </Card>
            <Card className="bg-destructive/5 border-destructive/20">
              <CardContent className="p-6">
                <div className="text-sm font-semibold uppercase tracking-widest text-muted-foreground mb-2">Unexplained Variance</div>
                <div className="text-3xl font-bold tabular-nums text-destructive">
                  {totalVariance > 0 ? formatINR(totalVariance) : (unresolved > 0 ? `${unresolved} Cases` : "₹0")}
                </div>
                <div className="text-xs text-destructive/80 mt-1 font-medium">
                  {totalScenarios > 0 ? `${formatPercent(unresolved / totalScenarios)} of total volume` : "No exceptions"}
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            
            {/* WATERFALL DECOMPOSITION */}
            <Card className="border-border/60">
              <CardHeader>
                <CardTitle>Decision Matrix Breakdown</CardTitle>
                <CardDescription>Outcome distribution across all evaluated financial chains.</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4 font-mono text-sm">
                  <div className="flex justify-between items-center py-2 border-b">
                    <span>Total Scenarios Ingested</span>
                    <span className="font-semibold">{totalScenarios.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between items-center py-2 text-success">
                    <span>Verified Exact Matches</span>
                    <span className="font-semibold">{verifiedMatches.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between items-center py-2 text-indigo-600 dark:text-indigo-400">
                    <span>Explainable Variances (Fee / Tax Safe)</span>
                    <span className="font-semibold">{explainableVar.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between items-center py-2 text-amber-600">
                    <span>Manual Review Required</span>
                    <span className="font-semibold">{manualReview.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between items-center py-2 text-destructive font-medium border-b border-destructive/20">
                    <span>Unresolved Exceptions (High Risk)</span>
                    <span className="font-semibold">{unresolved.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between items-center pt-2 font-bold text-lg">
                    <span className="font-sans">Safe Automation Coverage</span>
                    <span className="text-success font-sans">
                      {totalScenarios > 0 ? formatPercent((verifiedMatches + explainableVar) / totalScenarios) : "—"}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* AI EXPLANATION */}
            <Card className="border-ai/30 shadow-md shadow-ai/5 bg-ai/5">
              <CardHeader>
                <CardTitle className="text-ai flex items-center gap-2">
                  <BrainCircuit className="h-5 w-5" />
                  AI Analysis & Priority Driver
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="text-base leading-relaxed">
                  ReconAI safely automated <span className="font-bold">{verifiedMatches + explainableVar} records</span> while isolating <span className="font-semibold text-destructive">{unresolved} unresolved exceptions</span> to eliminate false matches.
                  <br/><br/>
                  {topException ? (
                    <span>
                      The highest priority driver is <span className="font-semibold font-mono text-xs bg-muted/50 px-1.5 py-0.5 rounded">{topException.id}</span> ({topException.exception_type.replace(/_/g, ' ')}), requiring human review before closing.
                    </span>
                  ) : (
                    <span>No unresolved high-priority exceptions detected in the current run.</span>
                  )}
                </div>
                
                <Button 
                  className="bg-ai text-white hover:bg-ai/90 font-semibold w-full sm:w-auto"
                  onClick={handleViewEvidence}
                  disabled={!exceptionId}
                >
                  <FileText className="mr-2 h-4 w-4" /> 
                  {exceptionId ? "View Top Exception Evidence" : "No Evidence Available"}
                </Button>
              </CardContent>
            </Card>
          </div>
        </>
      )}

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
  const router = useRouter();
  return (
    <button 
      type="button"
      onClick={() => router.push(`/agent?q=${encodeURIComponent(q)}`)}
      className="p-4 border rounded-lg bg-card hover:border-ai/50 hover:bg-ai/5 transition-colors cursor-pointer group flex items-start justify-between text-left w-full focus-visible:ring-2 focus-visible:ring-ai"
      aria-label={`Ask ReconAI: ${q}`}
    >
      <span className="text-sm font-medium group-hover:text-ai transition-colors">{q}</span>
      <ArrowRight className="h-4 w-4 text-muted-foreground group-hover:text-ai shrink-0 mt-0.5" />
    </button>
  );
}
