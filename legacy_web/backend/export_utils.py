import csv
import json
import os

BASE_DIR = os.path.dirname(__file__)
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")


def save_chart_json(file_id: str, chart: dict) -> str:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, f"{file_id}_chart.json")
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(chart, handle, ensure_ascii=False, indent=2)
    return output_path


def save_analysis_json(file_id: str, analysis: dict) -> str:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, f"{file_id}_analysis.json")
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(analysis, handle, ensure_ascii=False, indent=2)
    return output_path


def save_chart_csv(file_id: str, chart: dict) -> str:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, f"{file_id}_chart.csv")
    with open(output_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["time", "lane", "type"])
        for note in chart.get("notes", []):
            writer.writerow([note.get("time"), note.get("lane"), note.get("type")])
    return output_path
