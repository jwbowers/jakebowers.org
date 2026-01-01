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

def build_publication_groups(entries):
    """Group publications by category and year."""
    category_map = {
        'article': 'Journal Articles',
        'inproceedings': 'Conference Papers',
        'conference': 'Conference Papers',
        'incollection': 'Book Chapters',
        'inbook': 'Book Chapters',
        'book': 'Books',
        'techreport': 'Technical Reports',
        'phdthesis': 'Theses',
        'mastersthesis': 'Theses',
        'misc': 'Other',
    }
    groups = {}
    for entry in entries:
        etype = entry.get('type', 'misc')
        if etype == 'unpublished':
            continue  # skip unpublished here; they go into projects
        group_name = category_map.get(etype, 'Other')
        groups.setdefault(group_name, []).append(entry)

    group_list = []
    for name, items in groups.items():
        # helper to clean up the year string
        def safe_year(year_value: str) -> int:
            import re
            digits = re.sub(r'\D', '', year_value or '')
            return int(digits) if digits else 0

        # sort by year descending then by title
        items_sorted = sorted(
            items,
            key=lambda x: (-safe_year(x.get('year', '')), x.get('title', '')),
        )

        display_items = []
        for item in items_sorted:
            authors = item.get('author', '').replace(' and ', ', ')
            title = item.get('title', '')
            year = item.get('year', '')
            venue = (
                item.get('journal')
                or item.get('booktitle')
                or item.get('publisher')
                or item.get('howpublished')
                or ''
            )
            url = item.get('url')
            display_items.append({
                'authors': authors,
                'title': title,
                'year': year,
                'venue': venue,
                'url': url,
            })
        group_list.append({'name': name, 'entries': display_items})

    order = [
        'Journal Articles', 'Conference Papers', 'Book Chapters', 'Books',
        'Technical Reports', 'Theses', 'Other'
    ]
    group_list.sort(key=lambda g: order.index(g['name']) if g['name'] in order else len(order))
    return group_list

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


def load_bio(bio_path: Path):
    """Load biography markdown and convert to basic HTML."""
    if not bio_path.exists():
        return ''
    text = bio_path.read_text(encoding='utf-8').strip()
    # simple conversion: paragraphs separated by blank lines become <p>
    paragraphs = [para.strip() for para in text.split('\n\n') if para.strip()]
    html_paragraphs = ['<p>' + para.replace('\n', ' ') + '</p>' for para in paragraphs]
    return '\n'.join(html_paragraphs)


def generate_site():
    base_dir = Path(__file__).parent
    data_dir = base_dir / 'data'
    # load config
    config_path = data_dir / 'config.yaml'
    config = yaml.safe_load(config_path.read_text(encoding='utf-8')) if config_path.exists() else {}
    site_name = config.get('site_name', 'My Site')
    author_name = config.get('author_name', 'Author')
    # load biography
    bio_html = load_bio(data_dir / 'bio.md')
    # load BibTeX
    bib_path = data_dir / 'vita.bib'
    entries = parse_bibtex(bib_path) if bib_path.exists() else []
    pub_groups = build_publication_groups(entries)
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
        'static_path': '/static',
    }
    # Generate index
    index_template = env.get_template('index.html')
    index_html = index_template.render(**common, title=f'{site_name}', bio_html=bio_html)
    (base_dir / 'index.html').write_text(index_html, encoding='utf-8')
    # Generate publications
    pub_template = env.get_template('publications.html')
    pub_html = pub_template.render(**common, title='Publications', pub_groups=pub_groups)
    (base_dir / 'publications.html').write_text(pub_html, encoding='utf-8')
    # Generate projects
    projects_template = env.get_template('projects.html')
    projects_html = projects_template.render(
        **common,
        title='Research & Projects',
        current_projects=current_projects,
        backburner_projects=backburner_projects,
        software_projects=software_projects,
    )
    (base_dir / 'projects.html').write_text(projects_html, encoding='utf-8')
    # Generate teaching
    teaching_template = env.get_template('teaching.html')
    teaching_html = teaching_template.render(**common, title='Teaching', courses=courses)
    (base_dir / 'teaching.html').write_text(teaching_html, encoding='utf-8')
    print('Site generated successfully.')


if __name__ == '__main__':
    generate_site()
