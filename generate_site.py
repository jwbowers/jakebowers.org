#!/usr/bin/env python3
"""
Generate a static academic website from templates and data.

This script reads a BibTeX file for publications, YAML files for teaching and
projects, and a Markdown file for the biography.  It then renders HTML
pages using Jinja2 templates.  The resulting HTML files are written
into the root of the project directory.

To use this script:

1. Place your `vita.bib` file in the `data` directory.
2. Update `config.yaml` with your name, site name and optional vita PDF path.
3. Edit `bio.md`, `teaching.yaml` and `projects.yaml` in the `data` directory
   to reflect your biography, courses and research projects.
4. Run `python generate_site.py` from the root of the repository to produce
   `index.html`, `publications.html`, `projects.html` and `teaching.html`.

The script requires the Python packages `jinja2` and `PyYAML`, both of
which are available in this environment.  It does not depend on external
libraries for BibTeX parsing; instead, it implements a minimal parser
for common fields.
"""

import os
import re
import datetime
import yaml
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape


MONTH_ABBREVIATIONS = {
    '1': 'Jan.',
    '2': 'Feb.',
    '3': 'Mar.',
    '4': 'Apr.',
    '5': 'May',
    '6': 'Jun.',
    '7': 'Jul.',
    '8': 'Aug.',
    '9': 'Sept.',
    '10': 'Oct.',
    '11': 'Nov.',
    '12': 'Dec.',
    'jan': 'Jan.',
    'feb': 'Feb.',
    'mar': 'Mar.',
    'apr': 'Apr.',
    'may': 'May',
    'jun': 'Jun.',
    'jul': 'Jul.',
    'aug': 'Aug.',
    'sep': 'Sept.',
    'sept': 'Sept.',
    'oct': 'Oct.',
    'nov': 'Nov.',
    'dec': 'Dec.',
}

MONTH_NUMBERS = {
    '1': 1,
    '2': 2,
    '3': 3,
    '4': 4,
    '5': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    '9': 9,
    '10': 10,
    '11': 11,
    '12': 12,
    'jan': 1,
    'january': 1,
    'feb': 2,
    'february': 2,
    'mar': 3,
    'march': 3,
    'apr': 4,
    'april': 4,
    'may': 5,
    'jun': 6,
    'june': 6,
    'jul': 7,
    'july': 7,
    'aug': 8,
    'august': 8,
    'sep': 9,
    'sept': 9,
    'september': 9,
    'oct': 10,
    'october': 10,
    'nov': 11,
    'november': 11,
    'dec': 12,
    'december': 12,
}


def safe_year(year_value: str) -> int:
    digits = re.sub(r'\D', '', year_value or '')
    return int(digits) if digits else 0


def format_authors(author_field: str) -> str:
    if not author_field:
        return ''
    parts = [part.strip() for part in author_field.split(' and ') if part.strip()]
    if len(parts) <= 1:
        return parts[0] if parts else ''
    if len(parts) == 2:
        return f'{parts[0]} and {parts[1]}'
    return f"{', '.join(parts[:-1])}, and {parts[-1]}"


def format_month(month_value: str) -> str:
    if not month_value:
        return ''
    normalized = month_value.strip().lower()
    if normalized.isdigit():
        normalized = str(int(normalized))
    return MONTH_ABBREVIATIONS.get(normalized, '')


def format_date(entry: dict) -> str:
    year = (entry.get('year') or '').strip()
    month = format_month(entry.get('month') or '')
    if month and year:
        return f'{month} {year}'
    return year


def month_number(month_value: str) -> int:
    if not month_value:
        return 0
    normalized = month_value.strip().lower()
    if normalized.isdigit():
        normalized = str(int(normalized))
    return MONTH_NUMBERS.get(normalized, 0)


def parse_keywords(entry: dict) -> list[str]:
    raw = entry.get('keywords') or entry.get('keyword') or ''
    parts = re.split(r'[;,]', raw)
    return [part.strip().lower() for part in parts if part.strip()]


def slugify_key(value: str) -> str:
    if not value:
        return ''
    slug = re.sub(r'[^A-Za-z0-9_-]+', '_', value)
    return slug.strip('_')


def is_pdf_url(url: str) -> bool:
    if not url:
        return False
    lowered = url.lower()
    return lowered.endswith('.pdf') or 'static/papers/' in lowered


def build_pdf_index(pdf_dir: Path | None) -> dict[str, str]:
    if not pdf_dir or not pdf_dir.exists():
        return {}
    pdf_index: dict[str, str] = {}
    for path in pdf_dir.iterdir():
        if path.is_file() and path.suffix.lower() == '.pdf':
            pdf_index[path.name.lower()] = path.name
    return pdf_index


def load_pdf_map(pdf_map_path: Path) -> dict[str, str]:
    if not pdf_map_path.exists():
        return {}
    data = yaml.safe_load(pdf_map_path.read_text(encoding='utf-8')) or {}
    if not isinstance(data, dict):
        return {}
    normalized = {}
    for key, value in data.items():
        if not key or not value:
            continue
        normalized[str(key).strip()] = str(value).strip()
    return normalized


def resolve_pdf_url(entry: dict, pdf_index: dict[str, str], pdf_map: dict[str, str] | None) -> str:
    if not pdf_index:
        return ''
    key = entry.get('key', '')
    slug = slugify_key(key)
    candidates: list[str] = []
    if pdf_map:
        mapped = pdf_map.get(key) or (pdf_map.get(slug) if slug else None)
        if mapped:
            candidates.append(mapped)
    if slug:
        candidates.append(f'{slug}.pdf')
    for candidate in candidates:
        candidate_name = Path(candidate).name
        if not candidate_name.lower().endswith('.pdf'):
            candidate_name = f'{candidate_name}.pdf'
        match = pdf_index.get(candidate_name.lower())
        if match:
            return f'static/papers/{match}'
    return ''


def parse_bibtex(bib_path: Path):
    """Parse a BibTeX file into a list of dictionaries.

    This minimal parser extracts common fields such as author, title,
    year, journal, booktitle, publisher, note and url.  It does not
    support nested braces or macros, but it suffices for typical
    bibliographies.  Entries of type 'unpublished' are returned with
    entry['type'] = 'unpublished'.

    Args:
        bib_path: Path to the .bib file.

    Returns:
        A list of dictionaries, one per BibTeX entry.
    """
    entries = []
    # Read the file content.  Remove comments beginning with %.
    raw = bib_path.read_text(encoding='utf-8')
    raw = re.sub(r'%.*$', '', raw, flags=re.MULTILINE)
    # Split entries by '@' markers.  The first split element may be empty.
    parts = re.split(r'@', raw)
    for part in parts:
        part = part.strip()
        if not part:
            continue
        # match type and remainder
        m = re.match(r'(\w+)\s*\{', part)
        if not m:
            continue
        entry_type = m.group(1).lower()
        # find the body between first '{' and last '}'
        body_start = part.find('{') + 1
        body_end = part.rfind('}')
        body = part[body_start:body_end].strip()
        # split into citation key and fields
        citation_key, _, fields_str = body.partition(',')
        fields_str = fields_str.strip()
        entry = {'type': entry_type, 'key': citation_key.strip()}
        # parse fields by splitting on ',' but ignoring commas inside braces
        field_parts = []
        buf = ''
        brace_level = 0
        for char in fields_str:
            if char == '{':
                brace_level += 1
            elif char == '}':
                brace_level -= 1
            if char == ',' and brace_level == 0:
                field_parts.append(buf)
                buf = ''
            else:
                buf += char
        if buf:
            field_parts.append(buf)
        # parse key=value pairs
        for field in field_parts:
            if '=' not in field:
                continue
            key, value = field.split('=', 1)
            key = key.strip().lower()
            value = value.strip().strip(',')
            # remove surrounding braces or quotes
            value = value.strip()
            if (value.startswith('{') and value.endswith('}')) or (value.startswith('"') and value.endswith('"')):
                value = value[1:-1]
            entry[key] = value.strip()
        entries.append(entry)
    return entries

def build_publication_list(entries, pdf_dir: Path | None = None, pdf_map: dict[str, str] | None = None):
    """Build a single, chronological list of publications."""
    pdf_index = build_pdf_index(pdf_dir)
    items = []
    for entry in entries:
        keywords = parse_keywords(entry)
        if 'edited' in keywords:
            continue
        if 'ritools' in entry.get('title', '').lower():
            continue
        is_allowed = (
            'peer_reviewed' in keywords
            or 'technical_report' in keywords
            or 'tecnical_report' in keywords
            or 'open_source' in keywords
            or 'essay' in keywords
        )
        if not is_allowed:
            continue
        etype = entry.get('type', 'misc')
        if etype == 'unpublished':
            continue  # skip unpublished here; they go into projects
        items.append(entry)

    items_sorted = sorted(
        items,
        key=lambda x: (
            -safe_year(x.get('year', '')),
            -month_number(x.get('month', '')),
            x.get('title', ''),
        ),
    )

    display_items = []
    for item in items_sorted:
        authors = format_authors(item.get('author', ''))
        title = item.get('title', '')
        date = format_date(item)
        venue = (
            item.get('journal')
            or item.get('booktitle')
            or item.get('howpublished')
            or item.get('organization')
            or item.get('institution')
            or ''
        )
        raw_url = (item.get('url') or '').strip()
        doi = item.get('doi', '').strip()
        doi_url = ''
        if doi:
            doi_url = doi if doi.startswith('http') else f'https://doi.org/{doi}'
        candidates = [
            raw_url,
            doi_url,
            item.get('bdsk-url-1') or '',
            item.get('bdsk-url-2') or '',
        ]
        url = ''
        pdf_url = ''
        for candidate in candidates:
            if not candidate:
                continue
            if is_pdf_url(candidate):
                if not pdf_url:
                    pdf_url = candidate
            elif not url:
                url = candidate
        local_pdf = resolve_pdf_url(item, pdf_index, pdf_map)
        if local_pdf:
            pdf_url = local_pdf
        if url and pdf_url and url == pdf_url:
            url = ''
        volume = item.get('volume', '')
        number = item.get('number', '')
        pages = item.get('pages', '')
        editor = item.get('editor', '')
        publisher = item.get('publisher', '')
        address = item.get('address', '')
        note = item.get('note') or item.get('annote') or ''
        etype = item.get('type', '')
        # Determine category for filtering
        keywords = parse_keywords(item)
        if 'peer_reviewed' in keywords:
            category = 'peer-reviewed'
        elif 'technical_report' in keywords or 'tecnical_report' in keywords:
            category = 'technical-report'
        elif 'essay' in keywords or 'open_source' in keywords:
            category = 'essay'
        else:
            category = 'other'
        display_items.append({
            'authors': authors,
            'title': title,
            'date': date,
            'venue': venue,
            'volume': volume,
            'number': number,
            'pages': pages,
            'editor': editor,
            'publisher': publisher,
            'address': address,
            'note': note,
            'type': etype,
            'key': item.get('key', ''),
            'url': url,
            'pdf_url': pdf_url,
            'category': category,
        })
    return display_items


def load_projects(projects_path: Path):
    """Load projects YAML and return structured lists for templates."""
    data = yaml.safe_load(projects_path.read_text(encoding='utf-8')) if projects_path.exists() else {}
    current = data.get('current', [])
    backburner = data.get('backburner', [])
    software = data.get('software', [])
    return current, backburner, software


def load_courses(courses_path: Path):
    """Load teaching YAML and return list of course dicts."""
    return yaml.safe_load(courses_path.read_text(encoding='utf-8')) if courses_path.exists() else []


def render_markdown(text: str) -> str:
    """Render a small Markdown subset (headings + links) to HTML."""
    if not text:
        return ''

    def render_markdown_links(value: str) -> str:
        return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', value)

    blocks = [block.strip() for block in text.strip().split('\n\n') if block.strip()]
    html_blocks = []
    for block in blocks:
        normalized = block.replace('\n', ' ').strip()
        normalized = render_markdown_links(normalized)
        heading_match = re.match(r'^(#{1,3})\s+(.*)$', normalized)
        if heading_match:
            level = len(heading_match.group(1))
            content = heading_match.group(2)
            html_blocks.append(f'<h{level}>{content}</h{level}>')
        else:
            html_blocks.append(f'<p>{normalized}</p>')
    return '\n'.join(html_blocks)


def load_markdown(path: Path):
    if not path.exists():
        return ''
    return render_markdown(path.read_text(encoding='utf-8').strip())


def load_bio(bio_path: Path):
    """Load biography markdown and convert to basic HTML."""
    return load_markdown(bio_path)


def generate_site():
    base_dir = Path(__file__).parent
    data_dir = base_dir / 'data'
    # load config
    config_path = data_dir / 'config.yaml'
    config = yaml.safe_load(config_path.read_text(encoding='utf-8')) if config_path.exists() else {}
    site_name = config.get('site_name', 'My Site')
    author_name = config.get('author_name', 'Author')
    goatcounter_code = config.get('goatcounter_code', '')
    # load biography
    bio_html = load_bio(data_dir / 'bio.md')
    future_politics_html = load_markdown(data_dir / 'future_politics.md')
    # load BibTeX
    bib_path = data_dir / 'vita.bib'
    entries = parse_bibtex(bib_path) if bib_path.exists() else []
    pdf_map = load_pdf_map(data_dir / 'publication_pdfs.yaml')
    pub_entries = build_publication_list(entries, pdf_dir=base_dir / 'static' / 'papers', pdf_map=pdf_map)
    # load projects and courses
    current_projects, backburner_projects, software_projects = load_projects(data_dir / 'projects.yaml')
    courses = load_courses(data_dir / 'teaching.yaml')
    # set up Jinja environment
    env = Environment(
        loader=FileSystemLoader(str(base_dir / 'templates')),
        autoescape=select_autoescape(['html', 'xml'])
    )
    # common context
    current_year = datetime.datetime.now().year
    common = {
        'site_name': site_name,
        'author_name': author_name,
        'current_year': current_year,
        'static_path': 'static',
        'goatcounter_code': goatcounter_code,
    }
    # Generate index
    index_template = env.get_template('index.html')
    index_html = index_template.render(
        **common,
        title=f'{site_name}',
        bio_html=bio_html,
    )
    (base_dir / 'index.html').write_text(index_html, encoding='utf-8')
    # Generate publications
    pub_template = env.get_template('publications.html')
    pub_html = pub_template.render(**common, title='Publications', pub_entries=pub_entries)
    (base_dir / 'publications.html').write_text(pub_html, encoding='utf-8')
    # Generate projects
    projects_template = env.get_template('projects.html')
    projects_html = projects_template.render(
        **common,
        title='Research & Software',
        current_projects=current_projects,
        backburner_projects=backburner_projects,
        software_projects=software_projects,
    )
    (base_dir / 'projects.html').write_text(projects_html, encoding='utf-8')
    # Generate teaching
    teaching_template = env.get_template('teaching.html')
    teaching_html = teaching_template.render(**common, title='Teaching', courses=courses)
    (base_dir / 'teaching.html').write_text(teaching_html, encoding='utf-8')
    # Generate Future Politics
    future_template = env.get_template('future_politics.html')
    future_html = future_template.render(
        **common,
        title='Future Politics',
        future_politics_html=future_politics_html,
    )
    (base_dir / 'future-politics.html').write_text(future_html, encoding='utf-8')
    print('Site generated successfully.')


if __name__ == '__main__':
    generate_site()
