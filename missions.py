"""Course-end missions. The source data also drives the browser game and its checks."""
import json
from html import escape as e
from pathlib import Path

ROOT = Path(__file__).parent
MISSIONS = {m['id']: m for m in json.loads((ROOT/'missions.json').read_text())}

def lesson_url(slug):
    return 'lesson.html' if slug == 'start' else f'lesson-{slug}.html'

def mission_card(slug, compact=False):
    m = MISSIONS[slug]
    title = '수업의 마지막은, 보스 클리어.' if not compact else '실습을 마쳤다면, 게임으로 한 번 더.'
    return f'''<section class="mission-entry {'compact' if compact else ''}" id="mission" data-mission-course="{slug}">
    <div class="mission-entry-copy"><p class="eyebrow">BUILDERS LEAGUE / CLASS {m['number']}</p><h2>{title}</h2><h3>{e(m['title'])}</h3><p>{e(m['brief'])}</p>
    <div class="mission-meta"><span>6개 상황 미션</span><span>시간 제한 없음</span><span>힌트 · 오답 재도전</span></div>
    <p class="mission-record" data-mission-status="{slug}" role="status">아직 클리어하지 않았어요.</p>
    <div class="download-row"><a class="button primary" href="mission-{slug}.html">{m['number']} 과정 게임 도전 ↗</a><a class="text-link" href="missions.html">전체 미션 보기</a></div>
    <p class="caption">실습 결과 확인과 게임 클리어를 모두 마치면 이 과정을 마무리해요. 게임 기록은 이 브라우저에만 저장됩니다.</p></div>
    <div class="mission-seal" aria-hidden="true"><span>CLASS</span><b>{m['number']}</b><span>{e(m['badge'])}</span></div></section>'''

def completion_banner(slug):
    return f'''<div class="completion-banner" id="lesson-complete" hidden><span aria-hidden="true">✓</span><h2 data-course-finish-title>기본 실습 확인을 마쳤어요.</h2><p data-course-finish-copy>독립 과제의 실제 결과를 확인한 뒤 마지막 게임에 도전하세요.</p><a class="button primary" data-course-finish-link href="#mission">마지막 게임 도전하기 ↓</a></div>'''

def render_missions(root, head, footer):
    assets=root/'assets/league'; assets.mkdir(exist_ok=True)
    data=[]
    books={b['id']:len(b['steps']) for b in json.loads((root/'workbooks.json').read_text())}
    for slug,m in MISSIONS.items():
        data.append({**m, 'lesson':lesson_url(slug), 'stepCount':7 if slug=='start' else books[slug]})
    (assets/'data.mjs').write_text('// Generated from missions.json by build.py.\nexport const missions = '+json.dumps(data,ensure_ascii=False,indent=2)+';\n')
    for slug in ['all', *MISSIONS]:
        title='빌더스 리그 · 과정별 미션' if slug=='all' else MISSIONS[slug]['title']
        shell=head(title).replace('<body>', '<body class="league-page">').replace('</head>', '<link rel="stylesheet" href="assets/league/game.css?v=20260922-missions"><script type="module" src="assets/league/game.mjs?v=20260922-missions"></script></head>')
        links=''.join(f'<a class="button secondary" href="mission-{m["id"]}.html">{m["number"]} {e(m["name"])}</a>' for m in data)
        shell+=f'<main id="main" class="league-wrap" data-game-course="{slug}"><h1>{e(title)}</h1><p>6개 과정 · 36개 상황 미션. 실습 뒤 게임으로 배운 내용을 다시 확인해요.</p><noscript><p>게임을 실행하려면 JavaScript를 켜주세요. 실습 교재는 아래 링크로 계속 읽을 수 있습니다.</p><a href="lessons.html">실습 교재 보기</a></noscript><nav class="download-row" aria-label="과정별 게임">{links}</nav></main>'
        shell+=footer()
        (root/('missions.html' if slug=='all' else f'mission-{slug}.html')).write_text(shell)
