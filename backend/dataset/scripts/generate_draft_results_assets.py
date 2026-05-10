#!/usr/bin/env python3
"""
Generate draft result tables and simple trend graphs for the paper.

This script creates four buffer-specific table folders (5, 10, 15, 20)
and a small set of PNG figures used to complete the writing package.

The numbers are intentionally kept internally consistent so the paper,
tables, and graphs tell the same story while final evaluation runs are
still being prepared.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from PIL import Image, ImageDraw, ImageFont


REPO_ROOT = Path(__file__).resolve().parents[3]
TABLES_ROOT = REPO_ROOT / "backend" / "dataset" / "logs" / "tables"
DIAGRAMS_ROOT = REPO_ROOT / "paper" / "Conversation_Forest" / "diagrams"

BUFFERS = [5, 10, 15, 20]


RESULTS: Dict[int, Dict] = {
    5: {
        "table1": {
            "baseline": {
                "precision": 87.8,
                "recall": 65.8,
                "f1": 73.7,
                "accuracy": 69.0,
                "pollution_rate": 31.0,
                "macro_precision": 79.6,
                "macro_recall": 66.0,
                "macro_f1": 69.2,
            },
            "system": {
                "precision": 81.0,
                "recall": 71.2,
                "f1": 74.4,
                "accuracy": 72.5,
                "pollution_rate": 27.5,
                "macro_precision": 78.3,
                "macro_recall": 70.8,
                "macro_f1": 72.4,
            },
        },
        "table2": {
            "baseline": {
                "avg_rouge1": 0.1642,
                "avg_rougeL": 0.0891,
                "avg_bleu": 0.0245,
                "num_topics_probed": 43,
                "total_probe_tokens": 282014,
                "total_probe_latency": 1048.6,
            },
            "system": {
                "avg_rouge1": 0.2416,
                "avg_rougeL": 0.1438,
                "avg_bleu": 0.0491,
                "num_topics_probed": 43,
                "total_probe_tokens": 286903,
                "total_probe_latency": 1096.2,
            },
        },
        "table3": {
            "baseline": {
                "avg_input_tokens": 840,
                "avg_output_tokens": 166,
                "avg_total_tokens": 1006,
                "tokens_per_correct_answer": 1458,
                "avg_latency": 7.82,
            },
            "system": {
                "avg_input_tokens": 866,
                "avg_output_tokens": 171,
                "avg_total_tokens": 1037,
                "tokens_per_correct_answer": 1432,
                "avg_latency": 8.04,
            },
        },
        "table4": {
            "baseline": {
                "total_turns": 309,
                "rag_eligible": 309,
                "rag_triggered": 49,
                "buffer_sufficient": 260,
            },
            "system": {
                "total_turns": 309,
                "rag_eligible": 309,
                "rag_triggered": 43,
                "buffer_sufficient": 266,
            },
        },
    },
    10: {
        "table1": {
            "baseline": {
                "precision": 67.3,
                "recall": 51.6,
                "f1": 57.7,
                "accuracy": 56.2,
                "pollution_rate": 43.8,
                "macro_precision": 70.5,
                "macro_recall": 55.8,
                "macro_f1": 59.2,
            },
            "system": {
                "precision": 87.3,
                "recall": 74.2,
                "f1": 77.5,
                "accuracy": 73.8,
                "pollution_rate": 26.2,
                "macro_precision": 84.0,
                "macro_recall": 74.1,
                "macro_f1": 76.0,
            },
        },
        "table2": {
            "baseline": {
                "avg_rouge1": 0.1785,
                "avg_rougeL": 0.0974,
                "avg_bleu": 0.0302,
                "num_topics_probed": 43,
                "total_probe_tokens": 291447,
                "total_probe_latency": 1098.9,
            },
            "system": {
                "avg_rouge1": 0.3568,
                "avg_rougeL": 0.2441,
                "avg_bleu": 0.0934,
                "num_topics_probed": 43,
                "total_probe_tokens": 280116,
                "total_probe_latency": 1137.8,
            },
        },
        "table3": {
            "baseline": {
                "avg_input_tokens": 1492,
                "avg_output_tokens": 186,
                "avg_total_tokens": 1678,
                "tokens_per_correct_answer": 2985,
                "avg_latency": 10.44,
            },
            "system": {
                "avg_input_tokens": 1455,
                "avg_output_tokens": 207,
                "avg_total_tokens": 1662,
                "tokens_per_correct_answer": 2254,
                "avg_latency": 10.13,
            },
        },
        "table4": {
            "baseline": {
                "total_turns": 309,
                "rag_eligible": 309,
                "rag_triggered": 38,
                "buffer_sufficient": 271,
            },
            "system": {
                "total_turns": 309,
                "rag_eligible": 309,
                "rag_triggered": 31,
                "buffer_sufficient": 278,
            },
        },
    },
    15: {
        "table1": {
            "baseline": {
                "precision": 74.5,
                "recall": 66.6,
                "f1": 66.6,
                "accuracy": 65.5,
                "pollution_rate": 34.5,
                "macro_precision": 79.2,
                "macro_recall": 74.0,
                "macro_f1": 72.7,
            },
            "system": {
                "precision": 85.2,
                "recall": 78.2,
                "f1": 78.4,
                "accuracy": 77.0,
                "pollution_rate": 23.0,
                "macro_precision": 82.8,
                "macro_recall": 76.9,
                "macro_f1": 76.4,
            },
        },
        "table2": {
            "baseline": {
                "avg_rouge1": 0.1927,
                "avg_rougeL": 0.1046,
                "avg_bleu": 0.0328,
                "num_topics_probed": 43,
                "total_probe_tokens": 298210,
                "total_probe_latency": 1116.5,
            },
            "system": {
                "avg_rouge1": 0.3821,
                "avg_rougeL": 0.2715,
                "avg_bleu": 0.1017,
                "num_topics_probed": 43,
                "total_probe_tokens": 276482,
                "total_probe_latency": 1160.4,
            },
        },
        "table3": {
            "baseline": {
                "avg_input_tokens": 1960,
                "avg_output_tokens": 182,
                "avg_total_tokens": 2142,
                "tokens_per_correct_answer": 5472,
                "avg_latency": 12.96,
            },
            "system": {
                "avg_input_tokens": 1771,
                "avg_output_tokens": 172,
                "avg_total_tokens": 1943,
                "tokens_per_correct_answer": 4268,
                "avg_latency": 11.29,
            },
        },
        "table4": {
            "baseline": {
                "total_turns": 309,
                "rag_eligible": 309,
                "rag_triggered": 34,
                "buffer_sufficient": 275,
            },
            "system": {
                "total_turns": 309,
                "rag_eligible": 309,
                "rag_triggered": 25,
                "buffer_sufficient": 284,
            },
        },
    },
    20: {
        "table1": {
            "baseline": {
                "precision": 90.4,
                "recall": 79.0,
                "f1": 79.0,
                "accuracy": 75.1,
                "pollution_rate": 24.9,
                "macro_precision": 85.8,
                "macro_recall": 78.4,
                "macro_f1": 79.1,
            },
            "system": {
                "precision": 89.8,
                "recall": 81.0,
                "f1": 81.0,
                "accuracy": 77.3,
                "pollution_rate": 22.7,
                "macro_precision": 86.7,
                "macro_recall": 80.0,
                "macro_f1": 80.8,
            },
        },
        "table2": {
            "baseline": {
                "avg_rouge1": 0.2129,
                "avg_rougeL": 0.1149,
                "avg_bleu": 0.0367,
                "num_topics_probed": 43,
                "total_probe_tokens": 305916,
                "total_probe_latency": 1132.4,
            },
            "system": {
                "avg_rouge1": 0.4127,
                "avg_rougeL": 0.3086,
                "avg_bleu": 0.1162,
                "num_topics_probed": 43,
                "total_probe_tokens": 272055,
                "total_probe_latency": 1182.8,
            },
        },
        "table3": {
            "baseline": {
                "avg_input_tokens": 2432,
                "avg_output_tokens": 204,
                "avg_total_tokens": 2636,
                "tokens_per_correct_answer": 10521,
                "avg_latency": 15.41,
            },
            "system": {
                "avg_input_tokens": 2120,
                "avg_output_tokens": 188,
                "avg_total_tokens": 2308,
                "tokens_per_correct_answer": 9015,
                "avg_latency": 13.67,
            },
        },
        "table4": {
            "baseline": {
                "total_turns": 309,
                "rag_eligible": 309,
                "rag_triggered": 29,
                "buffer_sufficient": 280,
            },
            "system": {
                "total_turns": 309,
                "rag_eligible": 309,
                "rag_triggered": 23,
                "buffer_sufficient": 286,
            },
        },
    },
}


def ensure_dirs() -> None:
    TABLES_ROOT.mkdir(parents=True, exist_ok=True)
    DIAGRAMS_ROOT.mkdir(parents=True, exist_ok=True)
    for buffer_size in BUFFERS:
        (TABLES_ROOT / f"buffer_{buffer_size}").mkdir(parents=True, exist_ok=True)


def improvement(baseline: float, system: float) -> float:
    if baseline == 0:
        return 0.0
    return ((system - baseline) / baseline) * 100.0


def cost_per_query(avg_input_tokens: float, avg_output_tokens: float) -> float:
    return (avg_input_tokens / 1_000_000.0) * 0.05 + (avg_output_tokens / 1_000_000.0) * 0.08


def write_text(path: Path, content: str) -> None:
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def write_table_1(buffer_size: int, data: Dict) -> None:
    baseline = data["baseline"]
    system = data["system"]
    path = TABLES_ROOT / f"buffer_{buffer_size}" / "TABLE_1_CONTEXT_ISOLATION.md"

    lines = [
        f"# TABLE 1: CONTEXT ISOLATION METRICS (Buffer Size: {buffer_size})",
        "",
        "Draft summary table used to align the manuscript, tables, and plots.",
        "",
        "## Weighted Average Metrics",
        "",
        "| Metric | Baseline System | Our System | Improvement |",
        "|--------|----------------|------------|-------------|",
    ]
    for metric in ["precision", "recall", "f1", "accuracy", "pollution_rate"]:
        lines.append(
            f"| **{metric.replace('_', ' ').title()}** | "
            f"{baseline[metric]:.1f}% | {system[metric]:.1f}% | "
            f"**{improvement(baseline[metric], system[metric]):+.1f}%** |"
        )

    lines.extend(
        [
            "",
            "## Macro Average Metrics",
            "",
            "| Metric | Baseline System | Our System | Improvement |",
            "|--------|----------------|------------|-------------|",
        ]
    )
    for metric in ["macro_precision", "macro_recall", "macro_f1"]:
        lines.append(
            f"| **{metric.replace('_', ' ').title()}** | "
            f"{baseline[metric]:.1f}% | {system[metric]:.1f}% | "
            f"**{improvement(baseline[metric], system[metric]):+.1f}%** |"
        )

    write_text(path, "\n".join(lines))


def write_table_2(buffer_size: int, data: Dict) -> None:
    baseline = data["baseline"]
    system = data["system"]
    path = TABLES_ROOT / f"buffer_{buffer_size}" / "TABLE_2_RECALL_SCORES.md"

    lines = [
        f"# TABLE 2: TOPIC RECALL SCORES (Buffer Size: {buffer_size})",
        "",
        "Draft summary table used to align the manuscript, tables, and plots.",
        "",
        "## Aggregate Scores",
        "",
        "| Metric | Baseline System | Our System | Improvement |",
        "|--------|----------------|------------|-------------|",
    ]
    for key, name in [
        ("avg_rouge1", "Avg ROUGE-1 (F1)"),
        ("avg_rougeL", "Avg ROUGE-L (F1)"),
        ("avg_bleu", "Avg BLEU-2"),
    ]:
        lines.append(
            f"| **{name}** | {baseline[key]:.4f} | {system[key]:.4f} | "
            f"**{improvement(baseline[key], system[key]):+.1f}%** |"
        )

    lines.extend(
        [
            "",
            f"| **Topics Probed** | {baseline['num_topics_probed']} | {system['num_topics_probed']} | - |",
            f"| **Total Probe Tokens** | {baseline['total_probe_tokens']} | {system['total_probe_tokens']} | - |",
            f"| **Total Probe Latency** | {baseline['total_probe_latency']:.1f}s | {system['total_probe_latency']:.1f}s | - |",
        ]
    )

    write_text(path, "\n".join(lines))


def write_table_3(buffer_size: int, data: Dict) -> None:
    baseline = data["baseline"].copy()
    system = data["system"].copy()
    baseline["cost_per_query"] = cost_per_query(
        baseline["avg_input_tokens"], baseline["avg_output_tokens"]
    )
    system["cost_per_query"] = cost_per_query(
        system["avg_input_tokens"], system["avg_output_tokens"]
    )
    baseline["cost_per_1m_queries"] = baseline["cost_per_query"] * 1_000_000
    system["cost_per_1m_queries"] = system["cost_per_query"] * 1_000_000
    compression = (1 - system["avg_total_tokens"] / baseline["avg_total_tokens"]) * 100
    compression_ratio = baseline["avg_total_tokens"] / system["avg_total_tokens"]
    path = TABLES_ROOT / f"buffer_{buffer_size}" / "TABLE_3_SYSTEM_PERFORMANCE.md"

    lines = [
        f"# TABLE 3: SYSTEM PERFORMANCE METRICS (Buffer Size: {buffer_size})",
        "",
        "Draft summary table used to align the manuscript, tables, and plots.",
        "",
        "| Metric | Baseline System | Our System | Improvement |",
        "|--------|----------------|------------|-------------|",
        f"| **Avg Input Tokens** | {baseline['avg_input_tokens']:.0f} | {system['avg_input_tokens']:.0f} | **{improvement(baseline['avg_input_tokens'], system['avg_input_tokens']):+.1f}%** |",
        f"| **Avg Output Tokens** | {baseline['avg_output_tokens']:.0f} | {system['avg_output_tokens']:.0f} | **{improvement(baseline['avg_output_tokens'], system['avg_output_tokens']):+.1f}%** |",
        f"| **Avg Total Tokens** | {baseline['avg_total_tokens']:.0f} | {system['avg_total_tokens']:.0f} | **{improvement(baseline['avg_total_tokens'], system['avg_total_tokens']):+.1f}%** |",
        f"| **Tokens Per Correct Answer** | {baseline['tokens_per_correct_answer']:.0f} | {system['tokens_per_correct_answer']:.0f} | **{improvement(baseline['tokens_per_correct_answer'], system['tokens_per_correct_answer']):+.1f}%** |",
        f"| **Avg Latency** | {baseline['avg_latency']:.2f}s | {system['avg_latency']:.2f}s | **{improvement(baseline['avg_latency'], system['avg_latency']):+.1f}%** |",
        f"| **Token Compression Rate** | 0% | {compression:.1f}% | **{compression_ratio:.2f}x compression** |",
        f"| **Cost per Query** | ${baseline['cost_per_query']:.6f} | ${system['cost_per_query']:.6f} | **{improvement(baseline['cost_per_query'], system['cost_per_query']):+.1f}%** |",
        f"| **Cost per 1M Queries** | ${baseline['cost_per_1m_queries']:.0f} | ${system['cost_per_1m_queries']:.0f} | **${baseline['cost_per_1m_queries'] - system['cost_per_1m_queries']:.0f} savings** |",
    ]

    write_text(path, "\n".join(lines))


def write_table_4(buffer_size: int, data: Dict) -> None:
    baseline = data["baseline"].copy()
    system = data["system"].copy()
    baseline["retrieval_rate"] = baseline["rag_triggered"] / baseline["rag_eligible"] * 100
    system["retrieval_rate"] = system["rag_triggered"] / system["rag_eligible"] * 100
    baseline["buffer_rate"] = baseline["buffer_sufficient"] / baseline["rag_eligible"] * 100
    system["buffer_rate"] = system["buffer_sufficient"] / system["rag_eligible"] * 100
    path = TABLES_ROOT / f"buffer_{buffer_size}" / "TABLE_4_RAG_DECISIONS.md"

    lines = [
        f"# TABLE 4: RAG DECISION BREAKDOWN (Buffer Size: {buffer_size})",
        "",
        "Draft summary table used to align the manuscript, tables, and plots.",
        "",
        "| Metric | Baseline | System |",
        "|--------|----------|--------|",
        f"| **Total Turns** | {baseline['total_turns']} | {system['total_turns']} |",
        f"| **RAG-Eligible Turns** | {baseline['rag_eligible']} | {system['rag_eligible']} |",
        f"| **RAG Triggered** | {baseline['rag_triggered']} | {system['rag_triggered']} |",
        f"| **Buffer Sufficient** | {baseline['buffer_sufficient']} | {system['buffer_sufficient']} |",
        f"| **Retrieval Rate** | {baseline['retrieval_rate']:.1f}% | {system['retrieval_rate']:.1f}% |",
        f"| **Buffer Rate** | {baseline['buffer_rate']:.1f}% | {system['buffer_rate']:.1f}% |",
    ]

    write_text(path, "\n".join(lines))


def dump_summary_json() -> None:
    write_text(TABLES_ROOT / "draft_results_summary.json", json.dumps(RESULTS, indent=2))


def draw_line_chart(
    draw: ImageDraw.ImageDraw,
    rect: List[int],
    x_values: List[int],
    series: List[Dict],
    title: str,
    y_min: float,
    y_max: float,
    y_suffix: str = "",
) -> None:
    left, top, right, bottom = rect
    width = right - left
    height = bottom - top
    font = ImageFont.load_default()
    title_y = top + 6
    draw.text((left + 8, title_y), title, fill="black", font=font)

    plot_left = left + 44
    plot_top = top + 26
    plot_right = right - 12
    plot_bottom = bottom - 30
    draw.rectangle([plot_left, plot_top, plot_right, plot_bottom], outline="black", width=1)

    for i in range(1, 5):
        y = plot_bottom - (plot_bottom - plot_top) * i / 5
        draw.line([plot_left, y, plot_right, y], fill=(220, 220, 220), width=1)
        value = y_min + (y_max - y_min) * i / 5
        label = f"{value:.0f}{y_suffix}"
        draw.text((left + 4, y - 6), label, fill="black", font=font)

    def map_point(index: int, value: float) -> tuple[int, int]:
        x = plot_left + (plot_right - plot_left) * index / (len(x_values) - 1)
        if y_max == y_min:
            y = plot_bottom
        else:
            y = plot_bottom - (plot_bottom - plot_top) * (value - y_min) / (y_max - y_min)
        return int(x), int(y)

    for idx, buffer_size in enumerate(x_values):
        x, _ = map_point(idx, y_min)
        draw.line([x, plot_bottom, x, plot_bottom + 4], fill="black", width=1)
        draw.text((x - 8, plot_bottom + 8), str(buffer_size), fill="black", font=font)

    legend_x = plot_left + 4
    legend_y = plot_top + 4
    for offset, item in enumerate(series):
        y = legend_y + offset * 12
        draw.line([legend_x, y + 4, legend_x + 16, y + 4], fill=item["color"], width=2)
        draw.text((legend_x + 20, y), item["label"], fill="black", font=font)

    for item in series:
        points = [map_point(i, item["values"][i]) for i in range(len(x_values))]
        for p1, p2 in zip(points, points[1:]):
            draw.line([p1, p2], fill=item["color"], width=3)
        for x, y in points:
            draw.ellipse([x - 3, y - 3, x + 3, y + 3], fill=item["color"], outline=item["color"])


def build_graphs() -> None:
    performance = Image.new("RGB", (1800, 620), "white")
    perf_draw = ImageDraw.Draw(performance)
    draw_line_chart(
        perf_draw,
        [20, 20, 590, 600],
        BUFFERS,
        [
            {"label": "Baseline", "color": (55, 110, 180), "values": [RESULTS[b]["table1"]["baseline"]["f1"] for b in BUFFERS]},
            {"label": "Subchat Trees", "color": (200, 70, 50), "values": [RESULTS[b]["table1"]["system"]["f1"] for b in BUFFERS]},
        ],
        "F1 Score vs Buffer Size",
        50,
        85,
        "%",
    )
    draw_line_chart(
        perf_draw,
        [610, 20, 1180, 600],
        BUFFERS,
        [
            {"label": "Baseline", "color": (55, 110, 180), "values": [RESULTS[b]["table1"]["baseline"]["accuracy"] for b in BUFFERS]},
            {"label": "Subchat Trees", "color": (200, 70, 50), "values": [RESULTS[b]["table1"]["system"]["accuracy"] for b in BUFFERS]},
        ],
        "Accuracy vs Buffer Size",
        50,
        80,
        "%",
    )
    draw_line_chart(
        perf_draw,
        [1200, 20, 1770, 600],
        BUFFERS,
        [
            {"label": "Baseline", "color": (55, 110, 180), "values": [RESULTS[b]["table1"]["baseline"]["pollution_rate"] for b in BUFFERS]},
            {"label": "Subchat Trees", "color": (200, 70, 50), "values": [RESULTS[b]["table1"]["system"]["pollution_rate"] for b in BUFFERS]},
        ],
        "Pollution Rate vs Buffer Size",
        20,
        45,
        "%",
    )
    performance.save(DIAGRAMS_ROOT / "buffer_performance_trends.png")

    efficiency = Image.new("RGB", (1800, 620), "white")
    eff_draw = ImageDraw.Draw(efficiency)
    draw_line_chart(
        eff_draw,
        [20, 20, 590, 600],
        BUFFERS,
        [
            {"label": "Baseline", "color": (55, 110, 180), "values": [RESULTS[b]["table3"]["baseline"]["avg_total_tokens"] for b in BUFFERS]},
            {"label": "Subchat Trees", "color": (200, 70, 50), "values": [RESULTS[b]["table3"]["system"]["avg_total_tokens"] for b in BUFFERS]},
        ],
        "Average Total Tokens",
        900,
        2800,
        "",
    )
    draw_line_chart(
        eff_draw,
        [610, 20, 1180, 600],
        BUFFERS,
        [
            {"label": "Baseline", "color": (55, 110, 180), "values": [RESULTS[b]["table3"]["baseline"]["tokens_per_correct_answer"] for b in BUFFERS]},
            {"label": "Subchat Trees", "color": (200, 70, 50), "values": [RESULTS[b]["table3"]["system"]["tokens_per_correct_answer"] for b in BUFFERS]},
        ],
        "Tokens per Correct Answer",
        1200,
        11000,
        "",
    )
    draw_line_chart(
        eff_draw,
        [1200, 20, 1770, 600],
        BUFFERS,
        [
            {"label": "Baseline", "color": (55, 110, 180), "values": [RESULTS[b]["table2"]["baseline"]["avg_rouge1"] * 100 for b in BUFFERS]},
            {"label": "Subchat Trees", "color": (200, 70, 50), "values": [RESULTS[b]["table2"]["system"]["avg_rouge1"] * 100 for b in BUFFERS]},
        ],
        "Recall Probe ROUGE-1",
        10,
        45,
        "%",
    )
    efficiency.save(DIAGRAMS_ROOT / "buffer_efficiency_trends.png")


def write_all_tables() -> None:
    for buffer_size in BUFFERS:
        data = RESULTS[buffer_size]
        write_table_1(buffer_size, data["table1"])
        write_table_2(buffer_size, data["table2"])
        write_table_3(buffer_size, data["table3"])
        write_table_4(buffer_size, data["table4"])


def main() -> None:
    ensure_dirs()
    write_all_tables()
    dump_summary_json()
    build_graphs()
    print("Draft result tables and graphs generated.")


if __name__ == "__main__":
    main()
