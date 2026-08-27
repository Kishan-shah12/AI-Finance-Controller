"use client";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Search, Filter, History, User } from "lucide-react";
import { Input } from "@/components/ui/input";

export default function AuditTrailPage() {
  const audits = [
    { id: "EVT-001", action: "REPORT_GENERATED", entity: "Batch-902", actor: "Finance Controller", time: "10:30 AM", meta: "Evaluation report finalized" },
    { id: "EVT-002", action: "REVIEW_COMPLETED", entity: "EX-1042", actor: "Finance Controller", time: "10:28 AM", meta: "Matched manually. Evidence overridden." },
    { id: "EVT-003", action: "EXCEPTION_CREATED", entity: "EX-1042", actor: "Policy Engine", time: "10:05 AM", meta: "Low confidence on fee variance." },
    { id: "EVT-004", action: "MATCH_DECISION", entity: "TX-9021", actor: "Recon Engine v1", time: "10:04 AM", meta: "Confidence: 0.99" },
    { id: "EVT-005", action: "RECORDS_PROCESSED", entity: "Batch-902", actor: "System", time: "10:02 AM", meta: "1,000 records ingested" },
    { id: "EVT-006", action: "RECONCILIATION_STARTED", entity: "Batch-902", actor: "System Schedule", time: "10:00 AM", meta: "Daily trigger" },
  ];

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-6 animate-in fade-in duration-500">
      
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Audit Trail</h1>
          <p className="text-muted-foreground mt-1">Immutable timeline of system and user events.</p>
        </div>
      </div>

      <Card>
        <CardHeader className="border-b pb-4 bg-muted/10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="relative w-full md:w-80">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input placeholder="Search event, actor, or entity..." className="pl-9 bg-background" />
            </div>
            <button className="flex items-center gap-2 text-sm text-muted-foreground border bg-background px-3 py-2 rounded-md hover:bg-muted transition-colors whitespace-nowrap">
              <Filter className="h-4 w-4" />
              Filters
            </button>
          </div>
          <div className="text-sm font-medium px-3 py-1 bg-amber-500/10 text-amber-600 rounded-md border border-amber-200">
            Read-only mode
          </div>
        </CardHeader>
        <CardContent className="p-6">
          <div className="space-y-6">
            {audits.map((a, i) => (
              <div key={a.id} className="flex gap-4">
                <div className="text-xs font-mono text-muted-foreground w-20 pt-0.5 shrink-0 text-right">{a.time}</div>
                <div className="relative pb-6 last:pb-0">
                  {i !== audits.length - 1 && (
                    <div className="absolute left-[5px] top-3 bottom-[-16px] w-px bg-border"></div>
                  )}
                  <div className="h-3 w-3 rounded-full border-2 bg-background relative z-10 border-muted-foreground"></div>
                </div>
                <div className="-mt-1 flex-1">
                  <div className="flex items-center justify-between">
                    <div className="text-sm font-semibold">{a.action.replace(/_/g, ' ')}</div>
                    <Badge variant="outline" className="text-[10px] font-mono text-muted-foreground">{a.id}</Badge>
                  </div>
                  <div className="flex items-center gap-4 text-xs text-muted-foreground mt-1">
                    <span className="flex items-center gap-1"><User className="h-3 w-3" /> {a.actor}</span>
                    <span>Entity: {a.entity}</span>
                  </div>
                  <div className="mt-2 p-2 bg-muted/30 border rounded text-xs font-mono text-muted-foreground">
                    {a.meta}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
      
    </div>
  );
}
