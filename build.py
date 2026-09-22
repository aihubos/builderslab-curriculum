"""Build the local learning pages and workbooks with Python's standard library."""
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).parent
E = escape
COURSES = json.loads((ROOT / 'courses.json').read_text())
assert [c['id'] for c in COURSES] == ['start', 'workflow', 'wiki', 'hermes', 'web', 'app']
assert all(len(c['chapters']) == 4 and len(c['completion']) == 3 for c in COURSES)


def head(title, active=''):
    return f'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)} · AI 빌더스랩 배움터</title><meta name="description" content="처음 쓰는 Codex부터 나만의 앱까지. 모임원과 함께 배우는 AI, 작은 자동화로 시작하세요.">
<meta name="theme-color" content="#ffffff"><link rel="icon" href="assets/builders-lab-logo.png" type="image/png"><link rel="stylesheet" href="style.css"><script src="app.js" defer></script></head>
<body><a class="skip" href="#main">본문으로 바로가기</a><header class="header"><div class="wrap nav"><a class="brand" href="index.html" aria-label="AI 빌더스랩 배움터 홈"><img class="brand-logo" src="assets/builders-lab-logo.png" alt="AI 빌더스랩 · BUILDERS LAB" width="2172" height="724"></a><nav aria-label="주요 메뉴"><a href="index.html#courses" {'aria-current="page"' if active == 'courses' else ''}>교육 과정</a><a href="lessons.html">실습 교재</a><a href="index.html#way">배우는 방법</a></nav><a class="button small primary" href="lesson.html">첫 실습 시작 <span aria-hidden="true">↗</span></a></div></header>'''


def footer():
    return '''<footer class="wrap footer"><a class="brand" href="index.html"><img class="brand-logo" src="assets/builders-lab-logo.png" alt="AI 빌더스랩 · BUILDERS LAB" width="2172" height="724"></a><p>함께 시작해서, 혼자 할 수 있을 때까지.</p><small>모임원을 위한 교육 설계 · 2026</small></footer><p class="sr-only" id="action-status" role="status" aria-live="polite"></p></body></html>'''


def preview(kind):
    # These are authored learning examples, not simulated product screenshots.
    fragments = {
        'start': '<div class="preview-file">▤ <span>result-01.txt</span><i>정리 완료 예시</i></div><h4>모임 메모, 이렇게 정리해요.</h4><div class="note-row"><b>요약</b><span>다음 모임의 준비 사항을 논의했어요.</span></div><div class="note-row"><b>할 일</b><span>소개 문구 초안 · 민지</span></div><div class="note-row"><b>미정</b><span>마감일 · 모임 날짜 · 장소</span></div>',
        'workflow': '<div class="preview-file">▤ <span>my-workflow.txt</span><i>재사용 예시</i></div><h4>반복되는 일에, 나만의 순서.</h4><div class="flow"><span>자료 읽기</span><b>→</b><span>형식 맞추기</span><b>→</b><span>결과 확인</span></div><div class="sample-line">입력만 바꿔서 다시 쓰는 요청문</div><div class="mini-tags"><span>문서 요약</span><span>비교표</span><span>보고서 초안</span></div>',
        'wiki': '<div class="preview-file">▧ <span>나의 지식 모음</span><i>연결 예시</i></div><h4>읽은 자료가 쌓이는 곳.</h4><div class="wiki-tree"><span>목차.md</span><div><span>원문 / 자료 A</span><span>노트 / 핵심 요약</span><span>출처 / 링크와 확인일</span></div></div><p class="tiny">답에서 다시 근거로 돌아갈 수 있게.</p>',
        'hermes': '<div class="preview-file">✳ <span>나의 메모 비서</span><i>대화 예시</i></div><div class="bubble user">이 메모를 같은 형식으로 정리해줘.</div><div class="bubble reply">요약 · 할 일 · 미정 사항으로 정리했어요.<br><strong>담당자가 없는 일은 미정으로 남겼어요.</strong></div><div class="mini-tags"><span>작업 하나</span><span>명확한 규칙</span><span>결과 확인</span></div>',
        'web': '<div class="preview-file">◉ <span>나의 첫 소개 페이지</span><i>디자인 예시</i></div><div class="mini-site"><span class="mini-avatar">J</span><div><small>HELLO, WORLD.</small><h4>안녕하세요.<br>배우고 만드는 사람입니다.</h4><span class="fake-button">나의 이야기 ↗</span></div></div>',
        'app': '<div class="preview-file">☑ <span>나의 할 일</span><i>완성 화면 예시</i></div><h4>오늘, 작은 일 세 가지.</h4><div class="todo-demo"><span class="done">✓</span><s>첫 실습 시작하기</s></div><div class="todo-demo"><span>○</span>메모 한 개 정리하기</div><div class="todo-demo"><span>○</span>결과 파일 다시 열기</div><p class="tiny">입력 → 완료 표시 → 같은 브라우저에 저장</p>'
    }
    return f'<div class="preview {kind}"><div class="example-window">{fragments[kind]}</div><span class="example-label">교육용 결과물 예시 · 실제 앱 화면 아님</span></div>'


def cover(c):
    titles = {'start': ('Codex', '내 첫 자동화'), 'workflow': ('WORKFLOW', '반복 업무 끝내기'), 'wiki': ('LLM Wiki', '흩어진 지식 연결하기'), 'hermes': ('Hermes', '나를 돕는 AI 비서'), 'web': ('MY WEBSITE', '생각이 홈페이지로'), 'app': ('MY FIRST APP', '작은 아이디어를 앱으로')}
    big, sub = titles[c['id']]
    label = '참고 데모 · 교체 예정' if c['media']['placeholder'] else '과정 결과물 미리보기'
    return f'<div class="course-cover cover-{c["id"]}"><div class="cover-top"><span>AI BUILDERS LAB</span><span>CLASS {c["number"]}</span></div><strong>{big}</strong><p>{sub}</p><div class="cover-screen"><div class="window-bar"><i></i><i></i><i></i><span>PROJECT PREVIEW</span></div><img src="{E(c["media"]["poster"])}" alt="{E(c["media"]["title"])} 데모 화면" loading="lazy" width="774" height="504"></div><span class="cover-label">{label}</span></div>'


def demo(c):
    m = c['media']
    label = '교체용 참고 영상' if m['placeholder'] else '과정 예시 영상'
    return f'<figure class="demo"><div class="demo-top"><span>▶ {label}</span><span>{E(m["title"])}</span></div><video controls playsinline preload="none" poster="{E(m["poster"])}" aria-label="{E(m["title"])}"><source src="{E(m["src"])}" type="video/mp4"><a href="{E(m["src"])}">영상 파일 열기</a></video><figcaption><span>{"외부 강의 데모이며, 우리 과정의 완성 결과는 아닙니다." if m['placeholder'] else E(m['title'])}</span><a href="{E(m["source"])}" target="_blank" rel="noopener">{E(m['attribution'])} ↗</a></figcaption></figure>'


def course_card(c):
    return f'<article class="course-card" data-group="{"first" if c["id"]=="start" else "next"}"><a class="preview-link" href="{c["id"]}.html" aria-label="{E(c["title"])} 상세 보기">{cover(c)}</a><div class="card-copy"><p class="card-meta"><span>{"처음이라면 여기부터" if c["id"]=="start" else "기초 다음 선택 과정"}</span><span>STEP {c["number"]}</span></p><h3><a href="{c["id"]}.html">{E(c["title"])}</a></h3><p>{E(c["description"])}</p><div class="card-result">{E(c["outcome"])}</div><div class="card-bottom"><span>4개 챕터 · 실습 교재 제공</span><a href="{c["id"]}.html">과정 보기 ↗</a></div></div></article>'


roadmap = ''.join(f'<a href="{c["id"]}.html"><span>{c["number"]}</span><strong>{c["stage"]}</strong><small>{["Codex 첫걸음","문서와 반복 업무","LLM Wiki","Hermes 비서","나의 홈페이지","작은 앱"][i]}</small></a>' for i,c in enumerate(COURSES))
main = head('AI, 이제 내 일에 써먹자') + f'''<main id="main">
<div class="announcement">모임원을 위한 AI 클래스 <span>설치부터 첫 결과물까지, 함께 시작해요 ↗</span></div>
<section class="wrap feature-hero"><div class="feature-copy"><p class="hero-kicker">처음 배우는 사람을 위한 CODEX CLASS</p><h1>AI, 이제<br>내 일에 <em>써먹자.</em></h1><p>메모 정리부터 나만의 앱까지.<br>혼자서는 막혔던 첫 시작, 여기서 같이 해요.</p><a class="button primary" href="start.html">첫 번째 과정 만나보기 <span>↗</span></a><div class="hero-foot"><span>코딩 경험 없어도</span><span>Windows · Mac</span><span>내 속도로</span></div></div><div class="feature-visual"><div class="visual-heading"><span>FROM IDEA TO REAL LIFE</span><b>내가 만드는<br><em>작은 변화.</em></b><p>AI가 정리하고,<br>나는 더 중요한 일에<br>집중할 수 있도록.</p></div><div class="hero-demo">{demo(COURSES[1])}</div></div></section>
<section class="wrap category-bar" aria-label="단계별 교육">{roadmap}</section>
<section class="wrap section catalog" id="courses"><div class="section-heading"><div><p class="eyebrow">OUR CLASSES</p><h2>오늘 배워서, 내일 써먹는 AI</h2></div><p>01 첫걸음은 함께.<br>그다음은 필요한 과정을 골라요.</p></div><div class="filter-row"><div class="filters" role="group" aria-label="교육 과정 분류"><button data-filter="all" aria-pressed="true">전체 과정 <span>6</span></button><button data-filter="first" aria-pressed="false">처음 시작해요</button><button data-filter="next" aria-pressed="false">다음으로 배워요</button></div><p id="count" role="status">6개 과정</p></div><p class="workbook-entry"><a class="text-link" href="lessons.html">6개 과정의 실습 교재와 샘플 파일 모아보기 ↗</a></p><div class="course-grid">{''.join(course_card(c) for c in COURSES)}</div></section>
<section class="showcase"><div class="wrap"><div class="section-heading"><div><p class="eyebrow">SEE WHAT’S POSSIBLE</p><h2>설명보다 먼저,<br>움직이는 결과를 만나보세요.</h2></div><p>AI 비서와 지식 정리가 궁금하다면.<br>외부 강의의 공개 데모로 살펴보세요.</p></div><div class="showcase-grid">{demo(COURSES[3])}{demo(COURSES[2])}</div></div></section>
<section class="wrap section" id="way"><div class="section-heading"><div><p class="eyebrow">처음인 사람을 위한 수업</p><h2>“저는 설치부터 막히는데요.”<br>그래서, 거기서부터 시작해요.</h2></div><p>잘하는 사람의 속도보다<br>내가 다시 해낼 수 있는 경험이 중요하니까.</p></div><div class="method-grid"><article><span>01 / 같이 시작해요</span><h3>어디를 누르는지부터</h3><p>설치와 폴더 만들기부터 안내해요. Windows와 Mac에 맞는 방법을 선택하세요.</p></article><article><span>02 / 눈으로 확인해요</span><h3>정상 결과와 나란히</h3><p>요청 예시와 기대 결과를 함께 봐요. 실제로 저장된 파일까지 확인해요.</p></article><article><span>03 / 내 것으로 만들어요</span><h3>자료만 바꿔서 한 번 더</h3><p>오류를 설명하는 법을 익히고, 다른 메모로 같은 일을 혼자 반복해요.</p></article></div></section>
<section class="wrap"><div class="start-banner"><div><p class="eyebrow">YOUR FIRST SMALL WIN</p><h2>첫 결과물은,<br>메모 한 장이면 충분해요.</h2><p>샘플 파일과 복사할 요청문이 준비되어 있어요.</p></div><a class="button primary" href="lesson.html">첫 실습 시작하기 ↗</a></div></section>
<section class="wrap section sources"><details><summary>교육 구성과 참고 자료 <span>＋</span></summary><p>첨부한 「AI스터디 4기 분반 미리보기」와 패스트캠퍼스·클래스101의 과정 소개 흐름을 참고해 모임원 수준에 맞게 설계했습니다. 일정·회차·가격은 아직 정하지 않았습니다.</p><p>참고 영상은 패스트캠퍼스 공개 소개 페이지의 데모입니다. 화면 구성 참고를 위한 교체용 자료이며 우리 교육의 성과나 수강 영상이 아닙니다. 원본 출처는 아래 링크에서 확인할 수 있습니다.</p><a href="https://fastcampus.co.kr/biz_online_codexbible" target="_blank" rel="noopener">패스트캠퍼스 Codex 과정 ↗</a> · <a href="https://fastcampus.co.kr/biz_online_hermes" target="_blank" rel="noopener">데모 원본 출처 ↗</a> · <a href="https://class101.net/ko/products/6a2ba7346d66585d419a5c8a" target="_blank" rel="noopener">클래스101 참고 과정 ↗</a></details></section></main>''' + footer()
(ROOT / 'index.html').write_text(main)

for c in COURSES:
    chapters = ''.join(f'<details {"open" if i==1 else ""}><summary><span class="chapter-number">CHAPTER {i:02d}</span><strong>{E(ch[0])}</strong><span class="plus" aria-hidden="true">＋</span></summary><ol>{"".join(f"<li>{E(t)}</li>" for t in ch[1:])}</ol></details>' for i,ch in enumerate(c['chapters'],1))
    checks = ''.join(f'<li><span aria-hidden="true">✓</span>{E(t)}</li>' for t in c['completion'])
    title = E(c['headline']).replace('\n','<br>')
    lesson_url = 'lesson.html' if c['id']=='start' else f"lesson-{c['id']}.html"
    cta = f'<a class="button primary" href="{lesson_url}">실습 교재 시작하기 ↗</a><a class="text-link centered" href="#curriculum">교육 목차 보기 ↓</a>'
    body = head(c['title'],'courses') + f'''<main id="main" class="wrap detail-main"><a class="breadcrumb" href="index.html#courses">전체 과정 <span> / {c['number']} {c['stage']}</span></a><div class="detail-layout"><div class="detail-content"><div class="detail-gallery">{cover(c)}<div class="gallery-caption"><span>배우고 나면 직접 만들 수 있도록</span><a href="#examples">참고 영상 미리보기 ↓</a></div></div><nav class="section-nav" aria-label="과정 내 이동"><a href="#about">과정 소개</a><a href="#examples">예시 영상</a><a href="#curriculum">커리큘럼</a><a href="#prepare">준비사항</a></nav><section class="detail-section introduction" id="about"><p class="eyebrow">CLASS {c['number']} · {c['stage']}</p><h2>{title}</h2><p>{E(c['description'])}</p><div class="outcome-box"><small>이 과정을 마치면</small><h3>{E(c['outcome'])}</h3><ul class="check-list">{checks}</ul></div><h3>이런 분께 권해요</h3><p>{E(c['audience'])}</p><h3>먼저 해보면 좋아요</h3><p>{E(c['prerequisite'])}</p></section><section class="detail-section" id="examples"><p class="eyebrow">PROJECT PREVIEW</p><h2>직접 움직이는 예시로 살펴보세요.</h2><p>{'아래는 외부 강의의 참고 데모예요. 우리 과정에서 만들 결과물은 아래 교육용 예시로 확인하세요.' if c['media']['placeholder'] else '영상으로 작업의 흐름을 살펴보고, 아래 결과물 예시도 확인하세요.'}</p>{demo(c)}<div class="own-result"><h3>우리가 연습할 결과물</h3>{preview(c['id'])}</div></section><section class="detail-section" id="curriculum"><p class="eyebrow">CURRICULUM</p><h2>작은 단계로 나눈 커리큘럼</h2><p class="muted">4개 챕터 · 직접 해보는 12개 학습 항목</p><div class="chapters">{chapters}</div><p class="caption">교육 설계안입니다. 개설 회차·기간은 아직 정하지 않았습니다.</p></section><section class="detail-section" id="prepare"><p class="eyebrow">BEFORE WE START</p><h2>준비부터 막힌 순간까지</h2><h3>가져올 것</h3><p>{E(c['prepare'])}</p><div class="help-box"><strong>막혔다면 이렇게 해보세요</strong><p>{E(c['trouble'])}</p></div><p class="muted">샘플·요청문·정상 결과·오류 대처가 있는 단계별 실습 교재를 제공합니다.</p><a class="text-link" href="lesson.html#help">도움 요청 예시 보기 ↗</a></section></div><aside class="course-aside"><p class="aside-brand">AI 빌더스랩 / 모임원 클래스</p><span class="pill">{'필수 기초 · 여기부터 시작해요' if c['id']=='start' else '선택 과정 · 기초 다음에 골라요'}</span><h1>{E(c['title'])}</h1><p class="aside-outcome">{E(c['outcome'])}</p><dl><div><dt>학습 단계</dt><dd>{c['number']} · {c['stage']}</dd></div><div><dt>구성</dt><dd>4개 챕터 · 12개 항목</dd></div><div><dt>제공 자료</dt><dd>과정 안내 + 실습 교재</dd></div><div><dt>학습 방식</dt><dd>실행 · 확인 · 반복</dd></div></dl>{cta}<small>일정과 운영 조건은 추후 안내합니다.</small></aside></div><section class="section next-courses"><div class="section-heading"><h2>이런 과정도 함께 살펴보세요</h2><a class="text-link" href="index.html#courses">전체 과정 ↗</a></div><div class="course-grid">{''.join(course_card(x) for x in COURSES if x['id']!=c['id'])}</div></section></main>''' + footer()
    (ROOT / f'{c["id"]}.html').write_text(body)

lesson_content = (ROOT / 'lesson-content.html').read_text()
(ROOT / 'lesson.html').write_text(head('첫 실습 · 모임 메모 정리') + lesson_content + footer())
# Remove only the five superseded generated pages; retain reference documents.
for name in ('setup.html', 'website.html', 'dashboard.html', 'game.html', 'report.html'):
    (ROOT / name).unlink(missing_ok=True)
from workbooks import render_workbooks
render_workbooks(ROOT, COURSES, head, footer)
print('완료: 메인·과정 6개·실습 6개·교재 목록 / 14개 페이지')
