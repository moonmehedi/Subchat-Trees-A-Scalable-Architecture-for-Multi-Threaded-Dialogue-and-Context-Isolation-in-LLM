"""
Dataset Testing Logger

Specialized logging for dataset execution with test validation,
context isolation tracking, and detailed result analysis.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from colorama import Fore, Style, init

# Initialize colorama for colored terminal output
init(autoreset=True)


class DatasetLogger:
    """Logger for dataset testing with validation and reporting."""
    
    def __init__(self, log_dir: str = "logs/dataset-results"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        self.scenarios_dir = self.log_dir / "scenarios"
        self.scenarios_dir.mkdir(exist_ok=True)
        
        # Test results tracking
        self.test_results = []
        self.current_scenario = None
        self.scenario_start_time = None
        
    def start_scenario(self, scenario_name: str, description: str):
        """Start tracking a new scenario."""
        self.current_scenario = {
            "name": scenario_name,
            "description": description,
            "start_time": datetime.now().isoformat(),
            "tests": [],
            "status": "running"
        }
        self.scenario_start_time = datetime.now()
        
        # Print header
        print(f"\n{'='*80}")
        print(f"{Fore.CYAN}🧪 SCENARIO: {scenario_name}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{description}{Style.RESET_ALL}")
        print(f"{'='*80}\n")
        
    def log_message(self, step: int, node_type: str, message: str, response: str):
        """Log a message exchange."""
        timestamp = datetime.now().isoformat()
        
        print(f"{Fore.YELLOW}[Step {step}] {node_type.upper()}{Style.RESET_ALL}")
        print(f"  {Fore.WHITE}User: {message[:80]}...{Style.RESET_ALL}" if len(message) > 80 else f"  {Fore.WHITE}User: {message}{Style.RESET_ALL}")
        print(f"  {Fore.GREEN}AI: {response[:80]}...{Style.RESET_ALL}\n" if len(response) > 80 else f"  {Fore.GREEN}AI: {response}{Style.RESET_ALL}\n")
        
    def log_action(self, step: int, action: str, details: str):
        """Log a non-message action (create subchat, switch node, etc.)."""
        print(f"{Fore.MAGENTA}[Step {step}] ACTION: {action}{Style.RESET_ALL}")
        print(f"  {Fore.WHITE}{details}{Style.RESET_ALL}\n")
        
    def validate_test(
        self, 
        step: int,
        test_type: str,
        query: str,
        response: str,
        expected_contains: Optional[List[str]] = None,
        should_not_contain: Optional[List[str]] = None,
        expected_retrieval: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Validate a test and return results.
        
        Args:
            step: Step number
            test_type: Type of test (retrieval, context_isolation, etc.)
            query: User query
            response: AI response
            expected_contains: Keywords that should be in response
            should_not_contain: Keywords that should NOT be in response
            expected_retrieval: Keywords that should have been retrieved
            
        Returns:
            Dict with test results
        """
        result = {
            "step": step,
            "type": test_type,
            "query": query,
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "passed": True,
            "failures": []
        }
        
        response_lower = response.lower()
        
        # Check expected keywords
        if expected_contains:
            for keyword in expected_contains:
                if keyword.lower() not in response_lower:
                    result["passed"] = False
                    result["failures"].append(f"Missing expected keyword: '{keyword}'")
        
        # Check forbidden keywords (context isolation)
        if should_not_contain:
            for keyword in should_not_contain:
                if keyword.lower() in response_lower:
                    result["passed"] = False
                    result["failures"].append(f"Found forbidden keyword: '{keyword}' (context pollution)")
        
        # Check retrieval keywords
        if expected_retrieval:
            for keyword in expected_retrieval:
                if keyword.lower() not in response_lower:
                    result["passed"] = False
                    result["failures"].append(f"Expected retrieval keyword not found: '{keyword}'")
        
        # Add to current scenario
        if self.current_scenario:
            self.current_scenario["tests"].append(result)
        
        # Print result
        if result["passed"]:
            print(f"{Fore.GREEN}✅ TEST PASSED{Style.RESET_ALL} (Step {step}): {test_type}")
        else:
            print(f"{Fore.RED}❌ TEST FAILED{Style.RESET_ALL} (Step {step}): {test_type}")
            for failure in result["failures"]:
                print(f"  {Fore.RED}└─ {failure}{Style.RESET_ALL}")
        print()
        
        return result
        
    def end_scenario(self):
        """End current scenario and save results."""
        if not self.current_scenario:
            return
            
        # Calculate duration
        duration = (datetime.now() - self.scenario_start_time).total_seconds()
        self.current_scenario["duration_seconds"] = duration
        self.current_scenario["end_time"] = datetime.now().isoformat()
        
        # Calculate pass/fail
        total_tests = len(self.current_scenario["tests"])
        passed_tests = sum(1 for t in self.current_scenario["tests"] if t["passed"])
        failed_tests = total_tests - passed_tests
        
        self.current_scenario["total_tests"] = total_tests
        self.current_scenario["passed"] = passed_tests
        self.current_scenario["failed"] = failed_tests
        self.current_scenario["status"] = "completed"
        
        # Save scenario log
        scenario_file = self.scenarios_dir / f"{self.current_scenario['name'].replace(' ', '_')}.json"
        with open(scenario_file, 'w') as f:
            json.dump(self.current_scenario, f, indent=2)
        
        # Print summary
        print(f"\n{'-'*80}")
        print(f"{Fore.CYAN}📊 SCENARIO SUMMARY: {self.current_scenario['name']}{Style.RESET_ALL}")
        print(f"  Duration: {duration:.2f}s")
        print(f"  Total Tests: {total_tests}")
        if failed_tests == 0:
            print(f"  {Fore.GREEN}✅ Passed: {passed_tests}/{total_tests} (100%){Style.RESET_ALL}")
        else:
            pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
            print(f"  {Fore.GREEN}✅ Passed: {passed_tests}{Style.RESET_ALL}")
            print(f"  {Fore.RED}❌ Failed: {failed_tests} ({100-pass_rate:.1f}%){Style.RESET_ALL}")
        print(f"{'-'*80}\n")
        
        # Add to global results
        self.test_results.append(self.current_scenario)
        self.current_scenario = None
        
    def generate_final_report(self) -> str:
        """Generate comprehensive final report."""
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("📋 DATASET TESTING FINAL REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # Overall statistics
        total_scenarios = len(self.test_results)
        total_tests = sum(s["total_tests"] for s in self.test_results)
        total_passed = sum(s["passed"] for s in self.test_results)
        total_failed = sum(s["failed"] for s in self.test_results)
        overall_pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        total_duration = sum(s["duration_seconds"] for s in self.test_results)
        
        report_lines.append("📊 OVERALL STATISTICS")
        report_lines.append("-" * 80)
        report_lines.append(f"Total Scenarios: {total_scenarios}")
        report_lines.append(f"Total Tests: {total_tests}")
        report_lines.append(f"✅ Passed: {total_passed} ({overall_pass_rate:.1f}%)")
        report_lines.append(f"❌ Failed: {total_failed} ({100-overall_pass_rate:.1f}%)")
        report_lines.append(f"⏱️  Total Duration: {total_duration:.2f}s ({total_duration/60:.2f} minutes)")
        report_lines.append("")
        
        # Per-scenario breakdown
        report_lines.append("🧪 SCENARIO BREAKDOWN")
        report_lines.append("-" * 80)
        
        for i, scenario in enumerate(self.test_results, 1):
            status_icon = "✅" if scenario["failed"] == 0 else "❌"
            pass_rate = (scenario["passed"] / scenario["total_tests"] * 100) if scenario["total_tests"] > 0 else 0
            
            report_lines.append(f"\n{i}. {status_icon} {scenario['name']}")
            report_lines.append(f"   Tests: {scenario['passed']}/{scenario['total_tests']} passed ({pass_rate:.1f}%)")
            report_lines.append(f"   Duration: {scenario['duration_seconds']:.2f}s")
            
            # List failures
            if scenario["failed"] > 0:
                report_lines.append(f"   Failures:")
                for test in scenario["tests"]:
                    if not test["passed"]:
                        report_lines.append(f"     ❌ Step {test['step']}: {test['type']}")
                        for failure in test["failures"]:
                            report_lines.append(f"        └─ {failure}")
        
        report_lines.append("")
        report_lines.append("=" * 80)
        
        # Determine overall result
        if total_failed == 0:
            report_lines.append(f"🎉 {Fore.GREEN}ALL TESTS PASSED!{Style.RESET_ALL}")
            report_lines.append("The hierarchical subchat system is working perfectly! ✨")
        else:
            report_lines.append(f"⚠️  {Fore.YELLOW}SOME TESTS FAILED{Style.RESET_ALL}")
            report_lines.append(f"Please review the failures above and check logs for details.")
        
        report_lines.append("=" * 80)
        
        report_text = "\n".join(report_lines)
        
        # Save report
        report_file = self.log_dir / f"FINAL_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, 'w') as f:
            f.write(report_text)
        
        # Also save JSON version
        json_file = self.log_dir / f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "total_scenarios": total_scenarios,
                "total_tests": total_tests,
                "passed": total_passed,
                "failed": total_failed,
                "pass_rate": overall_pass_rate,
                "total_duration": total_duration,
                "scenarios": self.test_results
            }, f, indent=2)
        
        print(report_text)
        print(f"\n📄 Report saved to: {report_file}")
        print(f"📄 JSON results saved to: {json_file}")
        
        return report_text
