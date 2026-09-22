"""Run after build.py: verify generated pages and the lesson's usable paths."""
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit, unquote
import json
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
assert len(names)==14 and len(set(names))==14
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
    assert all((ROOT/media[k]).is_file() for k in ('src','poster','original'))
    assert media['source'].startswith('https://')
    text=(ROOT/f"{c['id']}.html").read_text()
    assert '<video controls playsinline preload="none"' in text
    assert 'autoplay' not in text
    assert media['src'] in text and media['poster'] in text
    assert '교체용 참고 영상' in text if media['placeholder'] else '과정 예시 영상' in text
lesson=pages['lesson.html']
assert lesson.checks==list('1234567')
assert all(i in lesson.ids for i in lesson.copies)
assert len(lesson.downloads)==5
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
print('PASS: 14 learning pages + 2 examples, links, 53 steps, copies, 6 ZIP packs, progress IDs, JS and storage failure checks')
