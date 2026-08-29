"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Search, User, CheckCircle2, Clock } from "lucide-react";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";

interface AuditItem {
  id: string;
  run_id?: string;
  action: string;
  entity_type: string;
  entity_id: string;
  actor: string;
  metadata_json?: Record<string, any>;
  created_at?: string;
}

export default function AuditTrailPage() {
  const [audits, setAudits] = useState<AuditItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterAction, setFilterAction] = useState("ALL");

  useEffect(() => {
    async function loadAudits() {
      try {
        const data = await api.getAuditEvents();
        setAudits(data || []);
      } catch (err) {
        console.error("Failed to load audit events", err);
      } finally {
        setLoading(false);
      }
    }
    loadAudits();
  }, []);

  const filteredAudits = audits.filter(a => {
    const query = searchQuery.toLowerCase().trim();
    const matchesSearch = !query ||
      a.id.toLowerCase().includes(query) ||
      a.action.toLowerCase().includes(query.replace(/ /g, '_')) ||
      a.actor.toLowerCase().includes(query) ||
      a.entity_type.toLowerCase().includes(query) ||
      a.entity_id.toLowerCase().includes(query);

    const matchesAction = filterAction === "ALL" || a.action === filterAction;
    return matchesSearch && matchesAction;
  });

  const uniqueActions = Array.from(new Set(audits.map(a => a.action)));

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
          <div className="flex items-center gap-4 flex-wrap">
            <div className="relative w-full md:w-80">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input 
                placeholder="Search event, actor, or entity..." 
                className="pl-9 bg-background"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <select
              className="text-sm text-muted-foreground border bg-background px-3 py-2 rounded-md hover:bg-muted transition-colors cursor-pointer"
              value={filterAction}
              onChange={(e) => setFilterAction(e.target.value)}
              aria-label="Filter audit action"
            >
              <option value="ALL">All Actions</option>
              {uniqueActions.map(act => (
                <option key={act} value={act}>{act.replace(/_/g, ' ')}</option>
              ))}
            </select>
          </div>
          <div className="text-sm font-medium px-3 py-1 bg-amber-500/10 text-amber-600 rounded-md border border-amber-200">
            Immutable Audit Trail
          </div>
        </CardHeader>
        <CardContent className="p-6">
          {loading ? (
            <div className="py-12 text-center text-muted-foreground flex items-center justify-center gap-2">
              <Clock className="h-5 w-5 animate-spin" /> Loading audit events...
            </div>
          ) : audits.length === 0 ? (
            <div className="py-12 text-center text-muted-foreground space-y-2">
              <CheckCircle2 className="h-8 w-8 mx-auto text-muted-foreground/50" />
              <p className="font-medium">No audit events yet.</p>
              <p className="text-xs">Run a reconciliation batch to generate immutable audit records.</p>
            </div>
          ) : filteredAudits.length === 0 ? (
            <div className="py-12 text-center text-muted-foreground">
              <p>No matching audit events found.</p>
            </div>
          ) : (
            <div className="space-y-6">
              {filteredAudits.map((a, i) => (
                <div key={a.id} className="flex gap-4">
                  <div className="text-xs font-mono text-muted-foreground w-28 pt-0.5 shrink-0 text-right">
                    {a.created_at ? new Date(a.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) : "Just now"}
                  </div>
                  <div className="relative pb-6 last:pb-0">
                    {i !== filteredAudits.length - 1 && (
                      <div className="absolute left-[5px] top-3 bottom-[-16px] w-px bg-border"></div>
                    )}
                    <div className="h-3 w-3 rounded-full border-2 bg-background relative z-10 border-primary"></div>
                  </div>
                  <div className="-mt-1 flex-1">
                    <div className="flex items-center justify-between">
                      <div className="text-sm font-semibold">{a.action.replace(/_/g, ' ')}</div>
                      <Badge variant="outline" className="text-[10px] font-mono text-muted-foreground">{a.id.slice(0, 8)}</Badge>
                    </div>
                    <div className="flex items-center gap-4 text-xs text-muted-foreground mt-1">
                      <span className="flex items-center gap-1"><User className="h-3 w-3" /> {a.actor}</span>
                      <span>Entity: {a.entity_type} ({a.entity_id.slice(0, 8)})</span>
                    </div>
                    {a.metadata_json && (
                      <div className="mt-2 p-2 bg-muted/30 border rounded text-xs font-mono text-muted-foreground">
                        {JSON.stringify(a.metadata_json)}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
      
    </div>
  );
}
