"""Shared teaching content: classroom guides, learner extensions and original previews."""
import json
from zipfile import ZipFile, ZIP_DEFLATED
from html import escape as e
from pathlib import Path

ROOT = Path(__file__).parent
PLANS = {c['id']: c for c in json.loads((ROOT/'teaching.json').read_text())}
VERSION = '2026.09 · 현장 실습판'
def ul(items):
    return '<ul>'+''.join(f'<li>{e(t)}</li>' for t in items)+'</ul>'

def rubric(plan):
    return '<div class="table-scroll"><table class="rubric"><caption>항목별 0~2점 · 총 8점 / 자기 점검용</caption><thead><tr><th>확인할 것</th><th>0 · 다시 해보기</th><th>1 · 도움받아 가능</th><th>2 · 혼자 가능</th></tr></thead><tbody>'+''.join('<tr>'+''.join(f'<{tag}>{e(x)}</{tag}>' for tag,x in zip(['th','td','td','td'],row))+'</tr>' for row in plan['assignment']['rubric'])+'</tbody></table></div><p class="caption">권장 통과 기준: 6점 이상, 모든 항목 1점 이상. 미달 항목은 도움을 받은 뒤 다른 입력으로 다시 확인합니다. 체크 횟수와 실제 수행 평가는 별개입니다.</p>'

def lesson_intro(slug):
    p=PLANS[slug]
    return f'''<section class="learning-contract" id="learning-goals"><p class="eyebrow">BEFORE YOU TRY</p><h2>오늘 내 손으로 할 수 있게 될 일</h2>{ul(p['objectives'])}<p class="notice">{e(p['prep'])}</p><div class="download-row"><a class="button secondary" href="assets/teaching/{slug}-workbook.pdf" download>인쇄용 교재 PDF ↓</a><a class="text-link" href="slides-{slug}.html">수업 슬라이드 ↗</a><a class="text-link" href="#assignment">독립 과제·평가 기준 ↓</a></div><details class="concepts"><summary>실습 전에 이해할 개념 세 가지 <span>＋</span></summary>{''.join(f'<article><h3>{e(x["title"])}</h3><p>{e(x["body"])}</p><p class="concept-example">{e(x["example"])}</p><details><summary>{e(x["question"])}</summary><p>{e(x["answer"])}</p></details></article>' for x in p['concepts'])}</details></section>'''

def assignment_html(slug):
    p=PLANS[slug];a=p['assignment']
    return f'''<section class="lesson-step assignment" id="assignment"><p class="eyebrow">YOUR TURN / 독립 실습</p><h2>{e(a['title'])}</h2><p>{e(a['task'])}</p><a class="button secondary" href="assets/teaching/{slug}-challenge.txt" download>새 과제 입력 파일 받기 ↓</a><pre>{e(a['input'])}</pre><h3>완료 후 보여줄 것</h3>{ul(a['deliverables'])}<p>파일은 본인 컴퓨터에 보관하고 강사에게 직접 보여주세요. 온라인으로 자동 제출되지 않습니다.</p><h3>도움이 필요할 때 · 한 단계씩 펼치기</h3>{''.join(f'<details class="trouble"><summary>힌트 {i} 보기</summary><p>{e(t)}</p></details>' for i,t in enumerate(p['rescue'],1))}<h3>내 결과를 평가해요</h3>{rubric(p)}<details class="answer-key"><summary>먼저 직접 수행한 뒤 · 모범 확인 기준 보기</summary><p>{e(a['answer'])}</p></details><div class="expected"><b>수업 후, 내 일에 한 번 더</b><p>{e(p['transfer'])}</p></div><h3>마지막 질문</h3><p>{e(p['exit'])}</p><a class="text-link" href="assets/teaching/{slug}-worksheet.md" download>결과·피드백 기록지 받기 ↓</a></section>'''

def preview_rows(slug):
    return {
      'start':[('요약','다음 모임 준비 사항'),('할 일','소개 문구 · 민지 · 미정'),('미정','날짜와 장소는 정하지 않음')],
      'workflow':[('입력','주간 메모 + 요청 템플릿'),('정리','완료 / 다음 행동 / 미정'),('반복','새 메모로 같은 형식 유지')],
      'wiki':[('원문','S1 · 모임 규칙 보존'),('노트','핵심 내용 + 출처 S1'),('질문','참가비? 자료에 없음')],
      'hermes':[('규칙','연습 폴더 · 원문 보존'),('요청','메모 하나를 정리해줘'),('확인','저장 파일을 직접 열기')],
      'web':[('소개','배우고 만드는 다온'),('관심사','기록 / 자료 / 웹'),('버튼','작업 섹션으로 이동')],
      'app':[('입력','오늘의 할 일 한 가지'),('완료','첫 항목만 체크'),('저장','같은 주소에서 다시 열기')]
    }[slug]

def demo(c):
    slug=c['id'];p=PLANS[slug];rows=preview_rows(slug)
    inputs={'start':'민지는 소개 문구를 준비한다. 마감일은 미정. 모임 날짜와 장소는 정하지 않았다.',
    'workflow':'이번 주 한 일, 다음에 할 일, 아직 못 정한 일이 한 메모에 섞여 있어요.',
    'wiki':'모임 규칙·실습 확인·요청 예시가 각기 다른 파일에 있어요.',
    'hermes':'새 대화에서도 같은 규칙으로 모임 메모를 처리하고 싶어요.',
    'web':'소개·관심사·작업을 한 페이지에서 보여주고 싶어요.',
    'app':'할 일을 적고 완료를 표시한 다음 다시 열고 싶어요.'}
    link=f'<a class="text-link" href="assets/practice/{slug}/example/index.html" target="_blank" rel="noopener">완성 예제 직접 사용하기 ↗</a>' if slug in ('web','app') else f'<a class="text-link" href="{ "lesson.html" if slug=="start" else "lesson-"+slug+".html"}">같은 결과를 만드는 실습 ↗</a>'
    return f'''<figure class="authored-demo"><figcaption><span class="eyebrow">BUILDERS LAB ORIGINAL</span><strong>{e(p['short'])}</strong></figcaption><div class="demo-input"><small>BEFORE / 이런 자료가 있어요</small><p>{e(inputs[slug])}</p></div><details><summary>결과가 어떻게 달라질까요? <span>＋</span></summary><div class="demo-output"><small>AFTER / 교육용 결과 예시</small>{''.join(f'<p><b>{e(k)}</b><span>{e(v)}</span></p>' for k,v in rows)}</div></details><p class="demo-caption">직접 작성한 학습 예시입니다. 펼치기는 AI 실행이 아닙니다.</p>{link}</figure>'''

def slides_for(c):
    p=PLANS[c['id']];a=p['assignment']
    slides=[
      dict(label='WELCOME',title=p['promise'],lines=[c['title'],'시연 → 함께 실행 → 혼자 반복'],notes=p['agenda'][0]['script'],kind='cover'),
      dict(label='GOAL',title='오늘의 완료는 파일로 보여줍니다',lines=p['objectives'],notes='세 목표를 읽고 현재 가장 어려울 것 같은 항목을 묻습니다. 마지막에는 같은 세 항목을 파일과 실제 동작으로 확인합니다.'),
      dict(label='CHECK IN',title='시작하기 전에, 내 상태 확인',lines=[p['prep'],'준비 / 도움이 필요 / 아직 못함 중 현재 상태를 표시하세요.'],notes='로그인·설치가 막힌 수강생을 파악합니다. 비밀번호 입력은 본인이 직접 합니다. 해결되지 않으면 관찰 실습과 보충 실습을 구분합니다.'),
    ]
    for concept in p['concepts']:
        slides.append(dict(label='UNDERSTAND',title=concept['title'],lines=[concept['body'],concept['example']],notes=concept['question']+' 10초 생각할 시간을 주세요. 확인 답: '+concept['answer']))
    slides += [
      dict(label='WATCH',title='먼저 전체 흐름을 관찰해요',lines=[p['agenda'][2]['activity'],p['agenda'][2]['checkpoint'],'지금은 보고, 다음 단계에서 직접 따라 합니다.'],notes=p['agenda'][2]['script']+' 사전 준비한 실습 폴더를 열고 입력·요청·출력을 소리 내어 구분합니다.'),
      dict(label='SPOT THE ERROR',title='이 결과에서 이상한 점을 찾아요',lines=[p['pitfall']['bad'],'어느 원문 또는 동작과 맞지 않나요?'],notes='답을 바로 공개하지 말고 수강생에게 근거를 묻습니다. '+p['pitfall']['why']+' 해결: '+p['pitfall']['fix']),
      dict(label='TOGETHER',title='이제 내 컴퓨터에서 한 단계씩',lines=[p['agenda'][3]['activity'],'교재 '+p['agenda'][3]['steps']+' 단계',p['agenda'][3]['checkpoint']],notes=p['agenda'][3]['script']+' 설명 후 손을 떼고 모두가 같은 단계에 도착했는지 확인합니다. 진행자가 대신 완료하지 않습니다.'),
      dict(label='CHECKPOINT',title='잠깐 멈추고, 결과를 열어봐요',lines=[p['agenda'][3]['checkpoint'],'설명한 결과와 실제 결과를 한 줄씩 비교','막혔다면: 단계 / 행동 / 기대 / 실제'],notes='완료자는 화면을 그대로 두고 주변 학습자에게 정답 대신 확인할 위치를 말해줍니다. 개인정보가 보이는 창은 공유하지 않습니다.'),
      dict(label='BREAK',title='10분 쉬고, 막힌 곳은 함께 해결해요',lines=[p['agenda'][4]['activity'],'다음 단계: 처음 보는 자료로 독립 실행'],notes='지연 원인을 설치·파일·요청·결과로 분류합니다. 빠른 학습자에게 기능을 늘리게 하지 않고 결과 검토를 맡깁니다.'),
      dict(label='YOUR TURN',title=a['title'],lines=[a['task'],'challenge.txt를 열고, 먼저 스스로 요청을 적습니다.'],notes=p['agenda'][5]['script']+' 첫 5분은 혼자 시작하게 합니다. 도움은 힌트 1→2→3 순으로 제공합니다.'),
      dict(label='SHOW YOUR WORK',title='이 세 가지를 준비하세요',lines=a['deliverables'],notes='수강생의 실제 파일이나 동작을 봅니다. AI의 완료 답변만으로 확인하지 않습니다. 경로와 재시작 방법도 질문합니다.'),
      dict(label='FEEDBACK',title='잘된 점 하나, 다음 행동 하나',lines=[row[0] for row in a['rubric']],notes='각 항목 0·1·2점의 행동 기준은 교재 평가표를 봅니다. 권장 기준은 6점 이상이며 모든 항목 1점 이상입니다. 미달 항목을 다른 입력으로 다시 확인합니다.'),
      dict(label='ANSWER CHECK',title='표현은 달라도 이 조건은 같아야 해요',lines=[a['answer']],notes='독립 시도 후에만 보여줍니다. 문장 일치 대신 사실·동작·보존을 평가합니다. 모범 답안과 같은 말을 썼다는 이유로 통과시키지 않습니다.'),
      dict(label='NEXT DAY',title='내일, 내 일에 한 번 더',lines=[p['transfer'],p['exit']],notes='학습자가 복습할 파일과 다음 행동을 직접 말하게 합니다. 수업 기록지에 해결 못 한 항목과 보충할 단계를 남깁니다.')
    ]
    return slides

def render_teaching(root,courses,head,footer):
    out=root/'assets/teaching';out.mkdir(exist_ok=True)
    for c in courses:
        p=PLANS[c['id']];a=p['assignment'];slug=c['id']
        (out/f'{slug}-challenge.txt').write_text(a['input']+'\n')
        worksheet=f"# {c['title']} · 독립 실습 기록\n\n이름 또는 별칭: ______\n날짜: ______\n\n## 요청 설계\n상황:\n할 일:\n목적:\n제한:\n\n## 실제 결과\n입력 파일:\n결과 파일과 위치:\n검사한 행동:\n기대한 결과:\n직접 본 결과:\n미확인 항목:\n\n## 평가 (각 0~2점)\n"+'\n'.join(f"- {row[0]}: ___ / 2 · 근거: ___" for row in a['rubric'])+"\n\n합계: ___ / 8\n\n## 피드백\n잘된 점 하나:\n다음에 고칠 행동 하나:\n다시 확인한 결과:\n\n## 수업 후\n"+p['transfer']+"\n"
        (out/f'{slug}-worksheet.md').write_text(worksheet)
        slides=slides_for(c)
        html=head(c['title']+' · 강의 슬라이드')+f'<main id="main" class="wrap slide-main"><a class="breadcrumb" href="teaching.html#{slug}">← 강사 자료실 / CLASS {c["number"]}</a><h1 class="sr-only">{e(c["title"])} 강의 슬라이드</h1><div class="slide-controls"><button id="slide-prev" class="button secondary" aria-label="이전 슬라이드">← 이전</button><span id="slide-count" role="status">전체 {len(slides)}장</span><button id="slide-next" class="button primary" aria-label="다음 슬라이드">다음 →</button><button class="button secondary" data-print>전체 인쇄</button></div><p class="caption">← → 방향키로 이동 · 발표 메모는 아래에서 펼치세요 · JavaScript가 꺼져 있으면 모든 장을 표시합니다.</p>'
        for i,s in enumerate(slides,1):
            html+=f'<section class="lecture-slide {s.get("kind","")}" data-slide><div class="slide-surface"><p class="eyebrow">{s["label"]} / CLASS {c["number"]}</p><h2>{e(s["title"])}</h2>{ul(s["lines"])}<footer><span>AI BUILDERS LAB · {VERSION}</span><b>{i:02d} / {len(slides)}</b></footer></div><details class="speaker-notes"><summary>강사 발표 메모 펼치기</summary><p>{e(s["notes"])}</p></details></section>'
        html+=f'<div class="download-row"><a class="button secondary" href="assets/teaching/{slug}-slides.pptx" download>편집 가능한 PPTX ↓</a><a class="text-link" href="{ "lesson.html" if slug=="start" else "lesson-"+slug+".html"}">실습 교재로 이동 ↗</a></div></main>'+footer()
        (root/f'slides-{slug}.html').write_text(html)
    ready=head('수업 전 준비')+'''<main id="main" class="wrap readiness"><section class="section"><p class="eyebrow">BEFORE CLASS</p><h1>처음 오셔도,<br>시작할 수 있도록.</h1><p class="lead">노트북을 가져오는 날부터 첫 파일을 만드는 순간까지.<br>설치와 파일 관리가 낯설면 준비 단계부터 도움을 받으세요.</p><div class="prep-grid"><article><span>01 / 가져올 것</span><h2>내 노트북과 내 계정</h2><p>충전기·마우스·인터넷 연결, 본인 ChatGPT/Codex 이용 가능 계정을 준비합니다. 이용 가능 여부와 사용량은 계정에서 확인합니다. 수강료에 AI 구독이 포함된 것으로 가정하지 않습니다.</p></article><article><span>02 / 먼저 해볼 것</span><h2>빈 폴더 하나 열어보기</h2><p>문서에 새 연습 폴더를 만들고 샘플 텍스트를 저장합니다. 다시 열어 한글이 보이면 준비됐어요. 막히면 운영체제·막힌 단계·오류 문구를 적어 오세요.</p></article><article><span>03 / 수업에서 할 것</span><h2>보고, 해보고, 다시 하기</h2><p>강사 시연을 먼저 본 후 같이 실행합니다. 마지막에는 새 자료로 혼자 반복하고 실제 파일을 보여줍니다. 빠른 속도보다 다시 할 수 있는지가 기준입니다.</p></article></div></section><section class="readiness-check"><h2>내 출발점 확인</h2><p>체크는 이 화면에서만 유지됩니다. 새로고침하면 초기화됩니다.</p>'''
    ready+=''.join(f'<label><input type="checkbox"> {e(t)}</label>' for t in ['본인 컴퓨터에서 앱을 설치할 수 있다.','본인 계정으로 Codex를 열 수 있다.','새 폴더를 만들고 다시 찾을 수 있다.','텍스트 파일을 저장하고 다시 열 수 있다.','샘플 요청을 보내 결과 파일을 열어봤다.'])
    ready+='''<details><summary>체크하지 못한 항목이 있다면</summary><p>설치·계정이 막혔다면 수업 전 진행자에게 준비 도움을 요청하세요. 폴더·파일이 낯설다면 01 첫걸음부터 시작합니다. 다른 과정은 첫걸음의 마지막 반복 실습을 혼자 할 수 있을 때 선택하세요.</p></details></section><section class="section"><h2>과정별로 더 준비할 것</h2><dl class="prep-list"><dt>Hermes</dt><dd>공식 지원 환경과 기존 ChatGPT/Codex 구독 인증을 확인합니다. 현재 공식 macOS 설치 경로는 Apple Silicon 기준이며 Intel Mac은 지원되지 않습니다. 교재의 공식 문서에서 최신 조건을 확인하세요.</dd><dt>홈페이지</dt><dd>Chrome 또는 Edge, 공개해도 되는 소개 문장. 개인정보나 없는 경력을 넣지 않습니다.</dd><dt>작은 앱</dt><dd>홈페이지 과정의 경험과 Python 3 실행 환경. 제공된 서버를 같은 주소에서 다시 여는 방법을 확인합니다.</dd></dl><div class="download-row"><a class="button primary" href="lesson.html">첫걸음부터 시작하기 ↗</a><a class="button secondary" href="lessons.html">교재와 준비 파일 보기</a></div></section></main>'''+footer()
    (root/'ready.html').write_text(ready)
    hub=head('강사 자료실')+'''<main id="main" class="wrap teaching-hub"><section class="section"><p class="eyebrow">INSTRUCTOR STUDIO</p><h1>수업을 여는 순간부터,<br>마지막 피드백까지.</h1><p class="lead">오프라인 현장 실습용 진행안 · 편집 가능한 강의 슬라이드 · 수강생 교재 · 독립 과제와 평가표</p><p class="notice">아래 시간은 설치 준비를 마친 수강생을 기준으로 한 권장 설계입니다. 실제 모집 일정·수강료·정원을 확정한 안내가 아닙니다. 실습 계정과 기기는 수업 전에 직접 확인하세요.</p><div class="download-row"><a class="button primary" href="assets/teaching/classroom-kit.zip" download>전체 강의 자료 ZIP ↓</a><a class="button secondary" href="assets/teaching/instructor-guide.pdf" download>현장 운영안 PDF ↓</a><a class="text-link" href="handouts.html">수강생 공유용 요약 교재 ↗</a><a class="text-link" href="ready.html">수강생 준비 안내 ↗</a></div></section>'''
    hub+='''<section class="operating-guide"><h2>현장 운영 순서</h2><div class="prep-grid"><article><span>수업 전</span><h3>기기·계정·폴더 확인</h3><p>준비 안내를 전달하고 설치 도움이 필요한 사람을 파악합니다. 강사는 새 연습 폴더에서 샘플 요청을 직접 실행해봅니다. 충전·와이파이·화면 글자 크기도 확인합니다.</p></article><article><span>수업 중</span><h3>설명할 때는 보고, 실습할 때는 손으로</h3><p>한 번에 한 행동만 시연합니다. 각 단계에서 ‘완료 / 도움 필요’를 확인합니다. 도움은 말로 안내 → 위치만 보여주기 → 다시 혼자 하기 순서로 줍니다.</p></article><article><span>수업 후</span><h3>결과를 보고 다음 행동을 정하기</h3><p>결과 파일과 원문을 함께 봅니다. 평가표에 근거를 남기고 미달 항목은 다른 입력으로 재시도합니다. 수강생에게 원본 파일과 다음 복습 행동을 남깁니다.</p></article></div><details><summary>진도가 달라지거나 인터넷이 안 될 때</summary><p>빠른 학습자는 기능 추가 대신 원문 대조와 두 번째 입력 검사를 합니다. 막힌 수강생은 마지막으로 성공한 단계부터 시작합니다. 네트워크·인증 장애는 다운로드한 원문과 모범 확인 기준으로 관찰·오류 찾기를 진행하고 AI 실행은 미완료로 남겨 보충합니다. 설치를 관찰한 것만으로 개인 설치 완료라고 기록하지 않습니다.</p></details><details><summary>개설 전에 강사가 확정할 운영 정보</summary><p>강사 소개와 실제 경력, 일정·장소·정원·수강료, 기기·계정 준비 조건, 보충 시간과 질문 채널, 신청·취소 안내를 확정해 별도 모집 공지에 담습니다. 이 홈페이지는 자료 제공용이며 신청·결제·수강생 정보를 수집하지 않습니다.</p></details></section>'''
    for c in courses:
        p=PLANS[c['id']];slug=c['id'];elapsed=0;rows=[]
        for row in p['agenda']:
            end=elapsed+row['minutes']
            rows.append(f'<tr><th>{elapsed}–{end}분</th><td><b>{e(row["title"])}</b><small>교재 {e(row["steps"])}</small></td><td>{e(row["activity"])}<details><summary>강사 발문과 확인 기준</summary><p>“{e(row["script"])}”</p><p>확인: {e(row["checkpoint"])}</p></details></td></tr>')
            elapsed=end
        hub+=f'''<section class="instructor-course section" id="{slug}"><p class="eyebrow">CLASS {c['number']} / 권장 {p['minutes']}분 · 휴식 포함</p><h2>{e(c['title'])}</h2><p class="notice">{e(p['prep'])}</p><div class="download-row"><a class="button primary" href="slides-{slug}.html">발표 슬라이드 열기 ↗</a><a class="button secondary" href="assets/teaching/{slug}-slides.pptx" download>PPTX ↓</a><a class="button secondary" href="assets/teaching/{slug}-slides.pdf" download>슬라이드 PDF ↓</a><a class="button secondary" href="assets/teaching/{slug}-workbook.pdf" download>수강생 PDF ↓</a><a class="text-link" href="assets/downloads/{slug}-practice.zip" download>실습 파일 ZIP ↓</a></div><div class="table-scroll"><table class="agenda"><caption>현장 진행 순서 · 실제 학습 속도에 따라 조정</caption><thead><tr><th>경과 시간</th><th>활동</th><th>진행 내용</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div><details class="teacher-rubric"><summary>이 과정의 독립 과제·평가·도움 순서</summary><h3>{e(p['assignment']['title'])}</h3><p>{e(p['assignment']['task'])}</p>{rubric(p)}<h3>모범 확인 기준</h3><p>{e(p['assignment']['answer'])}</p><h3>세 단계 도움</h3>{ul(p['rescue'])}<h3>마무리 질문</h3><p>{e(p['exit'])}</p></details></section>'''
    (root/'teaching.html').write_text(hub+'</main>'+footer())
    handouts=head('수강생 공유용 요약 교재')+'<main id="main" class="wrap"><section class="section"><p class="eyebrow">STUDENT FIELD NOTES</p><h1 class="library-title">가볍게 들고 와서,<br>직접 해보는 세 장.</h1><p class="lead">과정마다 3쪽. 준비와 핵심 개념 → 대표 실습 → 독립 과제와 복습.<br>강사 메모와 모범 답안 없이 수강생에게 바로 공유하는 요약 교재입니다.</p><div class="download-row"><a class="button primary" href="assets/teaching/student-handouts.pdf" download>전체 요약 교재 PDF · 18쪽 ↓</a><a class="button secondary" href="assets/teaching/student-handouts.zip" download>수강생 공유 묶음 ZIP ↓</a></div><p class="notice">설치·로그인·폴더 열기가 처음이라면 각 과정의 상세 웹 교재를 함께 보세요. 요약본은 실습 중 확인과 복습을 돕는 자료입니다.</p><div class="workbook-grid">'
    for c in courses:
        slug=c['id'];lesson='lesson.html' if slug=='start' else f'lesson-{slug}.html'
        handouts+=f'<article class="workbook-card"><span class="pill">CLASS {c["number"]} · 3쪽</span><h2>{e(c["title"])}</h2><p>{e(PLANS[slug]["promise"])}</p><a class="button primary" href="assets/teaching/{slug}-handout.pdf" download>공유용 PDF ↓</a><a class="text-link" href="assets/teaching/{slug}-handout.md" download>수정 가능한 텍스트 ↓</a><a class="text-link" href="{lesson}">자세한 실습 순서 ↗</a></article>'
    (root/'handouts.html').write_text(handouts+'</div></section></main>'+footer())


def package_materials(root):
    out=root/'assets/teaching'
    if not (out/'instructor-guide.pdf').exists():return
    with ZipFile(out/'student-handouts.zip','w',ZIP_DEFLATED) as z:
        z.write(out/'student-handouts.pdf','student-handouts.pdf')
        for slug in PLANS:
            for ext in ['pdf','md']:z.write(out/f'{slug}-handout.{ext}',f'{slug}-handout.{ext}')
            z.write(out/f'{slug}-challenge.txt',f'{slug}-challenge.txt')
        z.writestr('START-HERE.txt','전체 요약은 student-handouts.pdf, 과정별 교재는 과정-handout.pdf를 여세요. 강사 메모·모범 답안은 포함하지 않습니다. 독립 과제 파일은 작업 폴더에서 challenge.txt라는 이름으로 사용합니다. 기본 샘플과 설치부터의 상세 순서: https://aihubos.github.io/builderslab-curriculum/lessons.html')
    with ZipFile(out/'classroom-kit.zip','w',ZIP_DEFLATED) as z:
        for file in sorted(out.iterdir()):
            if file.is_file() and file.name!='classroom-kit.zip':z.write(file,'classroom/'+file.name)
        for slug in PLANS:
            file=root/'assets/downloads'/f'{slug}-practice.zip'
            z.write(file,'practice/'+file.name)
        z.writestr('START-HERE.txt','수강생: 과정별 PDF와 실습 ZIP을 여세요. 강사: instructor-guide.pdf와 PPTX의 발표자 메모를 먼저 읽으세요. 압축을 푼 뒤 사용합니다. 각 과정 ZIP 루트의 challenge.txt가 독립 과제 입력입니다. AI는 본인 앱에서 실행합니다. 온라인: https://aihubos.github.io/builderslab-curriculum/teaching.html')
