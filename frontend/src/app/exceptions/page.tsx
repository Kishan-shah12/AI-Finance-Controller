"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { ExceptionItem } from "@/lib/types";
import { formatPercent, formatINR, cn } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { AlertTriangle, Search, Filter, CheckCircle2 } from "lucide-react";
import Link from "next/link";
import { Input } from "@/components/ui/input";

export default function ExceptionsPage() {
  const [exceptions, setExceptions] = useState<ExceptionItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const data = await api.getExceptions();
        setExceptions(data);
      } catch (err) {
        console.error("Failed to load exceptions", err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) {
    return <div className="p-8 flex items-center justify-center text-muted-foreground">Loading exceptions queue...</div>;
  }

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Exception Queue</h1>
          <p className="text-muted-foreground mt-1">Review and resolve ambiguous or conflicting financial records.</p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="bg-amber-500/10 text-amber-600 border-amber-200 px-3 py-1 text-xs">
            {exceptions.filter(e => e.decision === "REVIEW").length} Pending Review
          </Badge>
          <Badge variant="outline" className="bg-red-500/10 text-red-600 border-red-200 px-3 py-1 text-xs">
            {exceptions.filter(e => e.decision !== "REVIEW").length} Unresolved
          </Badge>
        </div>
      </div>

      <Card>
        <CardHeader className="border-b pb-4 bg-muted/20">
          <div className="flex items-center justify-between">
            <div className="relative w-72">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input placeholder="Search ID or reason..." className="pl-9 bg-background" />
            </div>
            <button className="flex items-center gap-2 text-sm text-muted-foreground border bg-background px-3 py-2 rounded-md hover:bg-muted transition-colors">
              <Filter className="h-4 w-4" />
              Filter
            </button>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow className="bg-muted/30 hover:bg-muted/30">
                <TableHead className="w-[120px]">Exception ID</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Decision</TableHead>
                <TableHead className="text-right">Confidence</TableHead>
                <TableHead className="text-right">Variance / Amount</TableHead>
                <TableHead className="w-[100px]"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {exceptions.map((ex) => (
                <TableRow key={ex.id} className="group cursor-pointer hover:bg-muted/50 transition-colors">
                  <TableCell className="font-mono text-xs">{ex.id}</TableCell>
                  <TableCell>
                    <div className="font-medium text-sm group-hover:text-primary transition-colors">
                      {ex.exception_type.replace(/_/g, ' ')}
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline" className={cn(
                      "text-[10px]",
                      ex.decision === "REVIEW" ? "text-amber-600 border-amber-200 bg-amber-50" : "text-red-600 border-red-200 bg-red-50"
                    )}>
                      {ex.decision}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    <span className={cn(
                      "text-xs font-semibold px-2 py-1 rounded-md",
                      ex.confidence > 0.8 ? "bg-green-100 text-green-700" :
                      ex.confidence > 0.5 ? "bg-amber-100 text-amber-700" :
                      "bg-red-100 text-red-700"
                    )}>
                      {formatPercent(ex.confidence)}
                    </span>
                  </TableCell>
                  <TableCell className="text-right font-medium">
                    {/* Mock amount or fallback */}
                    {formatINR(ex.variance_details?.amount_difference || 50000)}
                  </TableCell>
                  <TableCell className="text-right">
                    <Link href={`/exceptions/${ex.id}`}>
                      <button className="text-xs font-semibold text-primary hover:underline">
                        Investigate
                      </button>
                    </Link>
                  </TableCell>
                </TableRow>
              ))}
              {exceptions.length === 0 && (
                <TableRow>
                  <TableCell colSpan={6} className="h-32 text-center text-muted-foreground">
                    <div className="flex flex-col items-center justify-center gap-2">
                      <CheckCircle2 className="h-8 w-8 text-success opacity-50" />
                      <p>All clear. No unresolved exceptions.</p>
                    </div>
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
