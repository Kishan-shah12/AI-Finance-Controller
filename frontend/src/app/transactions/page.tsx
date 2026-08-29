"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Search, Filter, Database, ArrowRight } from "lucide-react";
import { Input } from "@/components/ui/input";
import Link from "next/link";
import { formatINR } from "@/lib/utils";

export default function TransactionsPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [decisionFilter, setDecisionFilter] = useState("ALL");
  const txs = [
    { id: "TX-9021", order: "ORD-123", amount: 4500, decision: "VERIFIED_MATCH", conf: 0.99, exception_id: null },
    { id: "TX-9022", order: "ORD-124", amount: 12000, decision: "MATCH_WITH_EXPLAINABLE_VARIANCE", conf: 0.95, exception_id: null },
    { id: "TX-9023", order: "ORD-125", amount: 50000, decision: "REVIEW", conf: 0.65, exception_id: null },
    { id: "TX-9024", order: "ORD-126", amount: 8900, decision: "VERIFIED_MATCH", conf: 0.98, exception_id: null },
    { id: "TX-9025", order: "ORD-127", amount: 145000, decision: "UNRESOLVED", conf: 0.20, exception_id: null },
  ];

  const filteredTxs = txs.filter((tx) => {
    const query = searchQuery.toLowerCase().trim();
    const matchesSearch =
      !query ||
      tx.id.toLowerCase().includes(query) ||
      tx.order.toLowerCase().includes(query) ||
      tx.decision.toLowerCase().includes(query.replace(/ /g, '_'));

    const matchesDecision =
      decisionFilter === "ALL" || tx.decision === decisionFilter;

    return matchesSearch && matchesDecision;
  });

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6 animate-in fade-in duration-500">
      
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold tracking-tight">Transaction Explorer</h1>
            <Badge variant="outline" className="bg-primary/10 text-primary border-primary/20">DEMO SAMPLE DATA</Badge>
          </div>
          <p className="text-muted-foreground mt-1">Drill into individual canonical financial chains.</p>
        </div>
      </div>

      <Card>
        <CardHeader className="border-b pb-4 bg-muted/10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="relative w-full md:w-80">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search Order ID, Payment ID, UTR..."
                className="pl-9 bg-background"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <div className="flex items-center gap-2">
              <select
                className="flex items-center gap-2 text-sm text-muted-foreground border bg-background px-3 py-2 rounded-md hover:bg-muted transition-colors appearance-none cursor-pointer"
                value={decisionFilter}
                onChange={(e) => setDecisionFilter(e.target.value)}
              >
                <option value="ALL">All Decisions</option>
                <option value="VERIFIED_MATCH">Verified Match</option>
                <option value="MATCH_WITH_EXPLAINABLE_VARIANCE">Match with Explainable Variance</option>
                <option value="REVIEW">Review</option>
                <option value="UNRESOLVED">Unresolved</option>
              </select>
            </div>
          </div>
          <div className="text-sm text-muted-foreground flex items-center gap-2">
            <Database className="h-4 w-4" />
            Showing latest 500 records
          </div>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader className="bg-muted/30">
              <TableRow>
                <TableHead>Transaction ID</TableHead>
                <TableHead>Source Order</TableHead>
                <TableHead className="text-right">Amount</TableHead>
                <TableHead>Confidence</TableHead>
                <TableHead>Decision</TableHead>
                <TableHead className="w-[50px]"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredTxs.map((tx) => (
                <TableRow key={tx.id} className="group cursor-pointer">
                  <TableCell className="font-medium font-mono text-xs">{tx.id}</TableCell>
                  <TableCell className="font-mono text-xs text-muted-foreground">{tx.order}</TableCell>
                  <TableCell className="text-right">{formatINR(tx.amount)}</TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <div className="h-1.5 w-16 bg-muted rounded-full overflow-hidden">
                        <div 
                          className={`h-full ${tx.conf > 0.9 ? 'bg-success' : tx.conf > 0.6 ? 'bg-amber-500' : 'bg-destructive'}`} 
                          style={{ width: `${tx.conf * 100}%` }}
                        />
                      </div>
                      <span className="text-xs text-muted-foreground">{Math.round(tx.conf * 100)}%</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline" className={
                      tx.decision === "VERIFIED_MATCH" ? "bg-success/10 text-success border-success/20" :
                      tx.decision === "MATCH_WITH_EXPLAINABLE_VARIANCE" ? "bg-indigo-500/10 text-indigo-600 border-indigo-500/20" :
                      tx.decision === "REVIEW" ? "bg-amber-500/10 text-amber-600 border-amber-500/20" :
                      "bg-destructive/10 text-destructive border-destructive/20"
                    }>
                      {tx.decision}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {tx.exception_id && (tx.decision === "REVIEW" || tx.decision === "UNRESOLVED") ? (
                      <Link href={`/exceptions/${tx.exception_id}`}>
                        <ArrowRight className="h-4 w-4 text-muted-foreground group-hover:text-primary" />
                      </Link>
                    ) : (
                      <ArrowRight className="h-4 w-4 text-muted-foreground/30" />
                    )}
                  </TableCell>
                </TableRow>
              ))}
              {filteredTxs.length === 0 && (
                <TableRow>
                  <TableCell colSpan={6} className="h-32 text-center text-muted-foreground">
                    <p>No matching transactions found.</p>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
      
    </div>
  );
}
