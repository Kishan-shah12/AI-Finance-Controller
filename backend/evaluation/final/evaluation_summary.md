# Final Evaluation Summary

These metrics were measured on a locked synthetic test set and were not used for model or threshold tuning.
The dataset is synthetic and designed for hackathon evaluation.

### Model & Configuration
- **Model Version**: trained_v1
- **Auto-Match Threshold**: 0.8
- **Review Threshold**: 0.4
- **Ambiguity Margin**: 0.02

### Standard ML Metrics
- **Standard Precision**: 100.00%
- **Overall Match Recall**: 78.79%
- **Standard F1 Score**: 88.14%
- **False-Match Rate**: 0.00%

### Operational Metrics (Business Focus)
- **Operational Match Rate**: 69.33%
- **Strict Verified Match Rate**: 48.67%
- **Auto-Match Rate**: 69.33%
- **Review Rate**: 3.33%
- **Exception Rate**: 27.33%

### Custom Safe-Automation Metrics
- **Auto-Match Precision**: 100.00% (same as standard precision)
- **Safe Auto-Match Recall**: 100.00% (Denominator restricted to safely auto-matchable scenarios)

### Throughput
- **Core Engine**: 179906.81 records/s
- **End-to-End**: not measured
