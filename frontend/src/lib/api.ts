import axios from "axios";
import { MetricData, ExceptionItem } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const api = {
  getEvaluationMetrics: async (): Promise<MetricData> => {
    try {
      const response = await apiClient.get<MetricData>("/evaluation/final");
      return response.data;
    } catch (error) {
      console.error("Failed to fetch evaluation metrics:", error);
      throw error;
    }
  },
  
  getExceptions: async (): Promise<ExceptionItem[]> => {
    try {
      const response = await apiClient.get<ExceptionItem[]>("/exceptions");
      return response.data;
    } catch (error) {
      console.error("Failed to fetch exceptions:", error);
      throw error;
    }
  },
  
  getExceptionDetail: async (id: string): Promise<ExceptionItem> => {
    try {
      const response = await apiClient.get<ExceptionItem>(`/exceptions/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch exception ${id}:`, error);
      throw error;
    }
  },

  performExceptionAction: async (id: string, action: string): Promise<void> => {
    try {
      await apiClient.post(`/exceptions/${id}/action`, { action });
    } catch (error) {
      console.error(`Failed to perform action ${action} on ${id}:`, error);
      throw error;
    }
  },

  startReconciliationRun: async (mode: 'demo' | 'evaluation' = 'demo', provider: 'SYNTHETIC' | 'RAZORPAY_TEST' = 'SYNTHETIC'): Promise<any> => {
    try {
      const response = await apiClient.post("/reconciliation/run", {
        mode,
        provider,
        size: 1000,
        seed: 42
      });
      return response.data;
    } catch (error) {
      console.error("Failed to start run:", error);
      throw error;
    }
  },

  getRazorpayStatus: async (): Promise<any> => {
    try {
      const response = await apiClient.get("/providers/razorpay/status");
      return response.data;
    } catch (error) {
      console.error("Failed to fetch Razorpay status:", error);
      return { configured: false, message: "Backend unreachable" };
    }
  },

  getReconciliationRunStatus: async (runId: string): Promise<any> => {
    try {
      const response = await apiClient.get(`/reconciliation/runs/${runId}`);
      return response.data;
    } catch (error) {
      console.error("Failed to fetch run status:", error);
      throw error;
    }
  },

  getLatestDemoRun: async (): Promise<any> => {
    try {
      const response = await apiClient.get("/reconciliation/demo/latest");
      return response.data;
    } catch (error) {
      console.error("Failed to fetch latest demo run:", error);
      throw error;
    }
  },

  getHighestPriorityExceptionId: async (runId: string): Promise<string | null> => {
    try {
      const response = await apiClient.get(`/exceptions/run/${runId}/highest-priority`);
      return response.data.id;
    } catch (error) {
      console.error("Failed to fetch highest priority exception:", error);
      return null; // Graceful fallback
    }
  },

  queryAgent: async (query: string, context?: any): Promise<any> => {
    try {
      const response = await apiClient.post("/agent/query", {
        query,
        context
      });
      return response.data;
    } catch (error) {
      console.error("Failed to query agent:", error);
      throw error;
    }
  }
};
