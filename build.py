import json, html, pathlib
root=pathlib.Path(__file__).parent
courses=json.loads((root/'courses.json').read_text())
assert len(courses)==9 and len({c['number'] for c in courses})==9
assert all(len(c['topics'])==5 and len(c['practice'])==3 for c in courses)
labels={'foundation':'기초','build':'제작','connect':'연결','advance':'실전'}
icons={'foundation':'✧','build':'⌘','connect':'⤴','advance':'↗'}
cards=[]
for c in courses:
 e=lambda k:html.escape(c[k])
 topics=''.join(f'<li><span>{i:02d}</span>{html.escape(t)}</li>' for i,t in enumerate(c['topics'],1))
 practice=''.join(f'<li>{html.escape(t)}</li>' for t in c['practice'])
 cards.append(f'''<article class="course-card {e('stage')}" data-stage="{e('stage')}"><div class="card-top"><span class="course-icon" aria-hidden="true">{icons[c['stage']]}</span><span class="level">{labels[c['stage']]} · CLASS {e('number')}</span></div><p class="origin">{e('origin')}</p><h3>{e('title')}</h3><p class="description">{e('description')}</p><p class="audience">{e('audience')}</p><div class="outcome"><span>완성할 결과물</span><strong>{e('outcome')}</strong></div><div class="course-meta"><span>{e('duration')}</span><span>{e('prerequisite')}</span></div><details><summary>수업 목차 살펴보기 <span>＋</span></summary><div class="syllabus"><h4>차시별 교육 목차</h4><p>아래 5개 주제를 제안 회차 안에서 나누어 진행합니다.</p><ol class="topics">{topics}</ol><h4>실습과 완료 기준</h4><ul>{practice}</ul><h4>수업 전 준비</h4><p>{e('prepare')}</p></div></details></article>''')
template=root/'template.html'
if not template.exists(): (root/'index.html').rename(template)
(root/'index.html').write_text(template.read_text().replace('COURSE_CARDS','\n'.join(cards)))
print('9개 분반 HTML 생성 완료')
