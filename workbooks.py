"""Render beginner workbooks and their downloadable practice packs."""
import json
from teaching import lesson_intro, assignment_html
from html import escape as e
from html.parser import HTMLParser
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED


def paragraphs(items):
    return '<ol>' + ''.join(f'<li>{e(item)}</li>' for item in items) + '</ol>'


def copybox(identifier, text, label='요청문 복사'):
    return f'<div class="copy-block"><div class="copy-head"><span>입력 예시 · 실행할 앱을 확인하세요</span><button data-copy="{identifier}">{e(label)}</button></div><pre id="{identifier}">{e(text)}</pre></div>'


def markdown(book):
    text = [f'# {book["title"]}', book['goal'], '## 먼저 확인', book['prerequisite'], '## 준비', 'ZIP 압축을 풀고 START-HERE.txt가 보이는 폴더를 작업 폴더로 엽니다. AI 작업은 본인 앱에서 실행합니다.']
    for i, step in enumerate(book['steps'], 1):
        text += [f'## {i:02d}. {step["title"]}', '### 할 일'] + [f'{n}. {line}' for n, line in enumerate(step['do'], 1)]
        if step.get('os'):
            text += ['### Windows', step['os']['windows'], '### Mac', step['os']['mac']]
        text += ['### 입력 예시', '```text', step['prompt'], '```', '### 정상 결과', step['expected'], '### 막혔을 때', step['trouble'], f'- [ ] {step["check"]}']
    if book.get('extension'):
        x=book['extension']; text += [f'## {x["title"]}'] + x['do'] + ['```text', x['prompt'], '```', x['expected']]
    text += ['## 혼자 해보기 확인']+[f'- {x}' for x in book['assessment']]
    text += ['## 진행자 메모']+[f'- {x}' for x in book['instructor']]
    text += ['## 공식 참고 · 확인일 2026-09-22']+[f'- [{label}]({url})' for label,url in book['sources']]
    return '\n\n'.join(text)+'\n'


class FirstLessonText(HTMLParser):
    """Keep the existing first lesson as the single source of its offline text."""
    def __init__(self):
        super().__init__(); self.parts=[]; self.link=''
    def handle_starttag(self,tag,attrs):
        if tag in ('h1','h2','h3'):self.parts.append('\n\n'+'#'*int(tag[1])+' ')
        elif tag in ('p','div','section','tr','summary'):self.parts.append('\n')
        elif tag=='li':self.parts.append('\n- ')
        elif tag=='br':self.parts.append('\n')
        elif tag=='pre':self.parts.append('\n```text\n')
        elif tag=='a':self.link=dict(attrs).get('href','')
    def handle_endtag(self,tag):
        if tag=='pre':self.parts.append('\n```\n')
        elif tag in ('th','td'):self.parts.append(' | ')
        elif tag=='a' and self.link.startswith('https://'):self.parts.append(' ('+self.link+')'); self.link=''
    def handle_data(self,data):self.parts.append(data)


def render_workbooks(root, courses, head, footer):
    books=json.loads((root/'workbooks.json').read_text())
    downloads=root/'assets/downloads'; downloads.mkdir(exist_ok=True)
    by_id={c['id']:c for c in courses}
    for book in books:
        slug=book['id']; c=by_id[slug]; count=len(book['steps']); pack=root/'assets/practice'/slug
        (pack/'workbook.md').write_text(markdown(book))
        prompts='\n\n'.join(f'{i:02d} {s["title"]}\n{s["prompt"]}' for i,s in enumerate(book['steps'],1))
        if book.get('extension'):prompts+='\n\n'+book['extension']['prompt']
        (pack/'prompts.txt').write_text(prompts+'\n')
        with ZipFile(downloads/f'{slug}-practice.zip','w',ZIP_DEFLATED) as z:
            for file in sorted(pack.rglob('*')):
                if file.is_file() and '__pycache__' not in file.parts:z.write(file,Path(f'practice-{slug}')/file.relative_to(pack))
            for file in sorted((root/'assets/teaching').glob(slug+'-*')):
                if file.suffix!='.pptx':z.write(file,Path(f'practice-{slug}')/'classroom'/file.name)
            z.write(root/'assets/teaching'/f'{slug}-challenge.txt',f'practice-{slug}/challenge.txt')
        toc=''.join(f'<a href="#step-{i}">{i:02d} {e(s["title"])}</a>' for i,s in enumerate(book['steps'],1))
        sections=[]
        for i,s in enumerate(book['steps'],1):
            os=''
            if s.get('os'):
                os=''.join(f'<div data-os="{key}"><h3>{label}에서</h3><p>{e(s["os"][key])}</p></div>' for key,label in [('windows','Windows'),('mac','Mac')])
            sections.append(f'<section class="lesson-step" id="step-{i}"><div class="step-title"><span>{i:02d}</span><h2>{e(s["title"])}</h2></div><h3>할 일</h3>{paragraphs(s["do"])}{os}<h3>입력 예시</h3>{copybox(f"prompt-{i}",s["prompt"])}<div class="expected"><b>정상 결과</b><p>{e(s["expected"])}</p></div><details class="trouble"><summary>막혔을 때 <span aria-hidden="true">＋</span></summary><p>{e(s["trouble"])}</p></details><label class="step-check"><input type="checkbox" data-complete="{i}">{e(s["check"])}</label></section>')
        extension=''
        if book.get('extension'):
            x=book['extension'];extension=f'<section class="lesson-step" id="extension"><p class="eyebrow">기본 실습을 마친 뒤 선택하세요</p><h2>{e(x["title"])}</h2>{paragraphs(x["do"])}{copybox("extension-prompt",x["prompt"])}<div class="expected"><b>확인할 결과</b><p>{e(x["expected"])}</p></div></section>'
        example=f'<a class="button secondary" href="{e(book["example"])}" target="_blank" rel="noopener">직접 만든 완성 예시 열기 ↗</a>' if book.get('example') else ''
        body=head(c['title']+' · 실습 교재')+f'''<main id="main" class="wrap lesson-main" data-lesson-id="{slug}"><a class="breadcrumb" href="lessons.html">← 전체 실습 교재 <span>/ {c['number']} {c['stage']}</span></a><section class="lesson-hero"><p class="eyebrow">CLASS {c['number']} / 직접 해보는 실습 교재</p><h1>{e(book['title'])}</h1><p class="lead">{e(book['goal'])}</p><p class="notice">{e(book['prerequisite'])}</p><div class="download-row"><a class="button primary" href="assets/downloads/{slug}-practice.zip" download>실습 꾸러미 ZIP 받기 ↓</a><a class="button secondary" href="assets/practice/{slug}/workbook.md" download>텍스트 교재 받기 ↓</a>{example}<button class="button secondary" data-print>인쇄 / PDF 저장</button></div><p class="caption">{count}단계 · 가상 샘플과 정답 비교 자료 포함 · AI는 본인의 앱에서 실행합니다. 완료 체크는 직접 확인한 뒤 표시하세요.</p></section>{lesson_intro(slug)}<div class="lesson-layout"><aside class="lesson-sidebar"><div class="lesson-progress"><div><strong>나의 실습 기록</strong><span id="progress-label" role="status">0 / {count} 완료</span></div><progress id="progress" max="{count}" value="0" aria-label="실습 완료 단계"></progress><p id="storage-status">이 브라우저에만 저장됩니다.</p></div><details class="lesson-toc" open><summary>실습 목차 <span>＋</span></summary><nav aria-label="실습 단계">{toc}<a href="#help">도움 요청</a><a href="#teacher">진행자 메모</a></nav></details><button class="reset-button" id="reset-progress">이 과정 완료 표시 초기화</button><div id="reset-confirm" hidden><p>이 과정의 {count}개 완료 표시만 지울까요? 파일과 다른 과정 기록은 유지됩니다.</p><button class="button small" id="cancel-reset">유지하기</button><button class="button small primary" id="confirm-reset">초기화하기</button></div></aside><div class="lesson-content"><div class="os-picker" role="group" aria-label="내 컴퓨터 선택"><div><strong>내 컴퓨터에 맞는 안내</strong><p>Windows·Mac의 폴더·설치 안내를 전환합니다.</p></div><div class="os-buttons"><button data-os-choice="windows" aria-pressed="true">Windows</button><button data-os-choice="mac" aria-pressed="false">Mac</button></div></div><p id="os-status" class="caption" role="status">Windows 기준 안내입니다.</p><noscript><p>JavaScript가 꺼져 있어 두 운영체제 안내를 함께 보여줍니다. 요청문은 직접 선택해 복사하고, 완료 기록은 종이에 남겨주세요.</p></noscript><details class="glossary"><summary>낯선 말 먼저 보기 <span>＋</span></summary><dl>{''.join(f'<dt>{e(term)}</dt><dd>{e(meaning)}</dd>' for term,meaning in book['glossary'])}</dl></details>{''.join(sections)}{extension}<section class="lesson-step"><h2>내 힘으로 할 수 있나요?</h2>{paragraphs(book['assessment'])}</section><div class="completion-banner" id="lesson-complete" hidden><span>✓</span><h2>실습 확인을 모두 마쳤어요.</h2><p>이 체크는 학습자가 남긴 기록입니다. 실제 결과 파일을 보관하고 다음에도 다시 실행해보세요.</p><a class="button primary" href="lessons.html">다른 실습 교재 보기 ↗</a></div>{assignment_html(slug)}<section class="lesson-step" id="help"><h2>막혔다면 이렇게 질문해요.</h2>{copybox('help-request',f"과정: {c['number']} {c['title']}\n운영체제와 앱 이름:\n막힌 단계:\n열어둔 폴더/파일:\n직접 한 행동:\n기대한 결과:\n실제 결과와 오류 문구:\n내가 이미 해본 해결:",'도움 양식 복사')}<p class="caption">비밀번호와 인증 코드는 가린 뒤 진행자에게 보여주세요. 이 사이트에서 메시지를 보내지는 않습니다.</p></section><details class="teacher-notes" id="teacher"><summary>진행자를 위한 수업 메모 <span>＋</span></summary>{paragraphs(book['instructor'])}</details><section class="lesson-sources"><h2>공식 참고와 교재 기준</h2><p>확인일: 2026-09-22. 샘플·기대 결과·완성 예시는 교육용으로 직접 구성했습니다. 화면 이름과 이용 조건은 버전에 따라 달라질 수 있습니다.</p>{''.join(f'<a href="{e(url)}" target="_blank" rel="noopener">{e(label)} ↗</a>' for label,url in book['sources'])}</section></div></div></main>'''+footer()
        (root/f'lesson-{slug}.html').write_text(body)
    cards=[]
    for c in courses:
        slug=c['id']; path='lesson.html' if slug=='start' else f'lesson-{slug}.html'; count=7 if slug=='start' else len(next(b for b in books if b['id']==slug)['steps'])
        cards.append(f'<article class="workbook-card"><span class="pill">CLASS {c["number"]} · {count}단계</span><h2>{e(c["title"])}</h2><p>{e(c["outcome"])}</p><a class="button primary" href="{path}">실습 교재 열기 ↗</a><a class="text-link" href="assets/teaching/{slug}-workbook.pdf" download>인쇄용 교재 PDF ↓</a><a class="text-link" href="{slug}.html">과정 소개</a></article>')
    library=head('전체 실습 교재')+f'<main id="main" class="wrap"><section class="section"><p class="eyebrow">LEARN → TRY → REPEAT</p><h1 class="library-title">함께 배우고,<br>혼자 다시 해보는 실습 교재.</h1><p class="lead">6개 과정 · 53개 기본 단계. 샘플을 내려받고, 요청을 보내고, 실제 결과를 확인하세요.</p><p class="notice">처음이라면 01부터 시작하세요. 이후 과정의 선행 경험을 확인하고 선택하면 됩니다. 실제 설치·인증은 본인 컴퓨터에서 진행합니다.</p><div class="download-row"><a class="button secondary" href="assets/downloads/all-practice.zip" download>전체 실습 꾸러미 받기 ↓</a><a class="button secondary" href="assets/downloads/instructor-guide.md" download>진행자 안내 받기 ↓</a></div><p class="caption">전체 ZIP을 푼 뒤 원하는 과정 ZIP도 압축 해제하세요. PDF·새 과제·평가 기록지가 각 과정 묶음에 포함됩니다.</p><p class="workbook-entry"><a class="button primary" href="handouts.html">수강생 공유용 요약 교재 · 과정별 3쪽 ↗</a></p><div class="workbook-grid">{"".join(cards)}</div></section></main>'+footer()
    (root/'lessons.html').write_text(library)
    teacher=['# AI 빌더스랩 실습 진행자 안내','설명 → 같이 한 번 → 직접 확인 → 다른 입력으로 혼자 반복하는 순서로 진행합니다.','설치나 파일 관리가 막힌 학생은 해당 단계에서 동행하며 미완료를 완료로 표시하지 않습니다.','01 첫걸음: 설치·폴더·첫 메모·원문 대조·두 번째 메모 반복. 이어서 아래 과정을 선택합니다.']
    for b in books:teacher += [f'## {b["title"]}', b['prerequisite']]+b['instructor']+['완료 확인:']+b['assessment']
    (downloads/'instructor-guide.md').write_text('\n\n'.join(teacher)+'\n')
    first=FirstLessonText(); first.feed((root/'lesson-content.html').read_text())
    (downloads/'start-workbook.md').write_text('\n'.join(line.rstrip() for line in ''.join(first.parts).splitlines()).rstrip()+'\n')
    with ZipFile(downloads/'start-practice.zip','w',ZIP_DEFLATED) as z:
        z.write(downloads/'start-workbook.md','practice-start/workbook.md')
        for name in ('memo-01.txt','memo-02.txt','request-template.txt'):z.write(root/'assets'/name,'practice-start/'+name)
        for file in sorted((root/'assets/teaching').glob('start-*')):
            if file.suffix!='.pptx':z.write(file,'practice-start/classroom/'+file.name)
        z.write(root/'assets/teaching/start-challenge.txt','practice-start/challenge.txt')
        z.writestr('practice-start/START-HERE.txt','01 교재: 로컬 홈페이지의 lesson.html을 여세요. 메모 두 개를 새 폴더에 복사하고 첫 결과를 만듭니다. 이 묶음에는 입력 메모와 요청 템플릿이 있습니다.')
    with ZipFile(downloads/'all-practice.zip','w',ZIP_DEFLATED) as z:
        for slug in ['start']+[b['id'] for b in books]:z.write(downloads/f'{slug}-practice.zip',f'{slug}-practice.zip')
        z.write(downloads/'instructor-guide.md','instructor-guide.md')
    return books
