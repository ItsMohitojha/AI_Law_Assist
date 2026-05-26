import argparse
import json
import logging
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CATEGORY_MAP = {
    'code_of_civil_procedure_1908': 'civil',
    'indian_contract_act_1872': 'civil',
    'constitution_of_india': 'constitutional',
    'consumer_protection_act_2019': 'consumer',
    'bharatiya_nagarik_suraksha_sanhita_2023': 'criminal',
    'bharatiya_nyaya_sanhita_2023': 'criminal',
    'bharatiya_sakshya_adhiniyam_2023': 'criminal',
    'indian_panel_code': 'criminal',
    'prevention_of_corruption_act_1988': 'criminal',
    'information_technology_act_2000': 'cyber',
    'ugc_regulations': 'education',
    'industrial_disputes_act': 'labor',
    'motor_vehicles_act_1988': 'transport',
    'protection_of_women_from_domestic_violence_act_2005': 'women_protection'
}

@dataclass
class SectionNode:
    section_number: str
    title: str
    text: str
    page_numbers: List[int]
    is_repealed: bool

@dataclass
class StructureNode:
    level: str
    number: str
    title: str
    sections: List[SectionNode] = field(default_factory=list)

@dataclass
class ActDocument:
    act_name: str
    year: Optional[int]
    category: str
    type: str
    source_file: str
    structure: List[StructureNode] = field(default_factory=list)

def get_metadata(filename: str):
    stem = Path(filename).stem
    category = CATEGORY_MAP.get(stem, 'unknown')
    parts = stem.split('_')
    year = None
    if parts and parts[-1].isdigit():
        year = int(parts[-1])
        act_name = ' '.join(p.capitalize() for p in parts[:-1])
    else:
        act_name = ' '.join(p.capitalize() for p in parts)

    return act_name, year, category

def parse_text(text: str, is_constitution: bool) -> List[StructureNode]:
    lines = text.split('\n')
    current_page = 1

    structures = []
    current_structure = StructureNode(level="preamble", number="", title="Preamble")
    structures.append(current_structure)

    current_section = None
    current_section_text = []

    page_re = re.compile(r'^===\s*Page\s+(\d+)\s*===$', re.IGNORECASE)
    struct_re = re.compile(r'^(PART|CHAPTER|ORDER|SCHEDULE|RULE|RULES)\s+([A-Z0-9IVX]+)(?:[\.\-:]\s*(.*))?$', re.IGNORECASE)

    if is_constitution:
        section_re = re.compile(r'^(?:Article\s+)?(\d+[A-Z]*)\.\s*(.*)', re.IGNORECASE)
    else:
        section_re = re.compile(r'^(?:Section\s+)?(\d+[A-Z]*)\.\s*(.*)', re.IGNORECASE)

    def finalize_section():
        nonlocal current_section, current_section_text
        if current_section:
            full_text = '\n'.join(current_section_text).strip()
            current_section.text = full_text
            if '[Repealed' in full_text or '[Repealed' in current_section.title or 'Repealed.' in full_text:
                current_section.is_repealed = True
            current_structure.sections.append(current_section)
        current_section = None
        current_section_text = []

    for line in lines:
        stripped = line.strip()

        page_match = page_re.match(stripped)
        if page_match:
            current_page = int(page_match.group(1))
            continue

        struct_match = struct_re.match(stripped)
        if struct_match:
            finalize_section()
            current_structure = StructureNode(
                level=struct_match.group(1).lower(),
                number=struct_match.group(2),
                title=(struct_match.group(3) or '').strip()
            )
            structures.append(current_structure)
            continue

        # Match only at the beginning of the line to avoid matching list items in text
        if not line.startswith(' ') and not line.startswith('\t'):
            sec_match = section_re.match(line)
            if sec_match:
                finalize_section()
                sec_num = sec_match.group(1)
                sec_title = (sec_match.group(2) or '').strip()
                is_repealed = '[Repealed' in sec_title or 'Repealed.' in sec_title

                current_section = SectionNode(
                    section_number=sec_num,
                    title=sec_title,
                    text="",
                    page_numbers=[current_page],
                    is_repealed=is_repealed
                )
                continue

        if current_section:
            current_section_text.append(line)
            if current_page not in current_section.page_numbers:
                current_section.page_numbers.append(current_page)
        elif current_structure and not current_section:
            # Append to structure title if we haven't started a section
            if stripped and not stripped.startswith("==="):
                if not current_structure.title:
                    current_structure.title = stripped
                else:
                    current_structure.title += " " + stripped

    finalize_section()

    if structures and structures[0].level == "preamble" and not structures[0].sections:
        structures.pop(0)

    return structures

def process_file(filepath: Path, out_dir: Path):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    act_name, year, category = get_metadata(filepath.name)
    is_constitution = 'constitution' in filepath.name.lower()

    structures = parse_text(text, is_constitution)

    doc = ActDocument(
        act_name=act_name,
        year=year,
        category=category,
        type='statute',
        source_file=filepath.name,
        structure=structures
    )

    out_file = out_dir / f"{filepath.stem}.json"
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(asdict(doc), f, indent=2, ensure_ascii=False)

    return len(structures), sum(len(s.sections) for s in structures)

def main():
    parser = argparse.ArgumentParser(description="Structure extracted text into JSON")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    in_dir = Path("data/processed/extracted_text")
    out_dir = Path("data/processed/structured_json")

    out_dir.mkdir(parents=True, exist_ok=True)

    if not in_dir.exists():
        logger.error(f"Input directory {in_dir} does not exist.")
        return

    processed = 0
    total_structures = 0
    total_sections = 0

    for txt_file in in_dir.glob("*.txt"):
        logger.debug(f"Processing {txt_file.name}...")
        try:
            structs, sects = process_file(txt_file, out_dir)
            logger.info(f"Processed {txt_file.name}: {structs} structures, {sects} sections/articles")
            processed += 1
            total_structures += structs
            total_sections += sects
        except Exception as e:
            logger.error(f"Error processing {txt_file.name}: {e}", exc_info=True)

    logger.info(f"Finished parsing. Processed {processed} files.")
    logger.info(f"Total structures extracted: {total_structures}")
    logger.info(f"Total sections extracted: {total_sections}")

if __name__ == "__main__":
    main()
