"use client";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Search, Filter, Database, ArrowRight } from "lucide-react";
import { Input } from "@/components/ui/input";
import Link from "next/link";
import { formatINR } from "@/lib/utils";

export default function TransactionsPage() {
  // Mock transactions for UI layout
  const txs = [
    { id: "TX-9021", order: "ORD-123", amount: 4500, decision: "VERIFIED_MATCH", conf: 0.99 },
    { id: "TX-9022", order: "ORD-124", amount: 12000, decision: "MATCH_WITH_EXPLAINABLE_VARIANCE", conf: 0.95 },
    { id: "TX-9023", order: "ORD-125", amount: 50000, decision: "REVIEW", conf: 0.65 },
    { id: "TX-9024", order: "ORD-126", amount: 8900, decision: "VERIFIED_MATCH", conf: 0.98 },
    { id: "TX-9025", order: "ORD-127", amount: 145000, decision: "UNRESOLVED", conf: 0.20 },
  ];

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6 animate-in fade-in duration-500">
      
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Transaction Explorer</h1>
          <p className="text-muted-foreground mt-1">Drill into individual financial chains.</p>
        </div>
      </div>

      <Card>
        <CardHeader className="border-b pb-4 bg-muted/10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="relative w-full md:w-80">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input placeholder="Search Order ID, Payment ID, UTR..." className="pl-9 bg-background" />
            </div>
            <button className="flex items-center gap-2 text-sm text-muted-foreground border bg-background px-3 py-2 rounded-md hover:bg-muted transition-colors whitespace-nowrap">
              <Filter className="h-4 w-4" />
              Filters
            </button>
          </div>
          <div className="text-sm text-muted-foreground flex items-center gap-2">
            <Database className="h-4 w-4" />
            Showing latest 500 records
          </div>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow className="bg-muted/30 hover:bg-muted/30">
                <TableHead className="w-[120px]">Scenario ID</TableHead>
                <TableHead>Order Ref</TableHead>
                <TableHead className="text-right">Amount</TableHead>
                <TableHead>Decision</TableHead>
                <TableHead className="w-[50px]"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {txs.map((tx) => (
                <TableRow key={tx.id} className="group cursor-pointer hover:bg-muted/50 transition-colors">
                  <TableCell className="font-mono text-xs">{tx.id}</TableCell>
                  <TableCell className="font-mono text-xs text-muted-foreground">{tx.order}</TableCell>
                  <TableCell className="text-right font-medium">{formatINR(tx.amount)}</TableCell>
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
                    {tx.decision === "REVIEW" || tx.decision === "UNRESOLVED" ? (
                      <Link href={`/exceptions/${tx.id}`}>
                        <ArrowRight className="h-4 w-4 text-muted-foreground group-hover:text-primary" />
                      </Link>
                    ) : (
                      <ArrowRight className="h-4 w-4 text-muted-foreground/30" />
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
      
    </div>
  );
}
