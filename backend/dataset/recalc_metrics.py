#!/usr/bin/env python3
"""
Recalculate metrics from stored results without re-running tests
"""
import json
import sys
from pathlib import Path

# Import the test runner to use its metric calculation methods
from kaggle_serverless_runner import ServerlessTestRunner

def main():
    buffer_size = 10  # Changed to 10
    runner = ServerlessTestRunner()
    runner.current_buffer_size = buffer_size
    
    # Load stored results
    results_dir = Path(__file__).parent / "logs" / "tables" / f"buffer_{buffer_size}"
    
    baseline_file = results_dir / "raw_metrics_baseline.json"
    system_file = results_dir / "raw_metrics_system.json"
    
    if not baseline_file.exists() or not system_file.exists():
        print(f"❌ Results files not found for buffer {buffer_size}")
        print(f"   Looking for: {baseline_file}")
        print(f"   Looking for: {system_file}")
        return 1
    
    with open(baseline_file) as f:
        baseline_results = json.load(f)
    
    with open(system_file) as f:
        system_results = json.load(f)
    
    print(f"\n📊 Recalculating metrics for buffer {buffer_size}")
    print(f"   Baseline results: {len(baseline_results)} steps")
    print(f"   System results: {len(system_results)} steps")
    
    # Calculate metrics using the runner's method
    metrics = runner.calculate_metrics(baseline_results, system_results)
    
    # Generate tables (uses self.current_buffer_size internally)
    runner.generate_table(metrics)
    
    tables_dir = results_dir  # Tables are already in this dir
    
    print(f"\n✅ Metrics recalculated and saved to {tables_dir}")
    print(f"\n📊 KEY RESULTS:")
    print(f"   Baseline Accuracy: {metrics['table_1']['baseline']['accuracy']:.1f}%")
    print(f"   System Accuracy: {metrics['table_1']['system']['accuracy']:.1f}%")
    print(f"   Baseline Latency: {metrics['table_3']['baseline']['avg_latency']:.2f}s")
    print(f"   System Latency: {metrics['table_3']['system']['avg_latency']:.2f}s")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
