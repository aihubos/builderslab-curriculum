"""Run after build.py: verify generated pages and the lesson's usable paths."""
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit, unquote
import json
import re
import subprocess
from zipfile import ZipFile

ROOT = Path(__file__).parent
class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(); self.ids=set(); self.links=[]; self.checks=[]; self.copies=[]; self.downloads=[]; self.headings=0
        self.feed(path.read_text())
    def handle_starttag(self, tag, pairs):
        a=dict(pairs)
        if 'id' in a:
            assert a['id'] not in self.ids, f"Duplicate id: {a['id']}"
            self.ids.add(a['id'])
        if tag=='h1':self.headings+=1
        if 'data-complete' in a:self.checks.append(a['data-complete'])
        if 'data-copy' in a:self.copies.append(a['data-copy'])
        if 'download' in a:self.downloads.append(a['href'])
        for key in ('href','src'):
            if key in a:self.links.append(a[key])

courses=json.loads((ROOT/'courses.json').read_text())
books=json.loads((ROOT/'workbooks.json').read_text())
names=['index','lesson','lessons']+[c['id'] for c in courses]+['lesson-'+b['id'] for b in books]
names+=['ready','teaching','handouts']+['slides-'+c['id'] for c in courses]
names+=['missions']+['mission-'+c['id'] for c in courses]
assert len(names)==30 and len(set(names))==30
names+=['assets/practice/web/example/index','assets/practice/app/example/index']
pages={name+'.html':Page(ROOT/(name+'.html')) for name in names}
for name,page in pages.items():
    assert page.headings==1, name
    for url in page.links:
        part=urlsplit(url)
        if part.scheme or part.netloc:continue
        target=str(PurePosixPath(name).parent/unquote(part.path)) if part.path else name
        assert (ROOT/target).is_file(), (name,url)
        if part.fragment and target in pages:assert unquote(part.fragment) in pages[target].ids,(name,url)
    text=(ROOT/name).read_text()
    for old in ('builderslab.ai-hub-os.com','open.kakao.com','20,000','최대 3명','동탄','course-homepage.jpg'):
        assert old not in text,(name,old)
for c in courses:
    media=c['media']
    assert media['kind']=='original' and not media['placeholder']
    assert (ROOT/media['poster']).is_file()
    text=(ROOT/f"{c['id']}.html").read_text()
    assert '<video' not in text and 'assets/demos/' not in text
    assert media['poster'] in text and 'BUILDERS LAB ORIGINAL' in text
lesson=pages['lesson.html']
assert lesson.checks==list('1234567')
assert all(i in lesson.ids for i in lesson.copies)
assert len(lesson.downloads)>=8
assert '수진' in (ROOT/'assets/memo-02.txt').read_text()
assert '미정이라고' in (ROOT/'assets/request-template.txt').read_text()
for old in ('setup','website','dashboard','game','report'):
    assert not (ROOT/f'{old}.html').exists(),old
subprocess.run(['node','--check',str(ROOT/'app.js')],check=True)
for book in books:
    page=pages['lesson-'+book['id']+'.html']
    assert page.checks==[str(i) for i in range(1,len(book['steps'])+1)]
    assert all(target in page.ids for target in page.copies)
    assert len(page.copies)>=len(book['steps'])+1
    for step in book['steps']:
        assert all(step[key] for key in ('do','prompt','expected','trouble','check'))
    with ZipFile(ROOT/'assets/downloads'/f"{book['id']}-practice.zip") as bundle:
        assert bundle.testzip() is None
        assert f"practice-{book['id']}/workbook.md" in bundle.namelist()
        assert f"practice-{book['id']}/prompts.txt" in bundle.namelist()
        assert not any('__pycache__' in x for x in bundle.namelist())
with ZipFile(ROOT/'assets/downloads/all-practice.zip') as bundle:
    assert len(bundle.namelist())==7 and bundle.testzip() is None
assert sum(len(b['steps']) for b in books)+7==53
subprocess.run(['node','--check',str(ROOT/'assets/practice/app/example/app.js')],check=True)
subprocess.run(['node',str(ROOT/'check-todo.cjs')],check=True)
plans=json.loads((ROOT/'teaching.json').read_text())
assert [p['id'] for p in plans]==[c['id'] for c in courses]
from xml.etree import ElementTree as ET
for p in plans:
    slug=p['id']
    assert sum(x['minutes'] for x in p['agenda'])==p['minutes']
    assert len(p['concepts'])==3 and len(p['assignment']['rubric'])==4
    assert all(len(row)==4 for row in p['assignment']['rubric'])
    lesson=pages['lesson.html' if slug=='start' else 'lesson-'+slug+'.html']
    assert {'learning-goals','assignment','mission'}<=lesson.ids
    for ext in ['slides.pptx','slides.pdf','workbook.pdf','challenge.txt','worksheet.md']:
        assert (ROOT/'assets/teaching'/f'{slug}-{ext}').stat().st_size>0
    with ZipFile(ROOT/'assets/teaching'/f'{slug}-slides.pptx') as z:
        slide_names=[n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',n)]
        notes=[n for n in z.namelist() if re.fullmatch(r'ppt/notesSlides/notesSlide\d+\.xml',n)]
        assert len(slide_names)==len(notes)==17,(slug,len(slide_names),len(notes))
        from teaching import slides_for
        c=next(c for c in courses if c['id']==slug)
        for i,slide in enumerate(slides_for(c),1):
            content=''.join(ET.fromstring(z.read(f'ppt/notesSlides/notesSlide{i}.xml')).itertext())
            assert slide['notes'] in content,(slug,i)
    with ZipFile(ROOT/'assets/downloads'/f'{slug}-practice.zip') as z:
        assert z.read(f'practice-{slug}/challenge.txt').decode().strip()==p['assignment']['input']
        assert z.read(f'practice-{slug}/classroom/{slug}-workbook.pdf')==(ROOT/'assets/teaching'/f'{slug}-workbook.pdf').read_bytes()
with ZipFile(ROOT/'assets/teaching/classroom-kit.zip') as z:
    assert z.testzip() is None
    for p in plans:
        name=f"practice/{p['id']}-practice.zip"
        assert z.read(name)==(ROOT/'assets/downloads'/Path(name).name).read_bytes()
print('PASS: 30 pages + 2 examples, 53 steps, 6 original assignments, rubric/agenda, 102 slides with notes, PDF and current ZIP bundles')

with ZipFile(ROOT/'assets/teaching/student-handouts.zip') as z:
    assert z.testzip() is None
    assert len(z.namelist())==20
    assert not any('slides' in n or 'instructor' in n or 'workbook' in n for n in z.namelist())
    for p in plans:
        md=z.read(p['id']+'-handout.md').decode()
        assert p['assignment']['answer'] not in md and '모범 답안' not in md
print('PASS: student-only handout archive excludes instructor notes and answer keys')
missions=json.loads((ROOT/'missions.json').read_text())
assert [m['id'] for m in missions]==[c['id'] for c in courses]
for m in missions:
    lesson=pages['lesson.html' if m['id']=='start' else 'lesson-'+m['id']+'.html']
    assert len(m['questions'])==6 and len({q['id'] for q in m['questions']})==6
    assert [q.get('boss',False) for q in m['questions']]==[False]*5+[True]
    for q in m['questions']:
        assert len(q['options'])==4 and len(set(q['options']))==4
        assert isinstance(q['answer'],int) and 0<=q['answer']<4
        assert q['hint'] and q['explain'] and q['anchor'] in lesson.ids
    for page in [m['id']+'.html','lesson.html' if m['id']=='start' else 'lesson-'+m['id']+'.html','handouts.html','teaching.html']:
        assert f'mission-{m["id"]}.html' in (ROOT/page).read_text()
    uri=f'https://aihubos.github.io/builderslab-curriculum/mission-{m["id"]}.html'
    for suffix in ['handout','workbook']:
        assert ('/URI ('+uri+')').encode() in (ROOT/'assets/teaching'/f'{m["id"]}-{suffix}.pdf').read_bytes()
for name in ['game','engine','monsters','data']:
    subprocess.run(['node','--check',str(ROOT/'assets/league'/f'{name}.mjs')],check=True)
subprocess.run(['node',str(ROOT/'check-missions.mjs')],check=True)
