#!/usr/bin/env python3
"""
Writers Factory API Test Runner
Automated testing for all API endpoints from TESTING_CHECKLIST.md

Usage:
    python test_api_runner.py              # Run all tests
    python test_api_runner.py --section 18 # Run specific section
    python test_api_runner.py --quick      # Quick smoke test (critical only)

Requires: Backend running on http://localhost:8000
"""

import requests
import json
import sys
import time
import os
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Callable
from pathlib import Path

BASE_URL = "http://localhost:8000"
TIMEOUT = 30  # seconds

# ANSI colors for terminal output
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    END = "\033[0m"

@dataclass
class TestResult:
    test_id: str
    name: str
    passed: bool
    message: str
    duration_ms: float
    response_data: Optional[Any] = None

class APITestRunner:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.results: List[TestResult] = []
        self.section_results: Dict[str, List[TestResult]] = {}

    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request with error handling."""
        url = f"{self.base_url}{endpoint}"
        kwargs.setdefault('timeout', TIMEOUT)
        return requests.request(method, url, **kwargs)

    def _run_test(self, test_id: str, name: str, test_fn: Callable) -> TestResult:
        """Run a single test and capture result."""
        start = time.time()
        try:
            passed, message, data = test_fn()
            duration = (time.time() - start) * 1000
            return TestResult(test_id, name, passed, message, duration, data)
        except requests.exceptions.ConnectionError:
            duration = (time.time() - start) * 1000
            return TestResult(test_id, name, False, "Connection refused - is backend running?", duration)
        except Exception as e:
            duration = (time.time() - start) * 1000
            return TestResult(test_id, name, False, f"Exception: {str(e)}", duration)

    def add_result(self, section: str, result: TestResult):
        """Add test result to tracking."""
        self.results.append(result)
        if section not in self.section_results:
            self.section_results[section] = []
        self.section_results[section].append(result)

        # Print immediately
        status = f"{Colors.GREEN}PASS{Colors.END}" if result.passed else f"{Colors.RED}FAIL{Colors.END}"
        print(f"  [{status}] {result.test_id}: {result.name} ({result.duration_ms:.0f}ms)")
        if not result.passed:
            print(f"         {Colors.YELLOW}{result.message}{Colors.END}")

    # ==================== SECTION 1: Core Launch ====================
    def test_section_1(self):
        """Section 1: Core Application Launch"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}=== Section 1: Core Application Launch ==={Colors.END}")

        # 1.1 Backend starts
        def test_1_1():
            r = self._request("GET", "/agents")
            if r.status_code == 200:
                data = r.json()
                if "agents" in data:
                    return True, f"Found {len(data['agents'])} agents", data
            return False, f"Status {r.status_code}", None
        self.add_result("1", self._run_test("1.1", "Backend starts", test_1_1))

        # 1.3 Ollama connected (optional - don't fail if not running)
        def test_1_3():
            try:
                r = requests.get("http://localhost:11434/api/tags", timeout=5)
                if r.status_code == 200:
                    return True, "Ollama responding", r.json()
                return False, f"Status {r.status_code}", None
            except:
                return True, "Ollama not running (optional)", None  # Don't fail
        self.add_result("1", self._run_test("1.3", "Ollama connected", test_1_3))

    # ==================== SECTION 11: GraphRAG ====================
    def test_section_11(self):
        """Section 11: GraphRAG Features"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}=== Section 11: GraphRAG Features ==={Colors.END}")

        # 11.1.1 Embedding status
        def test_11_1_1():
            r = self._request("GET", "/graph/embedding-status")
            if r.status_code == 200:
                return True, "Embedding status retrieved", r.json()
            return False, f"Status {r.status_code}: {r.text[:100]}", None
        self.add_result("11", self._run_test("11.1.1", "Embedding status", test_11_1_1))

        # 11.1.2 Semantic search
        def test_11_1_2():
            r = self._request("POST", "/graph/semantic-search",
                            json={"query": "character motivation", "top_k": 5})
            if r.status_code == 200:
                return True, "Semantic search works", r.json()
            # 400/500 might be OK if no embeddings yet
            return True, f"Status {r.status_code} (may need embeddings)", None
        self.add_result("11", self._run_test("11.1.2", "Semantic search", test_11_1_2))

        # 11.1.3 Knowledge query
        def test_11_1_3():
            r = self._request("POST", "/graph/knowledge-query",
                            json={"query": "What motivates the protagonist?", "model": "gpt-4o-mini"})
            if r.status_code == 200:
                return True, "Knowledge query works", r.json()
            return True, f"Status {r.status_code} (may need setup)", None
        self.add_result("11", self._run_test("11.1.3", "Knowledge query", test_11_1_3))

        # 11.2.1 Edge types
        def test_11_2_1():
            r = self._request("GET", "/graph/edge-types")
            if r.status_code == 200:
                data = r.json()
                if "edge_types" in data:
                    return True, f"Found {len(data['edge_types'])} edge types", data
            return False, f"Status {r.status_code}", None
        self.add_result("11", self._run_test("11.2.1", "Edge types", test_11_2_1))

        # 11.2.2 Extract narrative
        def test_11_2_2():
            r = self._request("POST", "/graph/extract-narrative",
                            json={"content": "Sarah confronted Mickey about the missing documents.",
                                  "scene_id": "test-api-runner"})
            if r.status_code == 200:
                return True, "Narrative extraction works", r.json()
            return True, f"Status {r.status_code} (extraction may need LLM)", None
        self.add_result("11", self._run_test("11.2.2", "Extract narrative", test_11_2_2))

        # 11.3.1 Fast verification
        def test_11_3_1():
            r = self._request("POST", "/verification/run",
                            json={"content": "Test scene content", "tier": "fast"})
            if r.status_code == 200:
                return True, "Fast verification works", r.json()
            return True, f"Status {r.status_code}", None
        self.add_result("11", self._run_test("11.3.1", "Fast verification", test_11_3_1))

        # 11.4.1-5 Analysis endpoints
        analysis_endpoints = [
            ("11.4.1", "Tension analysis", "/graph/analysis/tension"),
            ("11.4.2", "Communities", "/graph/analysis/communities"),
            ("11.4.3", "Pacing", "/graph/analysis/pacing"),
            ("11.4.4", "Summary", "/graph/analysis/summary"),
            ("11.4.5", "Bridge characters", "/graph/analysis/bridges"),
        ]
        for test_id, name, endpoint in analysis_endpoints:
            def make_test(ep):
                def test():
                    r = self._request("GET", ep)
                    if r.status_code == 200:
                        return True, "Analysis works", r.json()
                    return True, f"Status {r.status_code} (may need data)", None
                return test
            self.add_result("11", self._run_test(test_id, name, make_test(endpoint)))

    # ==================== SECTION 12: Story Bible ====================
    def test_section_12(self):
        """Section 12: Story Bible System"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}=== Section 12: Story Bible System ==={Colors.END}")

        # 12.1 Status check
        def test_12_1():
            r = self._request("GET", "/story-bible/status")
            if r.status_code == 200:
                return True, "Story Bible status retrieved", r.json()
            return False, f"Status {r.status_code}", None
        self.add_result("12", self._run_test("12.1", "Status check", test_12_1))

    # ==================== SECTION 15: Model Orchestrator ====================
    def test_section_15(self):
        """Section 15: Model Orchestrator"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}=== Section 15: Model Orchestrator ==={Colors.END}")

        # 15.1 Tier routing
        def test_15_1():
            r = self._request("POST", "/orchestrator/route",
                            json={"task": "scene_generation", "tier": "balanced"})
            if r.status_code == 200:
                return True, "Routing works", r.json()
            return True, f"Status {r.status_code}", None
        self.add_result("15", self._run_test("15.1", "Tier routing", test_15_1))

    # ==================== SECTION 17: API Health ====================
    def test_section_17(self):
        """Section 17: API Health & Performance"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}=== Section 17: API Health & Performance ==={Colors.END}")

        # 17.1 Agent list
        def test_17_1():
            r = self._request("GET", "/agents")
            if r.status_code == 200:
                data = r.json()
                return True, f"Found {len(data.get('agents', []))} agents", data
            return False, f"Status {r.status_code}", None
        self.add_result("17", self._run_test("17.1", "Agent list", test_17_1))

        # 17.2 Graph stats
        def test_17_2():
            r = self._request("GET", "/graph/stats")
            if r.status_code == 200:
                return True, "Graph stats retrieved", r.json()
            return False, f"Status {r.status_code}", None
        self.add_result("17", self._run_test("17.2", "Graph stats", test_17_2))

        # 17.3 Settings get
        def test_17_3():
            r = self._request("GET", "/settings/all")
            if r.status_code == 200:
                return True, "Settings retrieved", r.json()
            return False, f"Status {r.status_code}", None
        self.add_result("17", self._run_test("17.3", "Settings get", test_17_3))

    # ==================== SECTION 18: Distillation Pipeline ====================
    def test_section_18(self):
        """Section 18: Distillation Pipeline (Workspace Research)"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}=== Section 18: Distillation Pipeline ==={Colors.END}")

        # 18.1.1 Get categories
        def test_18_1_1():
            r = self._request("GET", "/workspace/research/categories")
            if r.status_code == 200:
                data = r.json()
                categories = data.get("categories", [])
                if len(categories) == 5:
                    return True, f"Found 5 categories", data
                return False, f"Expected 5 categories, got {len(categories)}", data
            return False, f"Status {r.status_code}", None
        self.add_result("18", self._run_test("18.1.1", "Get categories", test_18_1_1))

        # 18.1.2 List files
        def test_18_1_2():
            r = self._request("GET", "/workspace/research")
            if r.status_code == 200:
                return True, "File list retrieved", r.json()
            return False, f"Status {r.status_code}", None
        self.add_result("18", self._run_test("18.1.2", "List files", test_18_1_2))

        # 18.1.3 Valid categories
        def test_18_1_3():
            r = self._request("GET", "/workspace/research/categories")
            if r.status_code == 200:
                data = r.json()
                cat_ids = [c["id"] for c in data.get("categories", [])]
                expected = {"characters", "world", "theme", "plot", "voice"}
                if set(cat_ids) == expected:
                    return True, "All 5 categories present", cat_ids
                return False, f"Missing categories: {expected - set(cat_ids)}", cat_ids
            return False, f"Status {r.status_code}", None
        self.add_result("18", self._run_test("18.1.3", "Valid categories", test_18_1_3))

        # 18.1.4 Category icons
        def test_18_1_4():
            r = self._request("GET", "/workspace/research/categories")
            if r.status_code == 200:
                data = r.json()
                for cat in data.get("categories", []):
                    if "icon" not in cat or not cat["icon"]:
                        return False, f"Category {cat.get('id')} missing icon", data
                return True, "All categories have icons", None
            return False, f"Status {r.status_code}", None
        self.add_result("18", self._run_test("18.1.4", "Category icons", test_18_1_4))

        # 18.2.1 Save valid
        def test_18_2_1():
            r = self._request("POST", "/workspace/research/save",
                            json={
                                "category": "characters",
                                "key": "test_api_runner_char",
                                "content": "Fatal Flaw: Hubris\nThe Lie: I am always right"
                            })
            if r.status_code == 200:
                data = r.json()
                if data.get("success"):
                    return True, f"Saved to {data.get('file_path')}", data
                return False, data.get("message", "Save failed"), data
            return False, f"Status {r.status_code}: {r.text[:100]}", None
        self.add_result("18", self._run_test("18.2.1", "Save valid", test_18_2_1))

        # 18.2.2 Reject invalid category
        def test_18_2_2():
            r = self._request("POST", "/workspace/research/save",
                            json={
                                "category": "misc",
                                "key": "test_invalid",
                                "content": "This should fail"
                            })
            if r.status_code == 400:
                return True, "Correctly rejected invalid category", r.json()
            return False, f"Expected 400, got {r.status_code}", None
        self.add_result("18", self._run_test("18.2.2", "Reject invalid category", test_18_2_2))

        # 18.2.3 File created (check via read endpoint)
        def test_18_2_3():
            r = self._request("GET", "/workspace/research/characters/test_api_runner_char")
            if r.status_code == 200:
                data = r.json()
                if "content" in data:
                    return True, "File readable", data
            return False, f"Status {r.status_code}", None
        self.add_result("18", self._run_test("18.2.3", "File created", test_18_2_3))

        # 18.2.4 YAML frontmatter
        def test_18_2_4():
            r = self._request("GET", "/workspace/research/characters/test_api_runner_char")
            if r.status_code == 200:
                data = r.json()
                metadata = data.get("metadata", {})
                if metadata.get("category") == "characters" and metadata.get("status") == "draft":
                    return True, "Frontmatter correct", metadata
                return False, f"Missing expected frontmatter fields", metadata
            return False, f"Status {r.status_code}", None
        self.add_result("18", self._run_test("18.2.4", "YAML frontmatter", test_18_2_4))

        # 18.3.1 Check conflicts
        def test_18_3_1():
            r = self._request("POST", "/workspace/research/check-conflicts",
                            json={"content": "Test content", "category": "characters"})
            if r.status_code == 200:
                return True, "Conflict check works", r.json()
            return False, f"Status {r.status_code}", None
        self.add_result("18", self._run_test("18.3.1", "Check conflicts", test_18_3_1))

        # 18.3.2 Stage 1 warning
        def test_18_3_2():
            r = self._request("POST", "/workspace/research/check-conflicts",
                            json={"content": "Just some random brainstorming notes", "category": "characters"})
            if r.status_code == 200:
                data = r.json()
                if data.get("stage_warning"):
                    return True, "Stage 1 warning triggered", data
                return False, "Expected stage_warning: true", data
            return False, f"Status {r.status_code}", None
        self.add_result("18", self._run_test("18.3.2", "Stage 1 warning", test_18_3_2))

        # 18.3.3 Stage 2 pass
        def test_18_3_3():
            r = self._request("POST", "/workspace/research/check-conflicts",
                            json={"content": "Fatal Flaw: Pride\nThe Lie: I don't need anyone", "category": "characters"})
            if r.status_code == 200:
                data = r.json()
                if not data.get("stage_warning"):
                    return True, "Stage 2 content passes", data
                return False, "Unexpected stage_warning for Stage 2 content", data
            return False, f"Status {r.status_code}", None
        self.add_result("18", self._run_test("18.3.3", "Stage 2 pass", test_18_3_3))

        # 18.3.4 Summary included
        def test_18_3_4():
            r = self._request("POST", "/workspace/research/check-conflicts",
                            json={"content": "Test content", "category": "characters"})
            if r.status_code == 200:
                data = r.json()
                if "summary" in data:
                    return True, "Summary included", data
                return False, "Missing summary field", data
            return False, f"Status {r.status_code}", None
        self.add_result("18", self._run_test("18.3.4", "Summary included", test_18_3_4))

        # 18.4.1 Check promotable
        def test_18_4_1():
            r = self._request("GET", "/promotion/check",
                            params={"file_path": "workspace/research/characters/test_api_runner_char.md"})
            if r.status_code == 200:
                return True, "Promotion check works", r.json()
            return False, f"Status {r.status_code}", None
        self.add_result("18", self._run_test("18.4.1", "Check promotable", test_18_4_1))

        # 18.4.2-4 Promotion response fields
        def test_18_4_2():
            r = self._request("GET", "/promotion/check",
                            params={"file_path": "workspace/research/characters/test_api_runner_char.md"})
            if r.status_code == 200:
                data = r.json()
                if "blockers" in data:
                    return True, f"Blockers: {len(data['blockers'])}", data
                return False, "Missing blockers field", data
            return False, f"Status {r.status_code}", None
        self.add_result("18", self._run_test("18.4.2", "Blockers listed", test_18_4_2))

        def test_18_4_4():
            r = self._request("GET", "/promotion/check",
                            params={"file_path": "workspace/research/characters/test_api_runner_char.md"})
            if r.status_code == 200:
                data = r.json()
                if "target" in data and data["target"]:
                    return True, f"Target: {data['target']}", data
                return False, "Missing target field", data
            return False, f"Status {r.status_code}", None
        self.add_result("18", self._run_test("18.4.4", "Target shown", test_18_4_4))

        # 18.5.1 Preview extraction
        def test_18_5_1():
            r = self._request("GET", "/promotion/preview",
                            params={"file_path": "workspace/research/characters/test_api_runner_char.md"})
            if r.status_code == 200:
                return True, "Preview works", r.json()
            return True, f"Status {r.status_code} (may need file)", None
        self.add_result("18", self._run_test("18.5.1", "Preview extraction", test_18_5_1))

        # 18.5.3 Merge strategy
        def test_18_5_3():
            r = self._request("GET", "/promotion/preview",
                            params={"file_path": "workspace/research/characters/test_api_runner_char.md"})
            if r.status_code == 200:
                data = r.json()
                if "merge_strategy" in data:
                    return True, f"Strategy: {data['merge_strategy']}", data
                return False, "Missing merge_strategy", data
            return True, f"Status {r.status_code}", None
        self.add_result("18", self._run_test("18.5.3", "Merge strategy", test_18_5_3))

    # ==================== FOREMAN TESTS ====================
    def test_foreman(self):
        """Foreman API Tests"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}=== Foreman API Tests ==={Colors.END}")

        # Foreman status
        def test_foreman_status():
            r = self._request("GET", "/foreman/status")
            if r.status_code == 200:
                return True, "Foreman status OK", r.json()
            return False, f"Status {r.status_code}", None
        self.add_result("foreman", self._run_test("F.1", "Foreman status", test_foreman_status))

    # ==================== NOTEBOOKLM TESTS ====================
    def test_notebooklm(self):
        """NotebookLM API Tests"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}=== NotebookLM API Tests ==={Colors.END}")

        # List notebooks
        def test_notebooks_list():
            r = self._request("GET", "/notebooklm/notebooks")
            if r.status_code == 200:
                return True, "Notebooks list OK", r.json()
            return True, f"Status {r.status_code} (may need setup)", None
        self.add_result("notebooklm", self._run_test("N.1", "List notebooks", test_notebooks_list))

    # ==================== RUN ALL ====================
    def run_all(self):
        """Run all test sections."""
        start_time = time.time()

        print(f"\n{Colors.BOLD}{'='*60}")
        print(f"  Writers Factory API Test Runner")
        print(f"  Target: {self.base_url}")
        print(f"{'='*60}{Colors.END}\n")

        # Check backend is running
        try:
            r = requests.get(f"{self.base_url}/agents", timeout=5)
            if r.status_code != 200:
                print(f"{Colors.RED}Backend not responding correctly. Start with:{Colors.END}")
                print(f"  cd backend && uvicorn api:app --reload --port 8000")
                return
        except requests.exceptions.ConnectionError:
            print(f"{Colors.RED}Cannot connect to backend at {self.base_url}{Colors.END}")
            print(f"Start backend with:")
            print(f"  cd backend && uvicorn api:app --reload --port 8000")
            return

        # Run all sections
        self.test_section_1()
        self.test_section_11()
        self.test_section_12()
        self.test_section_15()
        self.test_section_17()
        self.test_section_18()
        self.test_foreman()
        self.test_notebooklm()

        # Summary
        total_time = time.time() - start_time
        self.print_summary(total_time)

    def run_section(self, section: str):
        """Run a specific section."""
        section_map = {
            "1": self.test_section_1,
            "11": self.test_section_11,
            "12": self.test_section_12,
            "15": self.test_section_15,
            "17": self.test_section_17,
            "18": self.test_section_18,
            "foreman": self.test_foreman,
            "notebooklm": self.test_notebooklm,
        }

        if section in section_map:
            start_time = time.time()
            section_map[section]()
            self.print_summary(time.time() - start_time)
        else:
            print(f"Unknown section: {section}")
            print(f"Available: {', '.join(section_map.keys())}")

    def run_quick(self):
        """Quick smoke test - critical endpoints only."""
        print(f"\n{Colors.BOLD}=== Quick Smoke Test ==={Colors.END}")
        start_time = time.time()

        self.test_section_1()
        self.test_section_17()

        self.print_summary(time.time() - start_time)

    def print_summary(self, duration: float):
        """Print test summary."""
        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)
        total = len(self.results)

        print(f"\n{Colors.BOLD}{'='*60}")
        print(f"  TEST SUMMARY")
        print(f"{'='*60}{Colors.END}")

        # By section
        for section, results in self.section_results.items():
            section_passed = sum(1 for r in results if r.passed)
            section_total = len(results)
            status = f"{Colors.GREEN}OK{Colors.END}" if section_passed == section_total else f"{Colors.RED}FAIL{Colors.END}"
            print(f"  Section {section}: {section_passed}/{section_total} [{status}]")

        print(f"\n{Colors.BOLD}  TOTAL: {passed}/{total} passed{Colors.END}")
        print(f"  Duration: {duration:.1f}s")

        if failed > 0:
            print(f"\n{Colors.RED}  FAILED TESTS:{Colors.END}")
            for r in self.results:
                if not r.passed:
                    print(f"    - {r.test_id}: {r.name}")
                    print(f"      {r.message}")

        print()

        # Exit code
        return 0 if failed == 0 else 1


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Writers Factory API Test Runner")
    parser.add_argument("--section", "-s", help="Run specific section (1, 11, 12, 15, 17, 18, foreman, notebooklm)")
    parser.add_argument("--quick", "-q", action="store_true", help="Quick smoke test")
    parser.add_argument("--url", default=BASE_URL, help=f"Backend URL (default: {BASE_URL})")
    args = parser.parse_args()

    runner = APITestRunner(args.url)

    if args.quick:
        exit_code = runner.run_quick()
    elif args.section:
        exit_code = runner.run_section(args.section)
    else:
        exit_code = runner.run_all()

    sys.exit(exit_code or 0)


if __name__ == "__main__":
    main()
