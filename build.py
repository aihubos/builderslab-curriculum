"""Build the local learning pages and workbooks with Python's standard library."""
import json
import re
from html import escape
from pathlib import Path
from teaching import demo, PLANS, render_teaching, lesson_intro, assignment_html, package_materials
from missions import mission_card, completion_banner, render_missions

ROOT = Path(__file__).parent
E = escape
COURSES = json.loads((ROOT / 'courses.json').read_text())
assert [c['id'] for c in COURSES] == ['start', 'workflow', 'wiki', 'hermes', 'web', 'app']
assert all(len(c['chapters']) == 4 and len(c['completion']) == 3 for c in COURSES)


def head(title, active=''):
    return f'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)} · AI 빌더스랩 배움터</title><meta name="description" content="처음 쓰는 Codex부터 나만의 앱까지. 모임원과 함께 배우는 AI, 작은 자동화로 시작하세요.">
<meta name="theme-color" content="#ffffff"><link rel="icon" href="assets/builders-lab-logo.png" type="image/png"><link rel="stylesheet" href="style.css"><script src="app.js?v=20260922-missions" defer></script><link rel="stylesheet" href="classroom.css?v=20260922-missions"></head>
<body><a class="skip" href="#main">본문으로 바로가기</a><header class="header"><div class="wrap nav"><a class="brand" href="index.html" aria-label="AI 빌더스랩 배움터 홈"><img class="brand-logo" src="assets/builders-lab-logo.png" alt="AI 빌더스랩 · BUILDERS LAB" width="2172" height="724"></a><nav aria-label="주요 메뉴"><a href="index.html#courses" {'aria-current="page"' if active == 'courses' else ''}>교육 과정</a><a href="lessons.html">실습 교재</a><a href="ready.html">수업 준비</a><a href="missions.html">게임 도전</a></nav><details class="mobile-menu"><summary>메뉴</summary><nav aria-label="모바일 메뉴"><a href="index.html#courses">교육 과정</a><a href="lessons.html">실습 교재</a><a href="ready.html">수업 준비</a><a href="missions.html">게임 도전</a><a href="teaching.html">강사 자료실</a></nav></details><a class="button small primary" href="lesson.html">첫 실습 시작 <span aria-hidden="true">↗</span></a></div></header>'''


def footer():
    return '''<footer class="wrap footer"><a class="brand" href="index.html"><img class="brand-logo" src="assets/builders-lab-logo.png" alt="AI 빌더스랩 · BUILDERS LAB" width="2172" height="724"></a><p>함께 시작해서, 혼자 할 수 있을 때까지.</p><a class="text-link" href="teaching.html">강사 자료실 ↗</a><small>AI BUILDERS LAB · 2026</small></footer><p class="sr-only" id="action-status" role="status" aria-live="polite"></p></body></html>'''


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
    label = '직접 만드는 결과물 · 교육용 예시'
    return f'<div class="course-cover cover-{c["id"]}"><div class="cover-top"><span>AI BUILDERS LAB</span><span>CLASS {c["number"]}</span></div><strong>{big}</strong><p>{sub}</p><div class="cover-screen"><div class="window-bar"><i></i><i></i><i></i><span>PROJECT PREVIEW</span></div><img src="{E(c["media"]["poster"])}" alt="{E(c["media"]["title"])} 교육용 예시" loading="lazy" width="774" height="504"></div><span class="cover-label">{label}</span></div>'


def course_card(c):
    return f'<article class="course-card" data-group="{"first" if c["id"]=="start" else "next"}"><a class="preview-link" href="{c["id"]}.html" aria-label="{E(c["title"])} 상세 보기">{cover(c)}</a><div class="card-copy"><p class="card-meta"><span>{"처음이라면 여기부터" if c["id"]=="start" else "기초 다음 선택 과정"}</span><span>STEP {c["number"]}</span></p><h3><a href="{c["id"]}.html">{E(c["title"])}</a></h3><p>{E(c["description"])}</p><div class="card-result">{E(c["outcome"])}</div><div class="card-bottom"><span>실습 교재 · 새 과제 · 피드백</span><a href="{c["id"]}.html">과정 보기 ↗</a></div></div></article>'


roadmap = ''.join(f'<a href="{c["id"]}.html"><span>{c["number"]}</span><strong>{c["stage"]}</strong><small>{["Codex 첫걸음","문서와 반복 업무","LLM Wiki","Hermes 비서","나의 홈페이지","작은 앱"][i]}</small></a>' for i,c in enumerate(COURSES))
main = head('AI를 배우는 가장 확실한 방법, 직접 해보는 것') + f'''<main id="main">
<div class="announcement">OFFLINE HANDS-ON CLASS <span>설치부터 내 손으로 만든 결과물까지</span></div>
<section class="wrap feature-hero"><div class="feature-copy"><p class="hero-kicker">AI BUILDERS LAB / 처음 시작하는 사람을 위한 수업</p><h1>듣고 끝내지 않는<br>AI 수업.<br><em>내 손으로, 완성.</em></h1><p>메모 한 장의 자동화에서 나만의 앱까지.<br>옆에서 함께 시작하고, 혼자 다시 할 수 있도록.</p><a class="button primary" href="#courses">나에게 맞는 과정 찾기 <span>↗</span></a><div class="hero-foot"><span>비전공자 입문</span><span>현장 실습</span><span>실제 결과물</span></div></div><div class="feature-visual original-hero"><div class="visual-heading"><span>SMALL INPUT. REAL OUTPUT.</span><b>첫 성취는<br><em>메모 한 장에서.</em></b></div><div class="hero-demo">{demo(COURSES[0])}</div></div></section>
<section class="wrap value-strip" aria-label="제공 자료"><span><b>6</b> 단계별 과정</span><span><b>53</b> 기본 실습 단계</span><span><b>6</b> 독립 과제·평가표</span><a href="lessons.html">교재 미리 살펴보기 ↗</a></section><section class="wrap category-bar" aria-label="단계별 교육">{roadmap}</section>
<section class="wrap section catalog" id="courses"><div class="section-heading"><div><p class="eyebrow">OUR CLASSES</p><h2>오늘 배워서, 내일 써먹는 AI</h2></div><p>01 첫걸음은 함께.<br>그다음은 필요한 과정을 골라요.</p></div><div class="filter-row"><div class="filters" role="group" aria-label="교육 과정 분류"><button data-filter="all" aria-pressed="true">전체 과정 <span>6</span></button><button data-filter="first" aria-pressed="false">처음 시작해요</button><button data-filter="next" aria-pressed="false">다음으로 배워요</button></div><p id="count" role="status">6개 과정</p></div><p class="workbook-entry"><a class="text-link" href="lessons.html">6개 과정의 실습 교재와 샘플 파일 모아보기 ↗</a></p><div class="course-grid">{''.join(course_card(c) for c in COURSES)}</div></section>
<section class="showcase"><div class="wrap"><div class="section-heading"><div><p class="eyebrow">MADE BY YOU</p><h2>수업이 끝나면,<br>보여줄 것이 생깁니다.</h2></div><p>직접 작성한 교육용 예시를 살펴보세요.<br>각 과정에서 내 자료로 다시 만듭니다.</p></div><div class="showcase-grid">{demo(COURSES[4])}{demo(COURSES[5])}</div></div></section>
<section class="wrap section" id="way"><div class="section-heading"><div><p class="eyebrow">처음인 사람을 위한 수업</p><h2>“저는 설치부터 막히는데요.”<br>그래서, 거기서부터 시작해요.</h2></div><p>잘하는 사람의 속도보다<br>내가 다시 해낼 수 있는 경험이 중요하니까.</p></div><div class="method-grid"><article><span>01 / 같이 시작해요</span><h3>어디를 누르는지부터</h3><p>강사 시연을 먼저 보고 한 단계씩 따라 합니다. 설치와 파일 찾기부터 필요한 도움을 받습니다.</p></article><article><span>02 / 눈으로 확인해요</span><h3>정상 결과와 나란히</h3><p>원문과 실제 파일을 나란히 확인합니다. 막히면 세 단계 힌트로 원인을 찾습니다.</p></article><article><span>03 / 내 것으로 만들어요</span><h3>자료만 바꿔서 한 번 더</h3><p>새 자료로 혼자 반복하고 평가표로 점검합니다. 잘된 점과 다음에 고칠 행동을 남깁니다.</p></article></div></section>
<section class="wrap"><div class="mission-collection-banner"><div><p class="eyebrow">BUILDERS LEAGUE / FINAL QUEST</p><h2>배운 만큼,<br>게임에서도 강해져요.</h2><p>6개 과정 · 36개 상황 미션.<br>실습을 마치고, 나의 과정 보스를 클리어하세요.</p></div><a class="button primary" href="missions.html">과정별 게임 도전 ↗</a></div></section><section class="wrap"><div class="start-banner"><div><p class="eyebrow">YOUR FIRST SMALL WIN</p><h2>첫 결과물은,<br>메모 한 장이면 충분해요.</h2><p>샘플 파일과 복사할 요청문이 준비되어 있어요.</p></div><a class="button primary" href="lesson.html">첫 실습 시작하기 ↗</a></div></section>
<section class="wrap section faq"><div class="section-heading"><div><p class="eyebrow">BEFORE YOU JOIN</p><h2>시작하기 전에 궁금한 것들</h2></div><a class="text-link" href="ready.html">수업 준비 안내 ↗</a></div><details><summary>설치와 파일 관리부터 어려워도 가능한가요?</summary><p>01 첫걸음은 그 지점부터 시작합니다. 수업 전 설치 도움 시간과 준비 안내를 활용하고, 혼자 첫 파일을 다시 여는 것까지 연습합니다.</p></details><details><summary>어떤 순서로 배우면 되나요?</summary><p>첫걸음을 먼저 마친 뒤 업무·지식·비서·홈페이지 중 필요한 과정을 고릅니다. 작은 앱은 홈페이지 제작 경험이 필요합니다. 각 과정의 선행 조건을 확인하세요.</p></details><details><summary>수업에서 무엇을 받나요?</summary><p>단계별 웹 교재, 인쇄용 PDF, 샘플과 요청문, 새 과제와 평가표, 복습 기록지를 제공합니다. 본인 컴퓨터에서 만든 결과를 그대로 가져갑니다.</p></details><details><summary>노트북과 AI 계정이 필요한가요?</summary><p>본인 노트북과 이용 가능한 계정이 필요합니다. Hermes는 개인 컴퓨터 설치와 기존 ChatGPT/Codex 구독을 기준으로 안내합니다. 지원 기종과 이용 한도는 준비 안내에서 확인하세요.</p></details><details><summary>일정·수강료·신청은 어디서 확인하나요?</summary><p>이 페이지는 교육 과정과 교재를 소개합니다. 모집 일정·장소·수강료·정원은 운영자가 확정한 별도 모집 공지에서 안내합니다. 현재 이 사이트에서 결제나 개인정보 입력을 받지 않습니다.</p></details></section></main>''' + footer()
(ROOT / 'index.html').write_text(main)

for c in COURSES:
    chapters = ''.join(f'<details {"open" if i==1 else ""}><summary><span class="chapter-number">CHAPTER {i:02d}</span><strong>{E(ch[0])}</strong><span class="plus" aria-hidden="true">＋</span></summary><ol>{"".join(f"<li>{E(t)}</li>" for t in ch[1:])}</ol></details>' for i,ch in enumerate(c['chapters'],1))
    checks = ''.join(f'<li><span aria-hidden="true">✓</span>{E(t)}</li>' for t in c['completion'])
    title = E(c['headline']).replace('\n','<br>')
    lesson_url = 'lesson.html' if c['id']=='start' else f"lesson-{c['id']}.html"
    cta = f'<a class="button primary" href="{lesson_url}">실습 교재 시작하기 ↗</a><a class="text-link centered" href="#curriculum">교육 목차 보기 ↓</a>'
    body = head(c['title'],'courses') + f'''<main id="main" class="wrap detail-main"><a class="breadcrumb" href="index.html#courses">전체 과정 <span> / {c['number']} {c['stage']}</span></a><div class="detail-layout"><div class="detail-content"><div class="detail-gallery">{cover(c)}<div class="gallery-caption"><span>배우고 나면 직접 만들 수 있도록</span><a href="#examples">결과물 예시 보기 ↓</a></div></div><nav class="section-nav" aria-label="과정 내 이동"><a href="#about">과정 소개</a><a href="#examples">결과물</a><a href="#curriculum">커리큘럼</a><a href="#prepare">준비사항</a></nav><section class="detail-section introduction" id="about"><p class="eyebrow">CLASS {c['number']} · {c['stage']}</p><h2>{title}</h2><p>{E(c['description'])}</p><div class="outcome-box"><small>이 과정을 마치면</small><h3>{E(c['outcome'])}</h3><ul class="check-list">{checks}</ul></div><h3>이런 분께 권해요</h3><p>{E(c['audience'])}</p><h3>먼저 해보면 좋아요</h3><p>{E(c['prerequisite'])}</p></section><section class="detail-section" id="examples"><p class="eyebrow">PROJECT PREVIEW</p><h2>이런 결과를 직접 만듭니다.</h2><p>실습의 입력과 결과를 먼저 살펴보세요. 예시를 바탕으로 나만의 자료로 다시 만듭니다.</p>{demo(c)}</section><section class="detail-section" id="curriculum"><p class="eyebrow">CURRICULUM</p><h2>작은 단계로 나눈 커리큘럼</h2><p class="muted">4개 챕터 · 직접 해보는 12개 학습 항목</p><div class="chapters">{chapters}</div><p class="caption">시연 → 함께 실행 → 독립 과제 → 평가와 복습의 순서로 진행합니다. 실제 개설 일정은 별도 안내합니다.</p><div class="outcome-box"><h3>독립 과제 · {E(PLANS[c["id"]]["assignment"]["title"])}</h3><p>{E(PLANS[c["id"]]["assignment"]["task"])}</p><a class="text-link" href="{lesson_url}#assignment">과제와 평가 기준 보기 ↗</a></div></section><section class="detail-section" id="prepare"><p class="eyebrow">BEFORE WE START</p><h2>준비부터 막힌 순간까지</h2><h3>가져올 것</h3><p>{E(c['prepare'])}</p><div class="help-box"><strong>막혔다면 이렇게 해보세요</strong><p>{E(c['trouble'])}</p></div><p class="muted">샘플·요청문·정상 결과·오류 대처가 있는 단계별 실습 교재를 제공합니다.</p><a class="text-link" href="lesson.html#help">도움 요청 예시 보기 ↗</a></section></div><aside class="course-aside"><p class="aside-brand">AI 빌더스랩 / 모임원 클래스</p><span class="pill">{'필수 기초 · 여기부터 시작해요' if c['id']=='start' else '선택 과정 · 기초 다음에 골라요'}</span><h1>{E(c['title'])}</h1><p class="aside-outcome">{E(c['outcome'])}</p><dl><div><dt>학습 단계</dt><dd>{c['number']} · {c['stage']}</dd></div><div><dt>구성</dt><dd>4개 챕터 · 12개 항목</dd></div><div><dt>제공 자료</dt><dd>PDF · 샘플 · 독립 과제</dd></div><div><dt>학습 방식</dt><dd>오프라인 현장 실습</dd></div></dl>{cta}<small>일정과 운영 조건은 추후 안내합니다.</small></aside></div>{mission_card(c["id"], compact=True)}<section class="section next-courses"><div class="section-heading"><h2>이런 과정도 함께 살펴보세요</h2><a class="text-link" href="index.html#courses">전체 과정 ↗</a></div><div class="course-grid">{''.join(course_card(x) for x in COURSES if x['id']!=c['id'])}</div></section></main>''' + footer()
    (ROOT / f'{c["id"]}.html').write_text(body)

render_teaching(ROOT, COURSES, head, footer)
lesson_content = (ROOT / 'lesson-content.html').read_text()
lesson_content = lesson_content.replace('<div class="lesson-layout">', lesson_intro('start')+'<div class="lesson-layout">',1).replace('<section class="lesson-step" id="help">',assignment_html('start')+mission_card('start')+'<section class="lesson-step" id="help">')
lesson_content = lesson_content.replace('<a href="#help">막혔을 때 도움 요청</a>', '<a href="#assignment">독립 과제 확인</a><a href="#mission">마지막 게임 도전</a><a href="#help">막혔을 때 도움 요청</a>')
lesson_content = re.sub(r'<div class="completion-banner" id="lesson-complete" hidden>.*?</div>',completion_banner('start'),lesson_content)
(ROOT / 'lesson.html').write_text(head('첫 실습 · 모임 메모 정리') + lesson_content + footer())
# Remove only the five superseded generated pages; retain reference documents.
for name in ('setup.html', 'website.html', 'dashboard.html', 'game.html', 'report.html'):
    (ROOT / name).unlink(missing_ok=True)
from workbooks import render_workbooks
render_workbooks(ROOT, COURSES, head, footer)
render_missions(ROOT, head, footer)
package_materials(ROOT)
print('완료: 교육·교재 23개 + 게임 로비·과정별 미션 7개 = 30개')
