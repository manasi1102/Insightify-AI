import os
import json
import re
from pathlib import Path

def parse_kb_note_txt(lines):
    """Parse standard KB note files with Title/Date/Source headers."""
    try:
        title = lines[0].replace("Title:", "").strip()
        date = lines[1].replace("Date:", "").strip()
        source = lines[2].replace("Source:", "").strip()
        content = "\n".join(lines[4:]).strip()
        return {
            "title": title,
            "date": date,
            "source": source,
            "type": "insight_note",
            "text": content
        }
    except Exception as e:
        print("⚠️ Error parsing KB note:", e)
        return None

def parse_email_txt(lines):
    """Parse Insightify-style emails with From/To/Date/Subject headers."""
    headers = {}
    body_lines = []
    in_body = False

    for line in lines:
        line = line.strip()
        if not line and not in_body:
            in_body = True
            continue
        if not in_body:
            if line.startswith("From:"):
                headers["from"] = line.replace("From:", "").strip()
            elif line.startswith("To:"):
                headers["to"] = line.replace("To:", "").strip()
            elif line.startswith("Date:"):
                headers["date"] = line.replace("Date:", "").strip()
            elif line.startswith("Subject:"):
                headers["title"] = line.replace("Subject:", "").strip()
        else:
            body_lines.append(line)

    return {
        "title": headers.get("title", "No Subject"),
        "date": headers.get("date", "Unknown"),
        "source": "Internal Email",
        "from": headers.get("from", ""),
        "to": headers.get("to", ""),
        "type": "internal_email",
        "text": "\n".join(body_lines).strip()
    }

def parse_transcript_txt(lines):
    """Parse transcript with [date | title] as header."""
    match = re.match(r"\[(\d{4}-\d{2}-\d{2}) \| (.+?)\]", lines[0])
    if not match:
        print("⚠️ Header not in expected format for transcript.")
        return None

    date = match.group(1)
    title = match.group(2)
    content = "\n".join(lines[2:]).strip()
    return {
        "title": title,
        "date": date,
        "source": "Transcript",
        "type": "meeting_transcript",
        "text": content
    }

def convert_txt_folder_to_jsonl(input_folder, output_jsonl_path, doc_type="auto"):
    input_path = Path(input_folder)
    jsonl_data = []

    for txt_file in sorted(input_path.glob("*.txt")):
        with open(txt_file, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()

        # Choose the right parser based on format or override
        if doc_type == "internal_email" or any("From:" in line for line in lines[:5]):
            parsed = parse_email_txt(lines)
        elif doc_type == "meeting_transcript" or re.match(r"\[\d{4}-\d{2}-\d{2} \| ", lines[0]):
            parsed = parse_transcript_txt(lines)
        elif doc_type == "insight_note" or lines[0].startswith("Title:"):
            parsed = parse_kb_note_txt(lines)
        else:
            print(f"⚠️ Unknown format for {txt_file.name}")
            continue

        if parsed:
            jsonl_data.append(parsed)

    with open(output_jsonl_path, "w", encoding="utf-8") as f:
        for record in jsonl_data:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"✅ Converted {len(jsonl_data)} files to {output_jsonl_path}")

# Example usage:
convert_txt_folder_to_jsonl("emails", "internal_emails.jsonl", doc_type="internal_email")
# convert_txt_folder_to_jsonl("transcripts", "meeting_transcripts.jsonl", doc_type="meeting_transcript")
# convert_txt_folder_to_jsonl("insightify_kb_notes", "insightify_kb_notes.jsonl", doc_type="insight_note")
