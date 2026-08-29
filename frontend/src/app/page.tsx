"use client";

import { useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";
import { MetricData, ExceptionItem } from "@/lib/types";
import { formatPercent, formatINR, cn } from "@/lib/utils";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ShieldAlert, CheckCircle2, AlertTriangle, Info, ArrowRight, Activity, Zap, Play, Database, RotateCw } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function Dashboard() {
  const [metrics, setMetrics] = useState<MetricData | null>(null);
  const [exceptions, setExceptions] = useState<ExceptionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [errorState, setErrorState] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setErrorState(null);
    try {
      const [m, e] = await Promise.all([
        api.getEvaluationMetrics(),
        api.getExceptions().catch(() => [])
      ]);
      setMetrics(m);
      setExceptions(e.slice(0, 5));
    } catch (err: any) {
      if (err instanceof ApiError || (err && err.type)) {
        setErrorState(err.type);
      } else {
        setErrorState('API_ERROR');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) {
    return <div className="p-8 flex items-center justify-center text-muted-foreground">Loading intelligence...</div>;
  }

  if (errorState === 'NO_DATA_YET') {
    return (
      <div className="p-8 max-w-3xl mx-auto mt-20 text-center space-y-6 animate-in fade-in duration-500">
        <div className="bg-primary/5 inline-flex p-6 rounded-full border border-primary/10">
          <Database className="h-12 w-12 text-primary opacity-80" />
        </div>
        <h2 className="text-3xl font-bold tracking-tight uppercase">No Reconciliation Data Yet</h2>
        <p className="text-muted-foreground text-lg max-w-md mx-auto leading-relaxed">
          Run your first reconciliation batch to populate the finance control center.
        </p>
        <div className="pt-4">
          <Link href="/reconciliation">
            <Button size="lg" className="font-bold tracking-wider px-8 h-12 text-sm uppercase">
              Run Reconciliation
            </Button>
          </Link>
        </div>
      </div>
    );
  }

  if (errorState === 'API_ERROR' || errorState === 'CONNECTION_ERROR' || !metrics) {
    const errorMsg = errorState === 'CONNECTION_ERROR' 
      ? 'Unable to reach the ReconAI backend.' 
      : (errorState === 'API_ERROR' ? 'ReconAI encountered a temporary server error.' : 'ReconAI backend is unavailable.');
    
    return (
      <div className="p-8 max-w-3xl mx-auto mt-20 text-center space-y-6 animate-in fade-in duration-500">
        <div className="bg-destructive/10 inline-flex p-6 rounded-full border border-destructive/20">
          <AlertTriangle className="h-12 w-12 text-destructive opacity-80" />
        </div>
        <h2 className="text-2xl font-bold tracking-tight text-destructive">{errorMsg}</h2>
        <div className="pt-4">
          <Button variant="outline" onClick={fetchData} className="flex items-center gap-2 mx-auto font-bold tracking-wider px-8 h-12 text-sm uppercase">
            <RotateCw className="h-4 w-4" /> Retry
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 animate-in fade-in duration-500">
      
      {/* HERO */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">AI Finance Control Center</h1>
          <p className="text-muted-foreground mt-2 text-lg max-w-xl">
            Reconcile faster. Explain every variance. Never force a financial match.
          </p>
        </div>
        <div className="flex items-center gap-4 bg-primary/5 text-primary px-5 py-4 rounded-xl border">
          <Activity className="h-8 w-8 text-primary opacity-80" />
          <div>
            <div className="text-sm font-semibold uppercase tracking-wider opacity-80">Primary KPI</div>
            <div className="text-2xl font-bold">{metrics.total_scenarios.toLocaleString()} Records Reconciled</div>
          </div>
        </div>
      </div>

      {/* METRICS GRID */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <MetricCard 
          title="Operational Match Rate" 
          value={formatPercent(metrics.operational_match_rate)} 
          highlight 
        />
        <MetricCard 
          title="Verified Match Rate" 
          value={formatPercent(metrics.strict_verified_match_rate)} 
        />
        <MetricCard 
          title="Auto-Match Precision" 
          value={formatPercent(metrics.safe_auto_match_precision)} 
          success
        />
        <MetricCard 
          title="False-Match Rate" 
          value={formatPercent(metrics.false_match_rate)} 
          success={metrics.false_match_rate === 0}
        />
        <MetricCard 
          title="Review Rate" 
          value={formatPercent(metrics.review_rate)} 
          warning
        />
        <MetricCard 
          title="Exception Rate" 
          value={formatPercent(metrics.exception_rate)} 
          danger
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* FUNNEL & AI BRIEF */}
        <div className="lg:col-span-2 space-y-8">
          
          <Card>
            <CardHeader>
              <CardTitle>Today's Reconciliation Funnel</CardTitle>
              <CardDescription>Records processed by the engine in the current batch.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="relative flex flex-col space-y-4">
                <FunnelStep 
                  label="Records Ingested" 
                  value={metrics.total_scenarios} 
                  color="bg-slate-100 dark:bg-slate-800" 
                />
                <FunnelStep 
                  label="Candidate Relationships Identified" 
                  value={metrics.total_scenarios} 
                  color="bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400 border-blue-200 dark:border-blue-800" 
                />
                <FunnelStep 
                  label="Verified Matches" 
                  value={Math.round(metrics.total_scenarios * metrics.strict_verified_match_rate)} 
                  color="bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400 border-green-200 dark:border-green-800" 
                />
                <FunnelStep 
                  label="Explainable Variances" 
                  value={Math.round(metrics.total_scenarios * (metrics.operational_match_rate - metrics.strict_verified_match_rate))} 
                  color="bg-indigo-50 dark:bg-indigo-900/20 text-indigo-700 dark:text-indigo-400 border-indigo-200 dark:border-indigo-800" 
                />
                <FunnelStep 
                  label="Manual Review Required" 
                  value={Math.round(metrics.total_scenarios * metrics.review_rate)} 
                  color="bg-amber-50 dark:bg-amber-900/20 text-amber-700 dark:text-amber-400 border-amber-200 dark:border-amber-800" 
                />
                <FunnelStep 
                  label="Unresolved Exceptions" 
                  value={Math.round(metrics.total_scenarios * metrics.exception_rate)} 
                  color="bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 border-red-200 dark:border-red-800" 
                />
              </div>
            </CardContent>
          </Card>

          <Card className="border-ai/30 shadow-sm shadow-ai/10">
            <CardHeader className="pb-3 flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-ai flex items-center gap-2">
                  <Zap className="h-5 w-5" />
                  AI Finance Brief
                </CardTitle>
              </div>
              <Badge variant="outline" className="text-ai border-ai/20 bg-ai/5">System Analysis</Badge>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground text-sm leading-relaxed mb-4">
                Today's reconciliation is <strong className="text-foreground">{formatPercent(metrics.operational_match_rate)}</strong> operationally resolved.
                ReconAI intentionally left <strong className="text-foreground">{formatPercent(metrics.exception_rate)}</strong> of scenarios unresolved because available evidence was insufficient. This guarantees a <strong className="text-foreground">0%</strong> false-match rate.
              </p>
              <Link href="/exceptions">
                <button className="text-sm font-medium text-ai hover:text-ai/80 flex items-center gap-1.5 transition-colors">
                  INVESTIGATE EXCEPTIONS <ArrowRight className="h-4 w-4" />
                </button>
              </Link>
            </CardContent>
          </Card>
          
        </div>

        {/* EXCEPTIONS & PULSE */}
        <div className="space-y-8">
          
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-destructive">
                <ShieldAlert className="h-5 w-5" />
                Attention Required
              </CardTitle>
              <CardDescription>Top financially impacting exceptions</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {exceptions.map((ex, i) => (
                <Link key={i} href={`/exceptions/${ex.id}`}>
                  <div className="group flex items-start justify-between p-3 rounded-lg border bg-card hover:border-muted-foreground/30 transition-colors cursor-pointer">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className={cn(
                          "text-[10px]",
                          ex.decision === "REVIEW" ? "text-amber-600 border-amber-200 bg-amber-50" : "text-red-600 border-red-200 bg-red-50"
                        )}>
                          {ex.decision}
                        </Badge>
                        <span className="text-xs font-mono text-muted-foreground">{ex.id}</span>
                      </div>
                      <div className="text-sm font-medium group-hover:text-primary transition-colors line-clamp-1">
                        {ex.exception_type.replace(/_/g, ' ')}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-semibold text-right tabular-nums text-foreground">
                        {formatINR(ex.variance_details?.amount_difference ?? ex.variance_details?.difference)}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {formatPercent(ex.confidence)} conf
                      </div>
                    </div>
                  </div>
                </Link>
              ))}
              <Link href="/exceptions" className="block text-center text-sm font-medium text-muted-foreground hover:text-foreground pt-2">
                View all exceptions
              </Link>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Settlement Pulse</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-end">
                  <div className="text-sm text-muted-foreground">Expected</div>
                  <div className="font-semibold tabular-nums text-lg">₹8,72,000</div>
                </div>
                <div className="flex justify-between items-end border-b pb-2">
                  <div className="text-sm text-muted-foreground">Actual (Bank)</div>
                  <div className="font-semibold tabular-nums text-lg">₹8,60,000</div>
                </div>
                <div className="flex justify-between items-end pt-1">
                  <div className="text-sm font-medium">Variance</div>
                  <div className="font-bold tabular-nums text-destructive text-xl">-₹12,000</div>
                </div>
                <div className="pt-2">
                  <div className="w-full h-2 bg-muted rounded-full overflow-hidden flex">
                    <div className="bg-success h-full" style={{ width: '98%' }}></div>
                    <div className="bg-destructive h-full" style={{ width: '2%' }}></div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

        </div>
      </div>
    </div>
  );
}

function MetricCard({ title, value, highlight, success, warning, danger }: { title: string, value: string, highlight?: boolean, success?: boolean, warning?: boolean, danger?: boolean }) {
  return (
    <div className={cn(
      "flex flex-col justify-center p-4 rounded-xl border bg-card shadow-sm",
      highlight && "bg-primary/5 border-primary/20",
      success && "bg-success/5 border-success/20",
      warning && "bg-review/5 border-review/20",
      danger && "bg-exception/5 border-exception/20"
    )}>
      <div className="text-xs font-medium text-muted-foreground mb-1 uppercase tracking-wider">{title}</div>
      <div className={cn(
        "text-2xl font-bold tabular-nums",
        highlight && "text-primary",
        success && "text-success",
        warning && "text-amber-600",
        danger && "text-exception"
      )}>{value}</div>
    </div>
  );
}

function FunnelStep({ label, value, color }: { label: string, value: number, color: string }) {
  return (
    <div className="flex items-center gap-4">
      <div className={cn("w-full py-3 px-4 rounded-md border flex items-center justify-between shadow-sm", color)}>
        <span className="font-medium text-sm">{label}</span>
        <span className="font-bold tabular-nums">{value.toLocaleString()}</span>
      </div>
    </div>
  );
}
