"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { ExceptionItem } from "@/lib/types";
import { formatPercent, formatINR, cn } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ArrowLeft, BrainCircuit, Check, X, AlertTriangle, ShieldCheck, ChevronRight, Activity, Clock } from "lucide-react";
import Link from "next/link";

export default function ExceptionDetail() {
  const params = useParams();
  const router = useRouter();
  const [exception, setException] = useState<ExceptionItem | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      if (!params?.id || params.id === "undefined" || params.id === "null") {
        setLoading(false);
        return;
      }
      try {
        const data = await api.getExceptionDetail(params.id as string);
        setException(data);
      } catch (err) {
        console.error("Failed to load exception details", err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [params?.id]);

  if (loading) {
    return <div className="p-8 flex items-center justify-center text-muted-foreground">Loading investigation context...</div>;
  }

  if (!exception) {
    return <div className="p-8 text-destructive">Exception not found.</div>;
  }

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6 animate-in slide-in-from-bottom-4 duration-500">
      
      <div className="flex items-center gap-4 text-sm text-muted-foreground mb-4">
        <Link href="/exceptions" className="hover:text-foreground flex items-center gap-1 transition-colors">
          <ArrowLeft className="h-4 w-4" /> Back to Queue
        </Link>
      </div>

      <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-3xl font-bold tracking-tight">EXCEPTION {exception.id}</h1>
            <Badge variant="outline" className={cn(
              "px-3 py-1 text-sm font-semibold",
              exception.decision === "REVIEW" ? "text-amber-600 border-amber-200 bg-amber-50" : "text-red-600 border-red-200 bg-red-50"
            )}>
              {exception.decision}
            </Badge>
          </div>
          <p className="text-muted-foreground text-lg flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-amber-500" />
            {exception.exception_type.replace(/_/g, ' ')}
          </p>
        </div>
        <div className="text-right">
          <div className="text-sm font-semibold text-muted-foreground uppercase tracking-widest mb-1">Disputed Amount</div>
          <div className="text-3xl font-bold text-destructive tabular-nums">
            {formatINR(exception.variance_details?.amount_difference || 50000)}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 pt-4">
        
        {/* LEFT: FINANCIAL CHAIN */}
        <div className="lg:col-span-5 space-y-4">
          <h3 className="text-sm font-semibold uppercase tracking-widest text-muted-foreground px-2">Financial Chain</h3>
          
          <div className="relative border rounded-xl p-6 bg-card shadow-sm">
            {/* Connecting line */}
            <div className="absolute left-[39px] top-[40px] bottom-[40px] w-0.5 bg-muted"></div>
            
            <div className="space-y-8 relative">
              <ChainNode 
                label="ORDER" 
                id="ORD-12345" 
                amount={50000} 
                status="Confirmed" 
                time="10:02 AM" 
              />
              <ChainNode 
                label="PAYMENT" 
                id="PAY-98765" 
                amount={50000} 
                status="Authorized" 
                time="10:05 AM" 
              />
              <ChainNode 
                label="SETTLEMENT" 
                id="SET-55443" 
                amount={48500} 
                status="Processed" 
                time="2 days later" 
                warning
              />
              <ChainNode 
                label="BANK" 
                id="BNK-11223" 
                amount={48500} 
                status="Credited" 
                time="2 days later" 
                warning
              />
            </div>
          </div>
        </div>

        {/* RIGHT: AI INVESTIGATION */}
        <div className="lg:col-span-7 space-y-6">
          <Card className="border-ai/30 shadow-md shadow-ai/5 overflow-hidden">
            <div className="bg-ai/5 border-b border-ai/10 px-6 py-4 flex items-center justify-between">
              <CardTitle className="text-ai flex items-center gap-2 text-lg">
                <BrainCircuit className="h-5 w-5" />
                AI Investigation
              </CardTitle>
              <div className="flex items-center gap-2 text-sm">
                <span className="text-muted-foreground">Confidence</span>
                <span className="font-bold tabular-nums text-foreground">{formatPercent(exception.confidence)}</span>
              </div>
            </div>
            <CardContent className="p-6 space-y-6">
              
              <div className="space-y-2">
                <h4 className="text-sm font-semibold uppercase tracking-widest text-muted-foreground">Why didn't ReconAI automatically close this?</h4>
                <div className="text-lg leading-relaxed text-foreground">
                  Payment and settlement references are consistent. The settlement is {formatINR(1500)} below the payment amount. 
                  <span className="text-destructive font-medium bg-destructive/10 px-1 rounded ml-1">The available fee/tax evidence does not fully explain the variance.</span> 
                  <br/><br/>ReconAI therefore recommends human review to prevent a forced match.
                </div>
              </div>

              <div className="space-y-3 pt-4 border-t">
                <h4 className="text-sm font-semibold uppercase tracking-widest text-muted-foreground mb-4">Evidence Collection</h4>
                
                {exception.evidence.map((ev, i) => (
                  <div key={i} className="flex items-start gap-3 text-sm">
                    {ev.passed ? (
                      <div className="mt-0.5 bg-success/20 text-success p-1 rounded-full shrink-0"><Check className="h-3 w-3" /></div>
                    ) : (
                      <div className="mt-0.5 bg-destructive/20 text-destructive p-1 rounded-full shrink-0"><AlertTriangle className="h-3 w-3" /></div>
                    )}
                    <div>
                      <span className={cn("font-medium", ev.passed ? "text-foreground" : "text-destructive")}>
                        {ev.explanation}
                      </span>
                      <div className="text-muted-foreground text-xs mt-1">Feature: {ev.feature_name} (Score: {ev.value.toFixed(2)})</div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="flex items-center gap-3 pt-6">
                <Button className="bg-success hover:bg-success/90 text-white font-semibold" onClick={async () => {
                  await api.performExceptionAction(exception.id!, 'APPROVE_MATCH');
                  router.push('/exceptions');
                }}>
                  <ShieldCheck className="h-4 w-4 mr-2" /> Approve Match
                </Button>
                <Button variant="outline" className="border-destructive/30 text-destructive hover:bg-destructive/10 font-semibold" onClick={async () => {
                  await api.performExceptionAction(exception.id!, 'KEEP_EXCEPTION');
                  router.push('/exceptions');
                }}>
                  Keep as Exception
                </Button>
                <Button variant="ghost" className="text-muted-foreground hover:text-foreground" onClick={async () => {
                  await api.performExceptionAction(exception.id!, 'ESCALATE');
                  router.push('/exceptions');
                }}>
                  Escalate
                </Button>
              </div>

            </CardContent>
          </Card>

          {/* AUDIT TIMELINE */}
          <div className="space-y-4 pt-4">
            <h3 className="text-sm font-semibold uppercase tracking-widest text-muted-foreground px-2">Audit Timeline</h3>
            <Card>
              <CardContent className="p-6">
                <div className="space-y-6">
                  <AuditRow time="10:05 AM" action="Reconciliation Started" actor="System" />
                  <AuditRow time="10:05 AM" action="Evidence Collected" actor="Core Engine" />
                  <AuditRow time="10:05 AM" action="Review Created" actor="Policy Engine" />
                  <AuditRow time="Just now" action="Viewed Investigation" actor="Finance Controller" active />
                </div>
              </CardContent>
            </Card>
          </div>

        </div>
      </div>
    </div>
  );
}

function ChainNode({ label, id, amount, status, time, warning = false }: { label: string, id: string, amount: number, status: string, time: string, warning?: boolean }) {
  return (
    <div className="flex items-center gap-4 relative z-10">
      <div className={cn(
        "h-8 w-8 rounded-full flex items-center justify-center shrink-0 border-2 bg-background",
        warning ? "border-destructive text-destructive" : "border-primary text-primary"
      )}>
        {warning ? <AlertTriangle className="h-4 w-4" /> : <Check className="h-4 w-4" />}
      </div>
      <div className={cn(
        "flex-1 border rounded-lg p-3 flex justify-between items-center bg-background shadow-sm transition-colors hover:border-muted-foreground/30",
        warning && "border-destructive/30 bg-destructive/5"
      )}>
        <div>
          <div className="text-xs font-bold text-muted-foreground tracking-wider uppercase mb-1">{label}</div>
          <div className="font-mono text-sm">{id}</div>
          <div className="text-xs text-muted-foreground mt-1 flex items-center gap-2">
            <Clock className="h-3 w-3" /> {time} <span className="bg-muted px-1.5 rounded">{status}</span>
          </div>
        </div>
        <div className={cn(
          "text-lg font-bold tabular-nums",
          warning ? "text-destructive" : "text-foreground"
        )}>
          {formatINR(amount)}
        </div>
      </div>
    </div>
  );
}

function AuditRow({ time, action, actor, active = false }: { time: string, action: string, actor: string, active?: boolean }) {
  return (
    <div className="flex gap-4">
      <div className="text-xs font-mono text-muted-foreground w-16 pt-0.5 shrink-0 text-right">{time}</div>
      <div className="relative pb-6 last:pb-0">
        <div className={cn(
          "absolute left-[5px] top-3 bottom-[-16px] w-px",
          active ? "bg-transparent" : "bg-border"
        )}></div>
        <div className={cn(
          "h-3 w-3 rounded-full border-2 bg-background relative z-10",
          active ? "border-primary" : "border-muted-foreground"
        )}></div>
      </div>
      <div className="-mt-1">
        <div className={cn("text-sm font-semibold", active ? "text-foreground" : "text-muted-foreground")}>{action}</div>
        <div className="text-xs text-muted-foreground mt-0.5">by {actor}</div>
      </div>
    </div>
  );
}
