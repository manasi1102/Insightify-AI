import pymupdf  # PyMuPDF
fitz = pymupdf
import json
import re
from pathlib import Path
from datetime import datetime

def extract_pdf_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text.strip()

def parse_weekly_report(text, fallback_title):
    lines = text.splitlines()
    content = "\n".join(lines)

    # Extract week range
    week_range = ""
    week_match = re.search(r"Week:\s*(.*)", content)
    if week_match:
        week_range = week_match.group(1).strip()

    # Extract date from start of week range
    date_match = re.search(r"([A-Za-z]+ \d{1,2})\s*[-–]\s*[A-Za-z]*\s*\d{1,2},?\s*(\d{4})", week_range)
    if date_match:
        full_date = f"{date_match.group(1)} {date_match.group(2)}"
        try:
            parsed_date = datetime.strptime(full_date, "%B %d %Y")
            date = parsed_date.strftime("%Y-%m-%d")
        except:
            date = ""
    else:
        date = ""

    # Extract author
    author_match = re.search(r"Author:\s*(.*)", content)
    author = author_match.group(1).strip() if author_match else ""

    # Construct a meaningful title
    if "smartsearch" in fallback_title.lower():
        title = f"SmartSearch Weekly Report – Week of {week_range}" if week_range else fallback_title.replace(".pdf", "").replace("_", " ").title()
    else:
        title = f"Insightify Weekly Report – Week of {week_range}" if week_range else fallback_title.replace(".pdf", "").replace("_", " ").title()

    def extract_section(section_name):
        pattern = rf"{section_name}\n(.*?)(?=\n[A-Z][a-zA-Z ]+\n|\Z)"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            section_text = match.group(1).strip()
            return [line.strip("–•- ").strip() for line in section_text.splitlines() if line.strip()]
        return []

    highlights = extract_section("Highlights")
    next_steps = extract_section("Next Steps")
    top_issues = extract_section("Top Issues")

    # Extract key metrics (basic parsing)
    metrics_raw = extract_section("Key Metrics")
    metrics = {}
    for line in metrics_raw:
        if ":" in line:
            key, value = line.split(":", 1)
            metrics[key.strip().lower().replace(" ", "_")] = value.strip()

    return {
        "title": title,
        "date": date,
        "week_range": week_range,
        "author": author,
        "source": "Weekly Report",
        "type": "weekly_report",
        "highlights": highlights,
        "metrics": metrics,
        "top_issues": top_issues,
        "next_steps": next_steps
    }

def convert_weekly_reports_to_jsonl(pdf_folder, output_jsonl):
    pdf_files = sorted(Path(pdf_folder).glob("*.pdf"))
    jsonl_data = []

    for pdf_file in pdf_files:
        text = extract_pdf_text(pdf_file)
        parsed = parse_weekly_report(text, pdf_file.stem)
        jsonl_data.append(parsed)

    with open(output_jsonl, "w", encoding="utf-8") as f:
        for record in jsonl_data:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"✅ Converted {len(jsonl_data)} PDFs → {output_jsonl}")

# Run the conversion
if __name__ == "__main__":
    convert_weekly_reports_to_jsonl(
        pdf_folder="insightify_weekly_reports_20",                      # Change this path if needed
        output_jsonl="weekly_reports_structured.jsonl"
    )
