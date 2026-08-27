export interface MetricData {
  dataset_version: string;
  model_version: string;
  total_scenarios: number;
  operational_match_rate: number;
  strict_verified_match_rate: number;
  auto_match_rate: number;
  standard_precision: number;
  overall_match_recall: number;
  standard_f1: number;
  safe_auto_match_precision: number;
  safe_auto_match_recall: number;
  false_match_rate: number;
  review_rate: number;
  exception_rate: number;
  core_engine_throughput: number;
}

export interface ExceptionEvidence {
  feature_name: string;
  value: number;
  threshold?: number;
  passed: boolean;
  explanation: string;
}

export interface ExceptionItem {
  id?: string; // added dynamically by frontend if not present
  decision: string;
  exception_type: string;
  confidence: number;
  evidence: ExceptionEvidence[];
  variance_details?: Record<string, any>;
}
