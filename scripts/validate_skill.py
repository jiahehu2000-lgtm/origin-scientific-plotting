"""Validate metadata, referenced helpers and portable package structure."""
from pathlib import Path
import re
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/origin-scientific-plotting'

def main():
    source = (SKILL / 'SKILL.md').read_text(encoding='utf-8')
    match = re.match(r'^---\n(.*?)\n---\n', source, re.DOTALL)
    if not match:
        raise ValueError('Missing YAML frontmatter')
    meta = yaml.safe_load(match.group(1))
    if meta.get('name') != SKILL.name or not isinstance(meta.get('description'), str):
        raise ValueError('Invalid name/description')
    if len(meta['description']) > 1024 or any(c in meta['description'] for c in '<>'):
        raise ValueError('Invalid description length/characters')
    ui = yaml.safe_load((SKILL / 'agents/openai.yaml').read_text(encoding='utf-8'))
    if not 25 <= len(ui['interface']['short_description']) <= 64:
        raise ValueError('Invalid UI short description length')
    if '$' + SKILL.name not in ui['interface']['default_prompt']:
        raise ValueError('Default prompt must mention the skill')
    for relative in re.findall(r'\]\((references/[^)]+)\)', source):
        if not (SKILL / relative).is_file():
            raise ValueError('Missing referenced file: ' + relative)
    for relative in ['scripts/origin_plot.py', 'scripts/origin_to_ppt.py', 'scripts/plot_spec.py', 'requirements.txt']:
        if not (SKILL / relative).is_file():
            raise ValueError('Missing package resource: ' + relative)
    for path in list((SKILL / 'scripts').glob('*.py')) + [Path(__file__)]:
        compile(path.read_text(encoding='utf-8'), str(path), 'exec')
    print('Skill metadata, references and Python syntax are valid.')
    return 0

if __name__ == '__main__':
    sys.exit(main())
