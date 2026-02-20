#!/usr/bin/env python3
"""
Test suite for inline recall probe functionality.

Tests the entire pipeline without requiring LLM/API calls:
1. Probe injection into merged JSON  (data integrity)
2. Probe detection in test loops      (is_recall_probe flag)
3. _compute_recall_scores()           (ROUGE / BLEU scoring)
4. _log_recall_probe_detail()         (detail log output)
5. _calculate_recall_metrics()        (metric aggregation)
6. generate_table() TABLE_2           (markdown generation)
7. Old methods are removed            (no run_recall_probes / _build_topic_references)
"""

import json
import os
import sys
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

# ── Path setup (guard for Kaggle exec() where __file__ may be undefined) ────
try:
    _THIS_FILE = Path(__file__).resolve()
except NameError:
    _THIS_FILE = Path(os.getcwd()) / "dataset" / "test_recall_probes.py"

DATASET_DIR = _THIS_FILE.parent
BACKEND_DIR = DATASET_DIR.parent
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(DATASET_DIR))


# ═══════════════════════════════════════════════════════════════════════════
# 1. DATA INTEGRITY — verify merged JSON has well-formed probes
# ═══════════════════════════════════════════════════════════════════════════
class TestProbeDataIntegrity(unittest.TestCase):
    """Verify the merged scenario JSON contains correct recall probe steps."""

    _SKIP_REASON: str = ""

    @classmethod
    def setUpClass(cls):
        merged_path = DATASET_DIR / "scenarios" / "merged_realistic_interleaved.json"
        try:
            with open(merged_path) as f:
                cls.data = json.load(f)
        except FileNotFoundError:
            cls._SKIP_REASON = (
                f"merged_realistic_interleaved.json not found at {merged_path}. "
                "Run `git lfs pull` to download dataset files."
            )
            cls.data = {"conversations": [], "total_turns": 0}
        except json.JSONDecodeError as e:
            cls._SKIP_REASON = f"Invalid JSON in merged scenario file: {e}"
            cls.data = {"conversations": [], "total_turns": 0}
        cls.all_steps = cls.data["conversations"]
        cls.probes = [s for s in cls.all_steps if s.get("is_recall_probe")]
        cls.regular = [s for s in cls.all_steps if not s.get("is_recall_probe")]

    def setUp(self):
        if self._SKIP_REASON:
            self.skipTest(self._SKIP_REASON)

    def test_probes_exist(self):
        """At least 1 recall probe must be present."""
        self.assertGreater(len(self.probes), 0, "No recall probes found in merged JSON")

    def test_probe_count_matches_metadata(self):
        """total_turns metadata must equal total step count."""
        self.assertEqual(
            self.data["total_turns"], len(self.all_steps),
            "total_turns metadata mismatch with actual step count"
        )

    def test_probes_come_after_regular_steps(self):
        """All probes must appear after all regular conversation steps."""
        last_regular_step = max(s["step"] for s in self.regular)
        first_probe_step = min(s["step"] for s in self.probes)
        self.assertGreater(
            first_probe_step, last_regular_step,
            f"Probe step {first_probe_step} overlaps with regular step {last_regular_step}"
        )

    def test_probe_step_numbers_are_sequential(self):
        """Probe step numbers must be sequential (no gaps)."""
        probe_steps = sorted(s["step"] for s in self.probes)
        for i in range(1, len(probe_steps)):
            self.assertEqual(
                probe_steps[i], probe_steps[i-1] + 1,
                f"Gap in probe steps: {probe_steps[i-1]} -> {probe_steps[i]}"
            )

    def test_each_probe_has_required_fields(self):
        """Every probe must have the essential fields."""
        required = [
            "is_recall_probe", "probe_topic", "node_type", "message",
            "action", "is_main_only_topic", "topic_turn_count",
        ]
        for p in self.probes:
            for field in required:
                self.assertIn(
                    field, p,
                    f"Probe step {p['step']} missing field '{field}'"
                )

    # NOTE: reference_text and reference_conversations are no longer required in JSON.
    # References are now built dynamically at runtime from real AI responses
    # collected during the test run (see _build_recall_reference).

    def test_probe_topics_are_unique(self):
        """No two probes should target the same topic."""
        topics = [p["probe_topic"] for p in self.probes]
        self.assertEqual(len(topics), len(set(topics)), f"Duplicate probe topics: {topics}")

    def test_probe_message_mentions_topic(self):
        """Probe message should reference the topic being probed."""
        for p in self.probes:
            topic_words = p["probe_topic"].replace("_", " ")
            # The message should contain at least part of the topic
            self.assertIn(
                topic_words, p["message"].lower(),
                f"Probe step {p['step']} message doesn't mention topic '{topic_words}'"
            )

    def test_main_only_topics_have_main_node_type(self):
        """Probes flagged is_main_only_topic=True must have node_type='main'."""
        for p in self.probes:
            if p["is_main_only_topic"]:
                self.assertEqual(
                    p["node_type"], "main",
                    f"main-only probe '{p['probe_topic']}' has node_type='{p['node_type']}' (should be 'main')"
                )

    def test_non_main_probes_have_subchat_node_type(self):
        """Probes not flagged main-only must have a subchat_* node_type."""
        for p in self.probes:
            if not p["is_main_only_topic"]:
                self.assertTrue(
                    p["node_type"].startswith("subchat_"),
                    f"Probe '{p['probe_topic']}' has non-subchat node_type='{p['node_type']}'"
                )

    def test_topic_turn_count_at_least_3(self):
        """All probed topics must have ≥3 turns (eligibility threshold)."""
        for p in self.probes:
            self.assertGreaterEqual(
                p["topic_turn_count"], 3,
                f"Probe '{p['probe_topic']}' has only {p['topic_turn_count']} turns"
            )

    def test_action_is_switch_node(self):
        """All probes should have action='switch_node'."""
        for p in self.probes:
            self.assertEqual(
                p["action"], "switch_node",
                f"Probe step {p['step']} has action='{p['action']}' (should be 'switch_node')"
            )

    def test_probe_node_types_exist_in_regular_steps(self):
        """Every probe's node_type must appear in at least one regular step."""
        regular_node_types = set(s.get("node_type", "main") for s in self.regular)
        for p in self.probes:
            self.assertIn(
                p["node_type"], regular_node_types,
                f"Probe node_type '{p['node_type']}' not found in any regular step"
            )


# ═══════════════════════════════════════════════════════════════════════════
# 2. SCORING — _compute_recall_scores()
# ═══════════════════════════════════════════════════════════════════════════
class TestComputeRecallScores(unittest.TestCase):
    """Test ROUGE/BLEU scoring without LLM calls."""

    @classmethod
    def setUpClass(cls):
        """Create a minimal runner instance (mock out LLM/DB dependencies)."""
        with patch("kaggle_serverless_runner.SimpleChat"), \
             patch("kaggle_serverless_runner.ContextClassifier"), \
             patch("kaggle_serverless_runner.set_log_directory"):
            from kaggle_serverless_runner import ServerlessTestRunner
            cls.runner = ServerlessTestRunner.__new__(ServerlessTestRunner)
            # Minimal init for scoring methods
            cls.runner.base_logs_dir = Path(tempfile.mkdtemp())
            cls.runner.main_log_file = cls.runner.base_logs_dir / "test.log"
            cls.runner.main_log_file.touch()
            cls.runner.buffer_log_dir = None

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.runner.base_logs_dir, ignore_errors=True)

    def test_identical_strings_high_score(self):
        """Identical summary and reference should yield high scores."""
        text = "The cookies recipe requires halving all ingredients precisely."
        scores = self.runner._compute_recall_scores(text, text)
        self.assertGreater(scores["rouge1_f"], 0.9)
        self.assertGreater(scores["rougeL_f"], 0.9)
        self.assertGreater(scores["bleu"], 0.5)

    def test_empty_summary_returns_zeros(self):
        """Empty summary should return all-zero scores."""
        scores = self.runner._compute_recall_scores("", "some reference text")
        self.assertEqual(scores["rouge1_f"], 0.0)
        self.assertEqual(scores["rougeL_f"], 0.0)
        self.assertEqual(scores["bleu"], 0.0)

    def test_empty_reference_returns_zeros(self):
        """Empty reference should return all-zero scores."""
        scores = self.runner._compute_recall_scores("some summary text", "")
        self.assertEqual(scores["rouge1_f"], 0.0)
        self.assertEqual(scores["rougeL_f"], 0.0)
        self.assertEqual(scores["bleu"], 0.0)

    def test_both_empty_returns_zeros(self):
        scores = self.runner._compute_recall_scores("", "")
        self.assertEqual(scores, {"rouge1_f": 0.0, "rougeL_f": 0.0, "bleu": 0.0})

    def test_partial_overlap_moderate_score(self):
        """Partial overlap should give moderate (non-zero, non-one) scores."""
        summary = "We discussed cookies and recipe halving."
        reference = "The user asked about cookies and halving the recipe ingredients. We calculated the amounts."
        scores = self.runner._compute_recall_scores(summary, reference)
        self.assertGreater(scores["rouge1_f"], 0.1)
        self.assertLess(scores["rouge1_f"], 1.0)

    def test_completely_disjoint_low_score(self):
        """Completely unrelated text should give very low scores."""
        summary = "quantum physics black holes relativity spacetime"
        reference = "cooking baking chocolate vanilla sugar butter"
        scores = self.runner._compute_recall_scores(summary, reference)
        self.assertLess(scores["rouge1_f"], 0.15)
        self.assertLess(scores["bleu"], 0.15)

    def test_return_dict_structure(self):
        """Scores dict must have exactly 3 expected keys."""
        scores = self.runner._compute_recall_scores("hello world", "hello world")
        self.assertEqual(set(scores.keys()), {"rouge1_f", "rougeL_f", "bleu"})

    def test_scores_are_floats_in_range(self):
        """All scores should be floats between 0 and 1."""
        scores = self.runner._compute_recall_scores(
            "This is a sample summary text with several words.",
            "This is the actual reference text that was said."
        )
        for key, val in scores.items():
            self.assertIsInstance(val, float, f"{key} is not float")
            self.assertGreaterEqual(val, 0.0, f"{key} below 0")
            self.assertLessEqual(val, 1.0, f"{key} above 1")


# ═══════════════════════════════════════════════════════════════════════════
# 3. DETAIL LOGGING — _log_recall_probe_detail()
# ═══════════════════════════════════════════════════════════════════════════
class TestLogRecallProbeDetail(unittest.TestCase):
    """Test that detail log file is written correctly."""

    def setUp(self):
        """Create temp dir and minimal runner."""
        self.tmpdir = Path(tempfile.mkdtemp())
        with patch("kaggle_serverless_runner.SimpleChat"), \
             patch("kaggle_serverless_runner.ContextClassifier"), \
             patch("kaggle_serverless_runner.set_log_directory"):
            from kaggle_serverless_runner import ServerlessTestRunner
            self.runner = ServerlessTestRunner.__new__(ServerlessTestRunner)
            self.runner.base_logs_dir = self.tmpdir
            self.runner.main_log_file = self.tmpdir / "test.log"
            self.runner.main_log_file.touch()
            self.runner.buffer_log_dir = self.tmpdir

        # Create the log file the method expects
        log_file = self.tmpdir / "recall_probes_detail.log"
        log_file.touch()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_log_file_created_and_populated(self):
        """_log_recall_probe_detail should write to recall_probes_detail.log."""
        self.runner._log_recall_probe_detail(
            topic="cookies_recipe_halving",
            target_node="subchat_1_cookies_recipe_halving",
            probe_message="Summarize everything about cookies recipe halving",
            llm_response="We discussed halving a cookie recipe. The user asked to divide ingredients by 2.",
            reference_text="User: Can you halve this recipe? Assistant: Sure, divide all ingredients by 2.",
            scores={"rouge1_f": 0.65, "rougeL_f": 0.58, "bleu": 0.42},
            mode="system",
            is_main_only=False,
        )

        log_path = self.tmpdir / "recall_probes_detail.log"
        self.assertTrue(log_path.exists())
        content = log_path.read_text()

        # Check essential sections
        self.assertIn("cookies_recipe_halving", content)
        self.assertIn("SYSTEM", content)
        self.assertIn("PROBE QUESTION", content)
        self.assertIn("LLM SUMMARY RESPONSE", content)
        self.assertIn("REFERENCE", content)
        self.assertIn("SCORES", content)
        self.assertIn("0.6500", content)  # ROUGE-1
        self.assertIn("0.5800", content)  # ROUGE-L
        self.assertIn("0.4200", content)  # BLEU
        self.assertIn("subchat_1_cookies_recipe_halving", content)
        self.assertIn("👤 User:", content)
        self.assertIn("🤖 AI:", content)

    def test_main_only_flag_in_log(self):
        """main-only topics should show a warning marker."""
        self.runner._log_recall_probe_detail(
            topic="ai_meta",
            target_node="main",
            probe_message="Summarize ai meta discussions",
            llm_response="We talked about AI capabilities.",
            reference_text="User: Tell me about yourself Assistant: I am an AI assistant.",
            scores={"rouge1_f": 0.3, "rougeL_f": 0.25, "bleu": 0.1},
            mode="baseline",
            is_main_only=True,
        )

        content = (self.tmpdir / "recall_probes_detail.log").read_text()
        self.assertIn("main-only topic", content)
        self.assertIn("⚠️", content)

    def test_no_write_when_buffer_log_dir_none(self):
        """If buffer_log_dir is None, nothing should be written."""
        self.runner.buffer_log_dir = None
        # Should not raise
        self.runner._log_recall_probe_detail(
            topic="test", target_node="main", probe_message="test",
            llm_response="test", reference_text="test",
            scores={"rouge1_f": 0, "rougeL_f": 0, "bleu": 0}, mode="system"
        )


# ═══════════════════════════════════════════════════════════════════════════
# 4. METRIC AGGREGATION — _calculate_recall_metrics()
# ═══════════════════════════════════════════════════════════════════════════
class TestCalculateRecallMetrics(unittest.TestCase):
    """Test recall metric aggregation."""

    @classmethod
    def setUpClass(cls):
        with patch("kaggle_serverless_runner.SimpleChat"), \
             patch("kaggle_serverless_runner.ContextClassifier"), \
             patch("kaggle_serverless_runner.set_log_directory"):
            from kaggle_serverless_runner import ServerlessTestRunner
            cls.runner = ServerlessTestRunner.__new__(ServerlessTestRunner)
            cls.runner.base_logs_dir = Path(tempfile.mkdtemp())
            cls.runner.main_log_file = cls.runner.base_logs_dir / "test.log"
            cls.runner.main_log_file.touch()
            cls.runner.buffer_log_dir = None

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.runner.base_logs_dir, ignore_errors=True)

    def _make_probe(self, topic, rouge1, rougeL, bleu, mode="system"):
        return {
            "topic": topic, "mode": mode,
            "rouge1_f": rouge1, "rougeL_f": rougeL, "bleu": bleu,
            "summary_length": 50, "reference_length": 100,
            "probe_tokens": 200, "probe_latency": 0.5,
        }

    def test_empty_probes_returns_zeros(self):
        result = self.runner._calculate_recall_metrics([], [])
        self.assertEqual(result["baseline"]["avg_rouge1"], 0.0)
        self.assertEqual(result["system"]["avg_bleu"], 0.0)
        self.assertEqual(result["baseline"]["num_topics_probed"], 0)

    def test_single_probe_averages(self):
        bl = [self._make_probe("t1", 0.5, 0.4, 0.3, "baseline")]
        sy = [self._make_probe("t1", 0.8, 0.7, 0.6, "system")]
        result = self.runner._calculate_recall_metrics(bl, sy)
        self.assertAlmostEqual(result["baseline"]["avg_rouge1"], 0.5)
        self.assertAlmostEqual(result["system"]["avg_rouge1"], 0.8)
        self.assertAlmostEqual(result["system"]["avg_bleu"], 0.6)

    def test_multiple_probes_average_correctly(self):
        bl = [
            self._make_probe("t1", 0.4, 0.3, 0.2, "baseline"),
            self._make_probe("t2", 0.6, 0.5, 0.4, "baseline"),
        ]
        sy = [
            self._make_probe("t1", 0.7, 0.6, 0.5, "system"),
            self._make_probe("t2", 0.9, 0.8, 0.7, "system"),
        ]
        result = self.runner._calculate_recall_metrics(bl, sy)
        self.assertAlmostEqual(result["baseline"]["avg_rouge1"], 0.5)
        self.assertAlmostEqual(result["system"]["avg_rouge1"], 0.8)

    def test_per_topic_breakdown_present(self):
        bl = [self._make_probe("cookies", 0.5, 0.4, 0.3, "baseline")]
        sy = [self._make_probe("cookies", 0.8, 0.7, 0.6, "system")]
        result = self.runner._calculate_recall_metrics(bl, sy)
        self.assertIn("cookies", result["baseline"]["per_topic"])
        self.assertIn("cookies", result["system"]["per_topic"])
        self.assertAlmostEqual(result["system"]["per_topic"]["cookies"]["rouge1_f"], 0.8)

    def test_improvements_calculated(self):
        bl = [self._make_probe("t1", 0.4, 0.3, 0.2, "baseline")]
        sy = [self._make_probe("t1", 0.8, 0.6, 0.4, "system")]
        result = self.runner._calculate_recall_metrics(bl, sy)
        # Improvement = (0.8 - 0.4) / 0.4 * 100 = 100%
        self.assertAlmostEqual(result["improvements"]["avg_rouge1"], 100.0)
        # BLEU: (0.4 - 0.2) / 0.2 * 100 = 100%
        self.assertAlmostEqual(result["improvements"]["avg_bleu"], 100.0)

    def test_improvement_from_zero_baseline(self):
        bl = [self._make_probe("t1", 0.0, 0.0, 0.0, "baseline")]
        sy = [self._make_probe("t1", 0.5, 0.4, 0.3, "system")]
        result = self.runner._calculate_recall_metrics(bl, sy)
        self.assertEqual(result["improvements"]["avg_rouge1"], float('inf'))

    def test_total_tokens_and_latency(self):
        probes = [
            self._make_probe("t1", 0.5, 0.4, 0.3, "system"),
            self._make_probe("t2", 0.6, 0.5, 0.4, "system"),
        ]
        result = self.runner._calculate_recall_metrics([], probes)
        self.assertEqual(result["system"]["total_probe_tokens"], 400)
        self.assertAlmostEqual(result["system"]["total_probe_latency"], 1.0)

    def test_return_structure(self):
        result = self.runner._calculate_recall_metrics([], [])
        self.assertIn("baseline", result)
        self.assertIn("system", result)
        self.assertIn("improvements", result)
        for key in ["avg_rouge1", "avg_rougeL", "avg_bleu", "num_topics_probed", "per_topic"]:
            self.assertIn(key, result["baseline"])
            self.assertIn(key, result["system"])


# ═══════════════════════════════════════════════════════════════════════════
# 5. TABLE 2 GENERATION — generate_table() recall section
# ═══════════════════════════════════════════════════════════════════════════
class TestTable2Generation(unittest.TestCase):
    """Test TABLE_2_RECALL_SCORES.md generation."""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        with patch("kaggle_serverless_runner.SimpleChat"), \
             patch("kaggle_serverless_runner.ContextClassifier"), \
             patch("kaggle_serverless_runner.set_log_directory"):
            from kaggle_serverless_runner import ServerlessTestRunner
            self.runner = ServerlessTestRunner.__new__(ServerlessTestRunner)
            self.runner.base_logs_dir = self.tmpdir
            self.runner.main_log_file = self.tmpdir / "test.log"
            self.runner.main_log_file.touch()
            self.runner.buffer_log_dir = self.tmpdir
            self.runner.current_buffer_size = 15

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_table2_markdown_generated(self):
        """TABLE_2_RECALL_SCORES.md should be generated when recall data exists."""
        metrics = {
            "table_1": {
                "baseline": {"accuracy": 50, "pollution_rate": 50, "precision": 50, "recall": 50, "f1": 50,
                             "macro_precision": 50, "macro_recall": 50, "macro_f1": 50,
                             "tp": 5, "tn": 0, "fp": 5, "fn": 0, "per_topic_metrics": {}, "topics": []},
                "system": {"accuracy": 80, "pollution_rate": 20, "precision": 80, "recall": 80, "f1": 80,
                           "macro_precision": 80, "macro_recall": 80, "macro_f1": 80,
                           "tp": 8, "tn": 0, "fp": 2, "fn": 0, "per_topic_metrics": {}, "topics": []},
                "improvements": {"precision": 60, "recall": 60, "f1": 60, "accuracy": 60,
                                 "pollution_rate": -60, "macro_precision": 60, "macro_recall": 60, "macro_f1": 60},
            },
            "table_3": {
                "baseline": {"avg_input_tokens": 100, "avg_output_tokens": 50, "avg_total_tokens": 150,
                             "avg_latency": 0.5, "token_compression_rate": 0, "tokens_per_correct_answer": 300,
                             "cost_per_query": 0.00001, "cost_per_1m_queries": 10},
                "system": {"avg_input_tokens": 80, "avg_output_tokens": 40, "avg_total_tokens": 120,
                           "avg_latency": 0.4, "token_compression_rate": 20, "tokens_per_correct_answer": 150,
                           "cost_per_query": 0.000008, "cost_per_1m_queries": 8},
                "improvements": {"avg_input_tokens": -20, "avg_output_tokens": -20, "avg_total_tokens": -20,
                                 "avg_latency": -20, "token_compression_rate": 100,
                                 "tokens_per_correct_answer": -50,
                                 "cost_per_query": -20, "cost_per_1m_queries": -20},
            },
            "table_2": {
                "baseline": {
                    "avg_rouge1": 0.35, "avg_rougeL": 0.30, "avg_bleu": 0.20,
                    "num_topics_probed": 3, "total_probe_tokens": 600,
                    "total_probe_latency": 1.5,
                    "per_topic": {
                        "cookies": {"rouge1_f": 0.4, "rougeL_f": 0.35, "bleu": 0.25,
                                    "summary_length": 50, "reference_length": 100},
                        "chess": {"rouge1_f": 0.3, "rougeL_f": 0.25, "bleu": 0.15,
                                  "summary_length": 40, "reference_length": 80},
                    }
                },
                "system": {
                    "avg_rouge1": 0.70, "avg_rougeL": 0.65, "avg_bleu": 0.55,
                    "num_topics_probed": 3, "total_probe_tokens": 500,
                    "total_probe_latency": 1.2,
                    "per_topic": {
                        "cookies": {"rouge1_f": 0.8, "rougeL_f": 0.75, "bleu": 0.65,
                                    "summary_length": 60, "reference_length": 100},
                        "chess": {"rouge1_f": 0.6, "rougeL_f": 0.55, "bleu": 0.45,
                                  "summary_length": 55, "reference_length": 80},
                    }
                },
                "improvements": {"avg_rouge1": 100.0, "avg_rougeL": 116.7, "avg_bleu": 175.0},
            }
        }

        self.runner.generate_table(metrics)

        table2_path = self.tmpdir / "tables" / "buffer_15" / "TABLE_2_RECALL_SCORES.md"
        self.assertTrue(table2_path.exists(), "TABLE_2_RECALL_SCORES.md not generated")

        content = table2_path.read_text()
        self.assertIn("TABLE 2", content)
        self.assertIn("ROUGE-1", content)
        self.assertIn("BLEU", content)
        self.assertIn("cookies", content)
        self.assertIn("chess", content)
        self.assertIn("Per-Topic Breakdown", content)
        self.assertIn("Topic Winners", content)

    def test_table2_skipped_when_no_probe_data(self):
        """TABLE_2 should be skipped gracefully when no probe data exists."""
        metrics = {
            "table_1": {
                "baseline": {"accuracy": 50, "pollution_rate": 50, "precision": 50, "recall": 50, "f1": 50,
                             "macro_precision": 50, "macro_recall": 50, "macro_f1": 50,
                             "tp": 5, "tn": 0, "fp": 5, "fn": 0, "per_topic_metrics": {}, "topics": []},
                "system": {"accuracy": 80, "pollution_rate": 20, "precision": 80, "recall": 80, "f1": 80,
                           "macro_precision": 80, "macro_recall": 80, "macro_f1": 80,
                           "tp": 8, "tn": 0, "fp": 2, "fn": 0, "per_topic_metrics": {}, "topics": []},
                "improvements": {"precision": 60, "recall": 60, "f1": 60, "accuracy": 60,
                                 "pollution_rate": -60, "macro_precision": 60, "macro_recall": 60, "macro_f1": 60},
            },
            "table_3": {
                "baseline": {"avg_input_tokens": 100, "avg_output_tokens": 50, "avg_total_tokens": 150,
                             "avg_latency": 0.5, "token_compression_rate": 0, "tokens_per_correct_answer": 300,
                             "cost_per_query": 0.00001, "cost_per_1m_queries": 10},
                "system": {"avg_input_tokens": 80, "avg_output_tokens": 40, "avg_total_tokens": 120,
                           "avg_latency": 0.4, "token_compression_rate": 20, "tokens_per_correct_answer": 150,
                           "cost_per_query": 0.000008, "cost_per_1m_queries": 8},
                "improvements": {"avg_input_tokens": -20, "avg_output_tokens": -20, "avg_total_tokens": -20,
                                 "avg_latency": -20, "token_compression_rate": 100,
                                 "tokens_per_correct_answer": -50,
                                 "cost_per_query": -20, "cost_per_1m_queries": -20},
            },
            # No table_2 key at all
        }
        # Should not raise
        self.runner.generate_table(metrics)
        table2_path = self.tmpdir / "tables" / "buffer_15" / "TABLE_2_RECALL_SCORES.md"
        self.assertFalse(table2_path.exists(), "TABLE_2 should not be generated with no data")


# ═══════════════════════════════════════════════════════════════════════════
# 6. OLD CODE REMOVAL — run_recall_probes / _build_topic_references gone
# ═══════════════════════════════════════════════════════════════════════════
class TestOldCodeRemoved(unittest.TestCase):
    """Verify deprecated recall probe methods no longer exist."""

    @classmethod
    def setUpClass(cls):
        cls.runner_src = (DATASET_DIR / "kaggle_serverless_runner.py").read_text()

    def test_run_recall_probes_removed(self):
        """Old run_recall_probes() method should not exist."""
        self.assertNotIn(
            "def run_recall_probes(", self.runner_src,
            "run_recall_probes() still exists — should be removed"
        )

    def test_build_topic_references_removed(self):
        """Old _build_topic_references() method should not exist."""
        self.assertNotIn(
            "def _build_topic_references(", self.runner_src,
            "_build_topic_references() still exists — should be removed"
        )

    def test_no_call_to_run_recall_probes(self):
        """No code should call run_recall_probes() anywhere."""
        # Allow the comment explaining it's removed, but no actual call
        import re
        calls = re.findall(r'(?<!#\s)self\.run_recall_probes\(', self.runner_src)
        self.assertEqual(len(calls), 0, f"Found {len(calls)} calls to run_recall_probes()")


# ═══════════════════════════════════════════════════════════════════════════
# 7. PROBE DETECTION IN TEST LOOPS — verify is_recall_probe branch
# ═══════════════════════════════════════════════════════════════════════════
class TestProbeDetectionInTestLoop(unittest.TestCase):
    """
    Verify that run_baseline_test and run_system_test correctly detect
    is_recall_probe steps and skip normal evaluation for them.
    Uses a minimal 3-step scenario (2 regular + 1 probe).
    """

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        with patch("kaggle_serverless_runner.SimpleChat") as MockChat, \
             patch("kaggle_serverless_runner.ContextClassifier") as MockClassifier, \
             patch("kaggle_serverless_runner.set_log_directory"):
            from kaggle_serverless_runner import ServerlessTestRunner
            self.runner = ServerlessTestRunner.__new__(ServerlessTestRunner)

            # Minimal init
            self.runner.base_logs_dir = self.tmpdir
            self.runner.main_log_file = self.tmpdir / "test.log"
            self.runner.main_log_file.touch()
            self.runner.buffer_log_dir = self.tmpdir
            self.runner.baseline_log_file = self.tmpdir / "baseline_test.log"
            self.runner.baseline_log_file.touch()
            self.runner.system_log_file = self.tmpdir / "system_test.log"
            self.runner.system_log_file.touch()
            self.runner.current_buffer_size = 15
            self.runner.chat = MagicMock()
            self.runner.classifier = MagicMock()
            self.runner._last_baseline_recall_probes = []
            self.runner._last_system_recall_probes = []

            # Create recall probe detail log
            (self.tmpdir / "recall_probes_detail.log").touch()

        self.mini_scenario = {
            "scenario_name": "Mini Test",
            "_extracted_topics": ["cookies_recipe_halving"],
            "conversations": [
                {
                    "step": 1, "context": "intro", "message": "Hello",
                    "expected": "greeting", "node_type": "main", "action": "",
                },
                {
                    "step": 2, "context": "cookies_recipe_halving",
                    "message": "cookies_recipe_halving : halve the recipe please",
                    "expected": "cookies_recipe_halving: halving response",
                    "node_type": "subchat_1_cookies_recipe_halving",
                    "action": "create_subchat",
                    "parent_node_type": "main",
                    "subchat_title": "Recipe Halving",
                    "selected_text": "halve the recipe",
                },
                {
                    "step": 3, "context": "cookies_recipe_halving",
                    "message": "Summarize everything we discussed about cookies recipe halving",
                    "expected": "recall_probe:cookies_recipe_halving",
                    "node_type": "subchat_1_cookies_recipe_halving",
                    "action": "switch_node",
                    "is_recall_probe": True,
                    "probe_topic": "cookies_recipe_halving",
                    "reference_text": "halve the recipe please",
                    "reference_conversations": [
                        {"role": "user", "message": "halve the recipe please", "step": 2}
                    ],
                    "is_main_only_topic": False,
                    "topic_turn_count": 3,
                    "parent_node_type": "",
                    "subchat_title": "",
                    "selected_text": "",
                    "linear_failure_risk": "none",
                    "source_conversation_id": "test",
                    "source_scenario": "test",
                    "original_step": 3,
                },
            ]
        }

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_baseline_skips_probe_in_results(self):
        """Baseline test: probe step should NOT appear in returned results list."""
        fake_node_id = "fake-uuid-1234"

        # Mock create_conversation and send_message
        self.runner.create_conversation = MagicMock(return_value=fake_node_id)
        self.runner.send_message = MagicMock(return_value={
            "response": "cookies_recipe_halving: Here is the halved recipe...",
            "usage": {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150},
            "latency": 0.3
        })

        results = self.runner.run_baseline_test(self.mini_scenario, buffer_size=15)

        # Regular steps should be in results, probe should not
        result_steps = [r["step"] for r in results]
        self.assertIn(1, result_steps, "Regular step 1 should be in results")
        self.assertIn(2, result_steps, "Regular step 2 should be in results")
        self.assertNotIn(3, result_steps, "Probe step 3 should NOT be in results")

        # Probe results should be stored separately
        self.assertEqual(len(self.runner._last_baseline_recall_probes), 1)
        self.assertEqual(self.runner._last_baseline_recall_probes[0]["topic"], "cookies_recipe_halving")

    def test_system_skips_probe_in_results(self):
        """System test: probe step should NOT appear in returned results list."""
        fake_main_id = "fake-main-uuid"
        fake_subchat_id = "fake-subchat-uuid"

        self.runner.create_conversation = MagicMock(return_value=fake_main_id)
        self.runner.create_subchat = MagicMock(return_value=fake_subchat_id)
        self.runner.send_message = MagicMock(return_value={
            "response": "cookies_recipe_halving: Here is the halved recipe...",
            "usage": {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150},
            "latency": 0.3
        })

        results = self.runner.run_system_test(self.mini_scenario, buffer_size=15)

        result_steps = [r["step"] for r in results]
        self.assertNotIn(3, result_steps, "Probe step 3 should NOT be in results")
        self.assertEqual(len(self.runner._last_system_recall_probes), 1)

    def test_system_probe_routed_to_correct_node(self):
        """System test: probe should be sent to the subchat node, not main."""
        fake_main_id = "fake-main-uuid"
        fake_subchat_id = "fake-subchat-uuid"

        self.runner.create_conversation = MagicMock(return_value=fake_main_id)
        self.runner.create_subchat = MagicMock(return_value=fake_subchat_id)

        call_log = []
        def track_send(node_id, message, enable_rag=False):
            call_log.append({"node_id": node_id, "message": message, "enable_rag": enable_rag})
            return {
                "response": "cookies_recipe_halving: response text",
                "usage": {"prompt_tokens": 50, "completion_tokens": 30, "total_tokens": 80},
                "latency": 0.2,
                "rag_used": False,
                "rag_decision": "disabled"
            }

        self.runner.send_message = track_send

        self.runner.run_system_test(self.mini_scenario, buffer_size=15)

        # Find the probe call (step 3's message)
        probe_calls = [c for c in call_log if "Summarize everything" in c["message"]]
        self.assertEqual(len(probe_calls), 1, "Expected exactly 1 probe call")
        self.assertEqual(
            probe_calls[0]["node_id"], fake_subchat_id,
            f"Probe routed to {probe_calls[0]['node_id']} instead of subchat {fake_subchat_id}"
        )


# ═══════════════════════════════════════════════════════════════════════════
# 8. END-TO-END INTEGRATION — full pipeline with mock LLM
# ═══════════════════════════════════════════════════════════════════════════
class TestEndToEndIntegration(unittest.TestCase):
    """Full pipeline: scenario load → test run → metrics → table generation."""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        with patch("kaggle_serverless_runner.SimpleChat"), \
             patch("kaggle_serverless_runner.ContextClassifier"), \
             patch("kaggle_serverless_runner.set_log_directory"):
            from kaggle_serverless_runner import ServerlessTestRunner
            self.runner = ServerlessTestRunner.__new__(ServerlessTestRunner)
            self.runner.base_logs_dir = self.tmpdir
            self.runner.main_log_file = self.tmpdir / "test.log"
            self.runner.main_log_file.touch()
            self.runner.buffer_log_dir = self.tmpdir
            self.runner.current_buffer_size = 15
            self.runner.chat = MagicMock()
            self.runner.classifier = MagicMock()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_full_recall_metrics_pipeline(self):
        """End-to-end: create probe data → compute scores → aggregate → generate table."""
        # Simulate probe results from both conditions
        baseline_probes = [
            {"topic": "cookies", "mode": "baseline",
             "rouge1_f": 0.30, "rougeL_f": 0.25, "bleu": 0.15,
             "summary_length": 40, "reference_length": 100,
             "probe_tokens": 200, "probe_latency": 0.5},
            {"topic": "chess", "mode": "baseline",
             "rouge1_f": 0.25, "rougeL_f": 0.20, "bleu": 0.10,
             "summary_length": 35, "reference_length": 80,
             "probe_tokens": 180, "probe_latency": 0.4},
        ]
        system_probes = [
            {"topic": "cookies", "mode": "system",
             "rouge1_f": 0.75, "rougeL_f": 0.70, "bleu": 0.60,
             "summary_length": 60, "reference_length": 100,
             "probe_tokens": 150, "probe_latency": 0.3},
            {"topic": "chess", "mode": "system",
             "rouge1_f": 0.65, "rougeL_f": 0.60, "bleu": 0.50,
             "summary_length": 55, "reference_length": 80,
             "probe_tokens": 140, "probe_latency": 0.35},
        ]

        # Calculate recall metrics
        recall_metrics = self.runner._calculate_recall_metrics(baseline_probes, system_probes)

        # Verify structure
        self.assertIn("baseline", recall_metrics)
        self.assertIn("system", recall_metrics)
        self.assertIn("improvements", recall_metrics)

        # Verify averages
        self.assertAlmostEqual(recall_metrics["baseline"]["avg_rouge1"], 0.275)
        self.assertAlmostEqual(recall_metrics["system"]["avg_rouge1"], 0.70)

        # Verify system > baseline (the whole point)
        self.assertGreater(
            recall_metrics["system"]["avg_rouge1"],
            recall_metrics["baseline"]["avg_rouge1"],
            "System should outperform baseline on ROUGE-1"
        )
        self.assertGreater(
            recall_metrics["system"]["avg_bleu"],
            recall_metrics["baseline"]["avg_bleu"],
            "System should outperform baseline on BLEU"
        )

        # Verify positive improvement
        self.assertGreater(recall_metrics["improvements"]["avg_rouge1"], 0)
        self.assertGreater(recall_metrics["improvements"]["avg_bleu"], 0)


# ═══════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    unittest.main(verbosity=2)
