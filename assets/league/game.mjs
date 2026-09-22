import {missions} from './data.mjs';
import {monster} from './monsters.mjs';
import {openStore, completed, runComplete, score, bossHealth, questionFor, shuffle, useHint, answer, nextQuestion, lessonChecks, recordText} from './engine.mjs';

const main=document.querySelector('[data-game-course]');
const e=value=>String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const storage={getItem:k=>localStorage.getItem(k),setItem:(k,v)=>localStorage.setItem(k,v),removeItem:k=>localStorage.removeItem(k)};
const stores=new Map(missions.map(m=>[m.id,openStore(m,storage)]));
const m=missions.find(m=>m.id===main.dataset.gameCourse);
const store=m?stores.get(m.id):null;
let mode='intro',optionId='',optionOrder=[];

function focusTitle(){
  const feedback=main.querySelector('[data-feedback-focus]');
  const target=feedback||main.querySelector('[data-focus]');
  target?.focus({preventScroll:true});
  (feedback||main).scrollIntoView({block:feedback?'nearest':'start',behavior:'instant'});
}
function status(){return store?.error?`<p class="game-warning" role="status">${e(store.error)}</p>`:'';}
function total(){return {count:[...stores.values()].filter(s=>completed(s.record)).length,xp:[...stores.values()].reduce((n,s)=>n+(s.record.best?.xp||0),0)};}
function topbar(){const t=total();return `<div class="league-topbar"><a href="missions.html" class="league-wordmark">BUILDERS<span>LEAGUE</span><small>CLASS QUEST</small></a><div class="league-player"><span>${t.count} / 6 클리어</span><b>${t.xp} XP</b></div></div>`;}
function footerNote(){return '<p class="league-note">진행과 배지는 이 브라우저에 저장돼요. 시간 제한 없이, 힌트와 함께 끝까지 도전하세요.</p>';}
function healthPanel(health=140,compact=false,hit=false){return `<aside class="boss-panel ${compact?'preview-boss':''} ${hit?'boss-hit':''}" style="--world:${m.color}" aria-label="보스 상태"><div class="boss-id"><span>WORLD ${m.number}</span><span>${health===0?'CLEARED':'BOSS'}</span></div><div class="boss-figure">${monster(m.sprite,e(m.enemy))}<div class="boss-platform"></div>${hit?'<span class="damage-pop">HIT!</span>':''}</div><div class="boss-name"><span>이번 과정의 보스</span><h2>${e(m.enemy)}</h2></div><div class="boss-hp"><div><b>남은 장벽</b><span>${health} / 140</span></div><progress max="140" value="${health}" aria-label="보스의 남은 장벽"></progress></div><p class="boss-caption">5개 기본 미션 × 20<br>마지막 보스 미션 × 40</p></aside>`;}
function rules(){return `<details class="game-rules"><summary>처음이라면 · 게임 방법 30초</summary><ol><li>카드의 상황을 읽고 가장 알맞은 행동 하나를 고르세요.</li><li>맞히면 장벽이 줄고 XP를 얻어요. 모든 미션을 해결하면 보스를 클리어합니다.</li><li>막히면 힌트를 보세요. 틀린 미션은 해설을 읽은 뒤 다시 돌아옵니다.</li><li>첫 시도 정답은 20 XP, 힌트·재도전 정답은 10 XP. 클리어 보너스는 80 XP입니다.</li><li>재연습은 최고 기록을 유지해요. 반복 플레이로 XP를 무한히 쌓지 않습니다.</li></ol></details>`;}

function lobby(){
  const t=total();
  main.innerHTML=topbar()+`<section class="league-hero"><div><p class="game-kicker"><i></i> 배운 것을, 나의 능력으로</p><h1 data-focus tabindex="-1">한 과정을 끝내고,<br><em>한 세계를 클리어.</em></h1><p>메모를 정리하는 첫 순간부터 나만의 앱까지.<br>실습에서 배운 판단으로 여섯 보스를 물리치세요.</p><div class="league-facts"><span><b>06</b> 과정별 보스</span><span><b>36</b> 상황 미션</span><span><b>∞</b> 다시 도전</span></div></div><div class="league-passport"><span class="game-kicker">MY BUILDER PASSPORT</span><div class="passport-badges">${missions.map(x=>`<span class="passport-seal ${completed(stores.get(x.id).record)?'earned':''}" title="${e(x.badge)}" aria-label="${e(x.name)} ${completed(stores.get(x.id).record)?'클리어':'미완료'}">${completed(stores.get(x.id).record)?'✦':x.number}</span>`).join('')}</div><b>${t.count===6?'여섯 세계, 모두 클리어!':`${6-t.count}개의 배지가 기다려요.`}</b><p>실습 → 게임 도전 → 나의 배지<br>배지는 게임에서 모든 미션을 해결하면 얻어요.</p></div></section><section class="world-section" aria-labelledby="world-title"><div class="world-section-head"><div><p class="game-kicker">CHOOSE YOUR NEXT QUEST</p><h2 id="world-title">방금 배운 과정으로 들어가세요.</h2></div><a href="lessons.html">실습 교재 먼저 보기 ↗</a></div><div class="world-grid">${missions.map(x=>{
    const s=stores.get(x.id),r=s.record;
    return `<a class="world-card ${completed(r)?'world-cleared':''}" href="mission-${x.id}.html" style="--world:${x.color}"><div class="world-card-top"><span>WORLD / ${x.number}</span><span class="world-state">${completed(r)?'✓ CLEAR':r.run.mastered.length?`${r.run.mastered.length}/6 진행 중`:'READY'}</span></div><div class="world-art">${monster(x.sprite,e(x.enemy))}<span class="world-orbit"></span></div><p class="world-subtitle">${e(x.name)}</p><h3>${e(x.title)}</h3><p>${e(x.enemy)} · 6개 미션</p><div class="world-card-bottom"><span>${completed(r)?e(x.badge):'최대 200 XP · 시간 제한 없음'}</span><b aria-hidden="true">↗</b></div></a>`;
  }).join('')}</div></section><div class="league-bottom"><p>틀려도 게임 오버는 없어요.<br><strong>이해하고 다시 선택하면 다음으로 나아갑니다.</strong></p><a href="https://jeremy.ai-hub-os.com/textbooks/games/builders-league/" target="_blank" rel="noopener">원작 빌더스 리그도 즐기기 ↗</a></div>${[...stores.values()].some(s=>s.error)?'<p class="game-warning">일부 기록을 읽지 못했어요. 해당 미션에서는 현재 화면에서 플레이할 수 있습니다.</p>':''}`+footerNote();
}

function intro(){
  const r=store.record,started=r.run.mastered.length||Object.keys(r.run.mistakes).length;
  const n=lessonChecks(m,storage);
  main.innerHTML=topbar()+`<a class="league-back" href="missions.html">← 전체 미션</a><section class="quest-intro"><div class="quest-intro-copy"><p class="game-kicker">CLASS ${m.number} / ${e(m.name)}</p><h1 data-focus tabindex="-1">${e(m.title)}</h1><p class="quest-brief">${e(m.brief)}</p><div class="quest-tags"><span>6개 미션</span><span>힌트 무제한</span><span>최대 200 XP</span></div><div class="quest-path"><span>01 상황 읽기</span><b>→</b><span>02 행동 선택</span><b>→</b><span>03 보스 클리어</span></div><p class="quest-check">${n===m.stepCount?'✓ 기본 실습 체크를 모두 마쳤어요. 독립 과제의 결과도 직접 확인했나요?':`교재 실습 확인 ${n}/${m.stepCount} · 게임은 먼저 연습할 수 있어요. 과정 마무리는 실습 확인까지 마친 뒤 표시됩니다.`}</p>${completed(r)?`<p class="earned-note">✦ ${e(m.badge)} 획득 · 최고 ${r.best.xp} XP</p>`:''}<div class="quest-actions"><button class="game-button" id="begin-game">${runComplete(r)?'클리어 결과 보기':started?'이어서 도전하기':'미션 시작하기'} <span>→</span></button><a class="game-link" href="${m.lesson}#assignment">독립 실습 확인하기 ↗</a></div>${status()}${rules()}</div>${healthPanel(bossHealth(m,r),true)}</section><section class="mission-checkpoints"><h2>이 여섯 관문을 해결하면 클리어</h2><ol>${m.questions.map((q,i)=>`<li class="${r.run.mastered.includes(q.id)?'solved':''}"><span>${r.run.mastered.includes(q.id)?'✓':String(i+1).padStart(2,'0')}</span><div><small>${e(q.tag)}</small><b>${e(q.title)}</b></div></li>`).join('')}</ol></section>`+footerNote();
  main.querySelector('#begin-game').onclick=()=>{mode=runComplete(r)&&!r.run.feedback?'result':'battle';render();};
}

function battle(){
  const r=store.record,feedback=r.run.feedback,q=questionFor(m,feedback?.id||r.run.queue[0]);
  if(!q){mode='result';return result();}
  if(optionId!==q.id){optionId=q.id;optionOrder=shuffle(q.options.map((_,i)=>i));}
  const done=r.run.mastered.length,retry=Boolean(r.run.mistakes[q.id]);
  main.innerHTML=topbar()+`<div class="battle-heading"><button class="game-link" id="pause-game">← 잠시 나가기</button><div><span>WORLD ${m.number} · ${e(m.name)}</span><b>${done} / 6 해결</b></div></div><div class="battle-progress" aria-label="미션 진행">${m.questions.map((x,i)=>`<span class="${r.run.mastered.includes(x.id)?'solved':x.id===q.id?'current':''}" aria-label="미션 ${i+1} ${r.run.mastered.includes(x.id)?'해결':x.id===q.id?'진행 중':'대기'}">${r.run.mastered.includes(x.id)?'✓':i+1}${x.boss?' · BOSS':''}</span>`).join('')}</div><section class="battle-stage">${healthPanel(bossHealth(m,r),false,Boolean(feedback?.correct))}<article class="question-card ${q.boss?'boss-question':''}" data-question="${q.id}"><div class="question-meta"><span>${e(q.tag)}</span><b>${feedback?.correct?'CLEAR':retry?'RETRY':'YOUR TURN'}</b></div><h1 data-focus tabindex="-1">${e(q.title)}</h1><p class="question-scene">${e(q.scene).replace(/\n/g,'<br>')}</p>${feedback?feedbackMarkup(q,feedback):`<p class="answer-label">가장 알맞은 행동 카드를 고르세요.</p><div class="answer-grid">${optionOrder.map((original,i)=>`<button class="answer-card" data-answer="${original}" aria-label="${e(q.options[original])}"><span class="answer-keycap" aria-hidden="true">${String.fromCharCode(65+i)}</span><span>${e(q.options[original])}</span></button>`).join('')}</div><details class="question-hint" id="question-hint" ${r.run.hinted.includes(q.id)?'open':''}><summary>✦ 막혔나요? 힌트 카드 열기</summary><p>${e(q.hint)}</p><small>힌트를 사용해도 배지를 얻을 수 있어요.</small></details>`}</article></section><div class="battle-bottom"><span>이번 도전 <b>${score(r)} XP</b></span><span>틀린 문제는 해설을 읽고 다시 도전해요.</span></div>${status()}`+footerNote();
  main.querySelector('#pause-game').onclick=()=>{mode='intro';render();};
  main.querySelectorAll('[data-answer]').forEach(button=>button.onclick=()=>{
    const entry=answer(r,m,q.id,Number(button.dataset.answer));
    if(entry){store.save();render();}
  });
  const hint=main.querySelector('#question-hint');
  if(hint)hint.addEventListener('toggle',()=>{if(hint.open&&useHint(r,q.id))store.save();});
  const next=main.querySelector('#next-question');
  if(next)next.onclick=()=>{nextQuestion(r);store.save();mode=runComplete(r)?'result':'battle';render();};
}

function feedbackMarkup(q,f){
  return `<div class="answer-feedback ${f.correct?'correct':'retry'}" role="status"><div class="feedback-heading"><span aria-hidden="true">${f.correct?'✦':'↻'}</span><h2 data-feedback-focus tabindex="-1">${f.correct?(q.boss?'보스 미션을 해결했어요!':'정확한 한 수!'):'이 선택은 한 번 더 확인해요.'}</h2></div>${f.correct?'':`<p class="picked-answer">내 선택: ${e(q.options[f.choice])}</p>`}<p class="correct-answer"><b>확인할 행동</b>${e(q.options[q.answer])}</p><p>${e(q.explain)}</p>${!f.correct?'<p class="retry-note">이 미션은 남은 문제 뒤에 다시 나와요. 정답의 이유를 기억해보세요.</p>':''}<a class="review-lesson" href="${m.lesson}#${q.anchor}" target="_blank" rel="noopener">이 내용, 교재에서 다시 보기 ↗</a><button class="game-button" id="next-question">${runComplete(store.record)?'클리어 결과 보기':f.correct?'다음 미션으로':'해설 읽었어요 · 계속 도전'} <span>→</span></button></div>`;
}

function downloadRecord(){
  const url=URL.createObjectURL(new Blob([recordText(m,store.record)],{type:'text/plain;charset=utf-8'}));
  const link=document.createElement('a');link.href=url;link.download=`builders-league-${m.id}-기록.txt`;link.click();
  setTimeout(()=>URL.revokeObjectURL(url),1000);
}

function result(){
  const r=store.record,n=lessonChecks(m,storage),missed=Object.keys(r.run.mistakes);
  main.innerHTML=topbar()+`<section class="quest-result" style="--world:${m.color}"><div class="victory-emblem" aria-hidden="true"><span>✦</span><small>WORLD ${m.number}</small></div><p class="game-kicker">MISSION COMPLETE</p><h1 data-focus tabindex="-1">${e(m.enemy)},<br><em>클리어!</em></h1><p class="victory-badge">${e(m.badge)} 배지를 얻었어요.</p><div class="result-stats"><div><span>미션 해결</span><b>6 <small>/ 6</small></b></div><div><span>이번 도전</span><b>${score(r)} <small>XP</small></b></div><div><span>최고 기록</span><b>${r.best?.xp||score(r)} <small>XP</small></b></div></div><p class="result-next">${n===m.stepCount?'실습 체크와 게임 클리어를 모두 마쳤어요. 독립 과제의 실제 결과를 강사에게 보여주세요.':`게임 클리어 완료! 교재 실습 확인은 ${n}/${m.stepCount}입니다. 실제 결과를 확인하고 교재 체크도 마무리하세요.`}</p><div class="quest-actions"><a class="game-button" href="${m.lesson}#mission">교재에서 과정 마무리 ↗</a><button class="game-secondary" id="download-record">클리어 기록지 받기 ↓</button></div>${status()}</section><section class="result-review"><h2>${missed.length?'다시 도전해서 내 것으로 만든 개념':'여섯 개의 판단을 모두 해냈어요.'}</h2><p>${missed.length?'틀렸던 문제를 다시 해결했어요. 아래 내용을 내 말로 설명해보세요.':'다음에는 실제 자료를 바꿔 같은 판단을 다시 해보세요.'}</p>${missed.map(id=>{const q=questionFor(m,id);return `<details><summary>${e(q.title)}</summary><p>${e(q.explain)}</p><a href="${m.lesson}#${q.anchor}">연결된 교재 보기 ↗</a></details>`;}).join('')}<div class="quest-actions"><a class="game-link" href="missions.html">전체 배지와 다른 미션 보기 →</a><button class="game-link" id="practice-again">최고 기록을 남기고 다시 연습 ↻</button></div><details class="game-reset"><summary>이 과정의 게임 기록 관리</summary><p>초기화하면 이 과정의 배지·XP·진행 기록만 지웁니다. 실습 체크와 다른 과정은 유지합니다.</p><button class="game-secondary" id="reset-game">이 과정 게임 기록 초기화</button><div class="game-reset-confirm" id="game-reset-confirm" hidden><p>이 과정의 게임 기록과 배지를 초기화할까요?</p><button class="game-secondary" id="cancel-game-reset">유지하기</button> <button class="game-secondary" id="confirm-game-reset">초기화하기</button></div></details></section>`+footerNote();
  main.querySelector('#download-record').onclick=downloadRecord;
  main.querySelector('#practice-again').onclick=()=>{store.restart();mode='battle';render();};
  main.querySelector('#reset-game').onclick=()=>{main.querySelector('#game-reset-confirm').hidden=false;main.querySelector('#cancel-game-reset').focus();};
  main.querySelector('#cancel-game-reset').onclick=()=>{main.querySelector('#game-reset-confirm').hidden=true;main.querySelector('#reset-game').focus();};
  main.querySelector('#confirm-game-reset').onclick=()=>{if(store.reset())mode='intro';render();};
}

function render(){
  if(!m)lobby();else if(mode==='battle')battle();else if(mode==='result')result();else intro();
  focusTitle();
}
render();
