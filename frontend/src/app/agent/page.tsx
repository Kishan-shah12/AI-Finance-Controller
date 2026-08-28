"use client";

import { useState } from "react";
import { formatINR, formatPercent } from "@/lib/utils";
import { api } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { BrainCircuit, Send, Sparkles, User, FileText, CheckCircle2 } from "lucide-react";
import Link from "next/link";

export default function AgentPage() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState<{role: 'user'|'agent', content: any}[]>([
    {
      role: 'agent',
      content: {
        text: "Hello. I am ReconAI, your Finance Controller. I can analyze transactions, explain variances, and verify match confidence using available evidence.",
        suggestions: [
          "Why is today's settlement short?",
          "Show unresolved transactions above ₹10,000.",
          "Which records are safe to auto-close?"
        ]
      }
    }
  ]);

  const handleSend = async () => {
    if (!query.trim()) return;
    
    // Add user message
    const newMessages = [...messages, { role: 'user' as const, content: { text: query } }];
    setMessages(newMessages);
    const currentQuery = query;
    setQuery("");

    try {
      const response = await api.queryAgent(currentQuery);
      
      if (response.status === 'AGENT_UNAVAILABLE') {
        setMessages(prev => [...prev, {
          role: 'agent',
          content: {
            text: response.message || "AI Finance Controller is not configured.",
            unavailable: true
          }
        }]);
      } else {
        setMessages(prev => [...prev, {
          role: 'agent',
          content: {
            text: response.answer,
            evidence: response.evidence,
            confidence: response.confidence,
            provider_metadata: response.provider_metadata,
            recommendation: response.recommended_action
          }
        }]);
      }
    } catch (e) {
      setMessages(prev => [...prev, {
        role: 'agent',
        content: { text: "Error communicating with the agent backend." }
      }]);
    }
  };

  return (
    <div className="flex h-full flex-col max-w-5xl mx-auto animate-in fade-in duration-500">
      
      <div className="p-6 border-b shrink-0 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <BrainCircuit className="h-6 w-6 text-ai" /> AI Finance Controller
          </h1>
          <p className="text-muted-foreground text-sm mt-1">Evidence-backed financial analysis</p>
        </div>
        <Badge variant="outline" className="bg-success/10 text-success border-success/20 flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full bg-success animate-pulse"></span>
          Online
        </Badge>
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-muted/10">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex gap-4 max-w-3xl ${msg.role === 'user' ? 'ml-auto' : ''}`}>
            
            {msg.role === 'agent' && (
              <div className="h-8 w-8 rounded-full bg-ai/10 border border-ai/20 flex items-center justify-center shrink-0">
                <Sparkles className="h-4 w-4 text-ai" />
              </div>
            )}

            <div className={`space-y-4 ${msg.role === 'user' ? 'items-end' : ''}`}>
              
              {msg.content.text && (
                <div className={`p-4 rounded-xl text-sm ${msg.role === 'user' ? 'bg-primary text-primary-foreground rounded-tr-sm' : 'bg-card border shadow-sm rounded-tl-sm'}`}>
                  {msg.content.text}
                </div>
              )}

              {msg.content.calculation && (
                <div className="p-4 rounded-xl border bg-card shadow-sm text-sm font-mono text-muted-foreground">
                  <div className="text-xs font-sans font-bold uppercase tracking-widest mb-2 text-foreground">Calculation</div>
                  {msg.content.calculation}
                </div>
              )}

              {msg.content.evidence && msg.content.evidence.length > 0 ? (
                <div className="p-4 rounded-xl border border-ai/30 bg-ai/5 shadow-sm text-sm">
                  <div className="text-xs font-bold uppercase tracking-widest mb-3 text-ai flex items-center gap-1.5">
                    <FileText className="h-3 w-3" /> Evidence
                  </div>
                  <div className="space-y-2">
                    {msg.content.evidence.map((ev: any, i: number) => {
                      const displayId = ev.exception_id || ev.id || "N/A";
                      const displayText = ev.explanation || ev.reason || ev.feature_name || "Evidence provided";
                      
                      if (ev.exception_id) {
                        return (
                          <Link key={i} href={`/exceptions/${ev.exception_id}`} className="flex items-center gap-2 group">
                            <Badge variant="outline" className="bg-background group-hover:border-ai transition-colors">{displayId.split('-')[0]}</Badge>
                            <span className="text-muted-foreground group-hover:text-foreground transition-colors">{displayText}</span>
                          </Link>
                        );
                      } else {
                        return (
                          <div key={i} className="flex items-center gap-2 opacity-70">
                            <Badge variant="outline" className="bg-background/50">{displayId.split('-')[0]}</Badge>
                            <span className="text-muted-foreground">{displayText}</span>
                          </div>
                        );
                      }
                    })}
                  </div>
                </div>
              ) : msg.content.evidence ? (
                <div className="p-4 rounded-xl border border-muted bg-muted/20 shadow-sm text-sm text-muted-foreground italic">
                  No supporting evidence found for this query.
                </div>
              ) : null}

              {(msg.content.confidence !== undefined || msg.content.provider_metadata) && (
                <div className="flex flex-wrap items-center gap-4 text-sm mt-2 pt-2 border-t border-muted/50">
                  {msg.content.provider_metadata && (
                    <div className="text-xs font-medium text-muted-foreground bg-muted/30 px-2 py-1 rounded">
                      {msg.content.provider_metadata}
                    </div>
                  )}
                  <div className="flex items-center gap-1.5 text-muted-foreground">
                    <span className="font-bold text-foreground">
                      {msg.content.confidence !== null ? formatPercent(msg.content.confidence) : 'Confidence unavailable'}
                    </span>
                    {msg.content.confidence !== null && <span>Evidence confidence</span>}
                  </div>
                  {msg.content.recommendation && (
                    <div className="flex items-center gap-1.5 text-success">
                      <CheckCircle2 className="h-4 w-4" /> {msg.content.recommendation}
                    </div>
                  )}
                </div>
              )}

              {msg.content.suggestions && (
                <div className="flex flex-wrap gap-2 pt-2">
                  {msg.content.suggestions.map((sug: string, i: number) => (
                    <button 
                      key={i} 
                      onClick={() => { setQuery(sug); }}
                      className="text-xs font-medium bg-background border px-3 py-1.5 rounded-full text-muted-foreground hover:text-ai hover:border-ai/50 transition-colors"
                    >
                      {sug}
                    </button>
                  ))}
                </div>
              )}

            </div>

            {msg.role === 'user' && (
              <div className="h-8 w-8 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center shrink-0">
                <User className="h-4 w-4 text-primary" />
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="p-6 border-t bg-background shrink-0">
        <div className="relative max-w-3xl mx-auto">
          <Input 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask your Finance Controller..."
            className="pr-12 h-12 text-base rounded-xl bg-muted/20 border-muted-foreground/20 focus-visible:ring-ai/30 focus-visible:border-ai"
          />
          <Button 
            size="icon" 
            variant="ghost" 
            className="absolute right-1 top-1 h-10 w-10 text-muted-foreground hover:text-ai hover:bg-ai/10"
            onClick={handleSend}
          >
            <Send className="h-5 w-5" />
          </Button>
        </div>
      </div>
      
    </div>
  );
}
