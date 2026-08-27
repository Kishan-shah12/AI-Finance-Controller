"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { MetricData } from "@/lib/types";
import { formatPercent, cn } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Lock, Cpu, BarChart3, ShieldCheck } from "lucide-react";

export default function MetricsPage() {
  const [metrics, setMetrics] = useState<MetricData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const m = await api.getEvaluationMetrics();
        setMetrics(m);
      } catch (err) {
        console.error("Failed to load metrics", err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) {
    return <div className="p-8 flex items-center justify-center text-muted-foreground">Loading metrics...</div>;
  }

  if (!metrics) {
    return <div className="p-8 text-destructive">Failed to load metrics data.</div>;
  }

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 border-b pb-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
            Model & System Performance
            <Badge variant="outline" className="text-ai border-ai/30 bg-ai/10 uppercase tracking-widest text-xs px-3 py-1">
              <Lock className="h-3 w-3 mr-1.5 inline-block" /> Locked Test Set
            </Badge>
          </h1>
          <p className="text-muted-foreground mt-2 text-lg">
            Scientific performance metrics measured on the frozen test distribution.
          </p>
        </div>
        <div className="text-right text-sm text-muted-foreground bg-muted/30 px-4 py-2 rounded-lg border">
          <div className="uppercase tracking-wider text-[10px] font-bold mb-1">Model Version</div>
          <div className="font-mono text-foreground font-medium">{metrics.model_version}</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* STANDARD ML METRICS */}
        <Card className="border-border/50 shadow-sm">
          <CardHeader className="bg-muted/20 border-b">
            <CardTitle className="text-lg flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-indigo-500" />
              Standard ML Metrics
            </CardTitle>
            <CardDescription>Raw machine learning performance against ground truth</CardDescription>
          </CardHeader>
          <CardContent className="p-0">
            <div className="divide-y">
              <MetricRow label="Standard Precision" value={metrics.standard_precision} />
              <MetricRow label="Overall Match Recall" value={metrics.overall_match_recall} />
              <MetricRow label="Standard F1 Score" value={metrics.standard_f1} highlight />
            </div>
          </CardContent>
        </Card>

        {/* OPERATIONAL METRICS */}
        <Card className="border-border/50 shadow-sm">
          <CardHeader className="bg-primary/5 border-b">
            <CardTitle className="text-lg flex items-center gap-2">
              <ShieldCheck className="h-5 w-5 text-primary" />
              Operational Metrics
            </CardTitle>
            <CardDescription>Business performance and automation outcomes</CardDescription>
          </CardHeader>
          <CardContent className="p-0">
            <div className="divide-y">
              <MetricRow label="Operational Match Rate" value={metrics.operational_match_rate} highlight />
              <MetricRow label="Strict Verified Match Rate" value={metrics.strict_verified_match_rate} />
              <MetricRow label="Auto-Match Rate" value={metrics.auto_match_rate} />
              <MetricRow label="False-Match Rate" value={metrics.false_match_rate} />
              <MetricRow label="Review Rate" value={metrics.review_rate} />
              <MetricRow label="Exception Rate" value={metrics.exception_rate} />
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* CUSTOM SAFE AUTOMATION METRICS */}
        <Card className="border-border/50 shadow-sm">
          <CardHeader className="bg-muted/20 border-b">
            <CardTitle className="text-lg flex items-center gap-2">
              <Lock className="h-5 w-5 text-amber-600" />
              Custom Safe-Automation Metrics
            </CardTitle>
            <CardDescription>Metrics adjusted for intentional uncertainty</CardDescription>
          </CardHeader>
          <CardContent className="p-0">
            <div className="divide-y">
              <MetricRow label="Safe Auto-Match Precision" value={metrics.safe_auto_match_precision} />
              <MetricRow label="Safe Auto-Match Recall" value={metrics.safe_auto_match_recall} />
            </div>
          </CardContent>
        </Card>

        {/* THROUGHPUT */}
        <Card className="border-border/50 shadow-sm">
          <CardHeader className="bg-muted/20 border-b">
            <CardTitle className="text-lg flex items-center gap-2">
              <Cpu className="h-5 w-5 text-muted-foreground" />
              System Metrics
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6 flex flex-col items-center justify-center space-y-2">
            <div className="text-4xl font-bold tabular-nums tracking-tight">
              ~{Math.round(metrics.core_engine_throughput).toLocaleString()} <span className="text-xl text-muted-foreground font-normal">records/sec</span>
            </div>
            <p className="text-sm text-muted-foreground uppercase tracking-widest font-semibold">Core-engine in-memory benchmark</p>
          </CardContent>
        </Card>
      </div>

      {/* METHODOLOGY */}
      <Card className="border-border/50 bg-muted/10 shadow-none">
        <CardHeader>
          <CardTitle className="text-lg">Methodology</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-4 text-sm font-medium">
            <div className="px-4 py-2 bg-background border rounded-md text-muted-foreground">Development</div>
            <div className="h-px flex-1 bg-border"></div>
            <div className="px-4 py-2 bg-background border rounded-md text-muted-foreground">Validation</div>
            <div className="h-px flex-1 bg-border"></div>
            <div className="px-4 py-2 bg-primary text-primary-foreground rounded-md shadow-sm">Locked Test</div>
          </div>
          <p className="text-muted-foreground text-sm">
            Model and thresholds were selected using development and validation data. The locked test set was used only for final evaluation. The locked test set was not used to tune the model, features, thresholds, or ambiguity margin.
          </p>
        </CardContent>
      </Card>
      
    </div>
  );
}

function MetricRow({ label, value, highlight = false }: { label: string, value: number, highlight?: boolean }) {
  return (
    <div className={cn("flex justify-between items-center p-4", highlight && "bg-primary/5")}>
      <span className={cn("text-sm font-medium", highlight ? "text-primary font-semibold" : "text-muted-foreground")}>{label}</span>
      <span className={cn("text-lg font-bold tabular-nums", highlight && "text-primary")}>{formatPercent(value, 2)}</span>
    </div>
  );
}
