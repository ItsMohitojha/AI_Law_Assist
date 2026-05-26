import argparse
import json
import logging
import re
import sys
from pathlib import Path
from typing import List, Dict, Any

# Set up standard logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

def split_into_atoms(text: str, max_chars: int) -> List[str]:
    """Hierarchically split text so no piece is > max_chars."""
    # Paragraphs
    paragraphs = []
    for p in re.split(r'(\n\n)', text):
        if p: paragraphs.append(p)

    atoms = []
    for p in paragraphs:
        if len(p) <= max_chars:
            atoms.append(p)
        else:
            # Lines
            lines = []
            for l in re.split(r'(\n)', p):
                if l: lines.append(l)
            for l in lines:
                if len(l) <= max_chars:
                    atoms.append(l)
                else:
                    # Sentences
                    sentences = []
                    for s in re.split(r'((?<=\.)\s+)', l):
                        if s: sentences.append(s)
                    for s in sentences:
                        if len(s) <= max_chars:
                            atoms.append(s)
                        else:
                            # Chars
                            for i in range(0, len(s), max_chars):
                                atoms.append(s[i:i+max_chars])
    return atoms

def chunk_text(text: str, max_chars: int, overlap_chars: int) -> List[str]:
    atoms = split_into_atoms(text, max_chars)

    chunks = []
    current_chunk = ""

    i = 0
    while i < len(atoms):
        atom = atoms[i]
        if len(current_chunk) + len(atom) <= max_chars:
            current_chunk += atom
            i += 1
        else:
            if not current_chunk:
                # Should not happen since we guarantee atoms <= max_chars
                current_chunk = atom
                i += 1
                chunks.append(current_chunk)
                current_chunk = ""
            else:
                chunks.append(current_chunk)

                # Start new chunk with overlap
                # Go backwards from i - 1 to find atoms that fit into overlap_chars
                overlap_text = ""
                j = i - 1
                while j >= 0:
                    if len(overlap_text) + len(atoms[j]) <= overlap_chars:
                        overlap_text = atoms[j] + overlap_text
                        j -= 1
                    else:
                        break

                current_chunk = overlap_text

                # Ensure we make progress in case an atom is too large to fit alongside the overlap
                if len(current_chunk) + len(atom) > max_chars:
                    # The overlap is too big for the next atom to fit.
                    # We have to skip overlap or just accept we'll drop it.
                    # Reset current_chunk to just this atom and advance
                    current_chunk = atom
                    i += 1

    if current_chunk:
        chunks.append(current_chunk)

    return [c.strip() for c in chunks if c.strip()]

def make_stem(name: str) -> str:
    s = name.lower()
    s = re.sub(r'[^a-z0-9_]', '_', s)
    s = re.sub(r'_+', '_', s)
    return s.strip('_')

def process_file(input_path: Path, output_dir: Path, max_chars: int, overlap_chars: int) -> Dict[str, Any]:
    stats = {
        'sections': 0,
        'chunks': 0,
        'chars': 0
    }

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"Failed to read {input_path}: {e}")
        return stats

    act_name = data.get('act_name', 'Unknown Act')
    year = data.get('year', '')
    act_stem = make_stem(act_name)

    sec_label = "Article" if "constitution" in act_name.lower() else "Section"
    act_display = f"{act_name}"
    if year:
        act_display += f" {year}"

    chunks_output = []
    seen_ids = set()

    for struct in data.get('structure', []):
        level = struct.get('level', '')
        s_num = struct.get('number', '')
        s_title = struct.get('title', '')

        struct_display = f"{level} {s_num}".strip()
        if s_title:
            struct_display += f": {s_title}"

        for section in struct.get('sections', []):
            sec_title = section.get('title', '')
            sec_text = section.get('text', '')
            is_repealed = section.get('is_repealed', False)
            sec_num = section.get('section_number', '')

            full_text = f"{sec_title}\n{sec_text}".strip()
            if not full_text:
                continue

            stats['sections'] += 1

            raw_chunks = []
            if is_repealed:
                raw_chunks = [full_text]
            elif len(full_text) <= max_chars:
                raw_chunks = [full_text]
            else:
                raw_chunks = chunk_text(full_text, max_chars, overlap_chars)

            total_chunks = len(raw_chunks)
            stats['chunks'] += total_chunks

            for chunk_idx, raw_content in enumerate(raw_chunks):
                stats['chars'] += len(raw_content)

                # Format chunk id
                safe_sec_num = re.sub(r'[^a-z0-9_]', '_', str(sec_num).lower())
                safe_sec_num = re.sub(r'_+', '_', safe_sec_num).strip('_')
                base_id = f"{act_stem}_sec_{safe_sec_num}_chunk_{chunk_idx}"
                chunk_id = base_id
                counter = 1
                while chunk_id in seen_ids:
                    chunk_id = f"{base_id}_dup{counter}"
                    counter += 1
                seen_ids.add(chunk_id)

                sec_display = f"{sec_label} {sec_num}".strip()
                if sec_title:
                    sec_display += f": {sec_title}"

                content_str = f"Act: {act_display}\n"
                if struct_display:
                    content_str += f"{struct_display}\n"
                content_str += f"{sec_display}\n"
                content_str += "Content:\n"
                content_str += raw_content

                chunk_dict = {
                    "chunk_id": chunk_id,
                    "metadata": {
                        "act_name": act_name,
                        "year": year,
                        "category": data.get('category', ''),
                        "type": data.get('type', ''),
                        "source_file": data.get('source_file', ''),
                        "structure_level": level,
                        "structure_number": s_num,
                        "structure_title": s_title,
                        "section_number": sec_num,
                        "section_title": sec_title,
                        "page_numbers": section.get('page_numbers', []),
                        "is_repealed": is_repealed
                    },
                    "chunk_index": chunk_idx,
                    "total_chunks_in_section": total_chunks,
                    "raw_content": raw_content,
                    "content": content_str
                }
                chunks_output.append(chunk_dict)

    output_path = output_dir / f"{input_path.stem}.json"
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(chunks_output, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to write {output_path}: {e}")

    return stats

def main():
    parser = argparse.ArgumentParser(description="Phase 3: Semantic Chunking")
    parser.add_argument("--input-dir", type=str, default="data/processed/structured_json", help="Input directory containing structured JSONs")
    parser.add_argument("--output-dir", type=str, default="data/processed/chunks", help="Output directory for chunks")
    parser.add_argument("--max-chars", type=int, default=1200, help="Maximum characters per chunk")
    parser.add_argument("--overlap-chars", type=int, default=200, help="Overlap characters between chunks")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)

    if not input_dir.exists():
        logger.error(f"Input directory does not exist: {input_dir}")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    files = list(input_dir.glob("*.json"))
    if not files:
        logger.warning(f"No JSON files found in {input_dir}")
        sys.exit(0)

    logger.info(f"Found {len(files)} files to process.")

    total_files = 0
    total_sections = 0
    total_chunks = 0
    total_chars = 0

    for file_path in files:
        logger.debug(f"Processing {file_path.name}...")
        stats = process_file(file_path, output_dir, args.max_chars, args.overlap_chars)
        if stats['sections'] > 0:
            total_files += 1
            total_sections += stats['sections']
            total_chunks += stats['chunks']
            total_chars += stats['chars']
            logger.info(f"Processed {file_path.name}: {stats['sections']} sections, {stats['chunks']} chunks.")

    logger.info("=== Summary ===")
    logger.info(f"Total files processed: {total_files}")
    logger.info(f"Total sections processed: {total_sections}")
    logger.info(f"Total chunks generated: {total_chunks}")

    if total_sections > 0:
        avg_chunks = total_chunks / total_sections
        logger.info(f"Average chunks per section: {avg_chunks:.2f}")

    if total_chunks > 0:
        avg_chars = total_chars / total_chunks
        logger.info(f"Average chunk character count: {avg_chars:.2f}")

if __name__ == "__main__":
    main()
