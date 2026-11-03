"""Generate the initial Tutors panels and PDF from calendar.yaml.

Run from any directory with Python and ReportLab installed.
Reads the current simple Tutors date/week/topic/assessment schema.
No webinar times or assessment details are inferred.
"""
from pathlib import Path
from datetime import date, timedelta
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
UNIT = ROOT / 'unit-1-sem-2'
raw = (ROOT / 'calendar.yaml').read_text(encoding='utf-8')
year = int(re.search(r'^year: (\d{4})$', raw, re.M)[1])
blocks = re.split(r'^  - date: ', raw, flags=re.M)[1:]
weeks = []
for block in blocks:
    start = date.fromisoformat(block.splitlines()[0].strip())
    number = re.search(r'^    week: (\d+|~)$', block, re.M)[1]
    topic = re.search(r'^    topic: (.+)$', block, re.M)[1].strip()
    assessment = re.search(r'^    assessment: (.+)$', block, re.M)[1].strip()
    if assessment != '~':
        raise ValueError('Assessment details now exist: extend the generator before publishing.')
    weeks.append((start, int(number) if number != '~' else None, topic))
assert len(weeks) == 17
assert [n for _, n, _ in weeks if n is not None] == list(range(1, 13))
for i, (start, _, _) in enumerate(weeks):
    assert start.year == year and start.weekday() == 0
    if i:
        assert start - weeks[i-1][0] == timedelta(days=7)

def fmt(d):
    return f'{d.day} {d:%b}'

first, last = weeks[0][0], weeks[-1][0] + timedelta(days=4)
span = f'{fmt(first)} - {fmt(last)} {year}'
schedule = [f'# Semester 2 schedule {year}', '',
    f'**{span}** · 12 teaching weeks · All times use Europe/Dublin.', '',
    '**January On-Site: Friday 15 January 2027.**', '',
    'Teaching starts on Monday 18 January. Teaching week 12 ends on Friday 7 May.', '',
    '## Modules and delivery days', '',
    '| Computer Systems & Networks | Database |',
    '| --- | --- |',
    '| ![Computer Systems & Networks course icon](img/computer-systems.png) | ![Database course icon](img/database.png) |',
    '| 🔴 **Red: Monday and Wednesday** | 🔵 **Blue: Thursday** |', '',
    'The colours match the printable calendar. Module names and weekdays also identify each delivery.', '',
    '## Weekly schedule', '',
    '| Teaching week | Monday | Friday | Schedule |',
    '| --- | --- | --- | --- |']
pdf_rows = [['Teaching week', 'Monday', 'Friday', 'Schedule']]
for start, number, topic in weeks:
    label = str(number) if number is not None else '-'
    detail = 'Teaching' if topic == '~' else topic
    schedule.append(f'| {label} | {fmt(start)} {year} | {fmt(start+timedelta(days=4))} {year} | {detail} |')
    pdf_rows.append([label, fmt(start), fmt(start+timedelta(days=4)), detail])
schedule += ['', 'Week ranges above show Monday to Friday. Weekends are not listed.', '',
    '## Reading weeks and Easter', '',
    '- Reading week: 15-19 February 2027.',
    '- Easter break: 22 March-2 April 2027.',
    '- Reading week: 19-23 April 2027.', '',
    '## Assessments', '',
    'Assessment dates and submission details will be added later.', '']
webinars = '''# Webinar details

Delivery days follow the module calendar. Webinar times and joining links have not yet been confirmed.

| Detail | Current information |
| --- | --- |
| Computer Systems & Networks | Monday and Wednesday (red) |
| Database | Thursday (blue) |
| Start and finish times | To be confirmed |
| Joining links | To be confirmed |
| Time zone | Europe/Dublin (Irish local time) |
| Recordings | Availability and access links to be confirmed |
| Reading weeks, Easter and public holidays | Session arrangements to be confirmed |

Confirmed times, joining links and any exceptions will be published here.
'''
for folder, text in [('panelnote-1-schedule', '\n'.join(schedule)), ('panelnote-2-webinars', webinars)]:
    dest = UNIT / folder
    dest.mkdir(exist_ok=True)
    (dest / ('schedule.md' if 'schedule' in folder else 'webinars.md')).write_text(text, encoding='utf-8')

# Keep the course PDF in the same landscape calendar style as the workbook.
if '--web-only' not in sys.argv:
    import runpy
    runpy.run_path(str(ROOT / 'scripts' / 'generate_calendar_pdf.py'), run_name='__main__')
print('Generated web schedule and webinar details.')
