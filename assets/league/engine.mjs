import {missions} from './data.mjs';

export const missionFor = id => missions.find(m => m.id === id);
export const storageKey = id => `builderslab-course-game-v1-${id}`;
export const freshRun = m => ({queue:m.questions.map(q => q.id), mastered:[], hinted:[], mistakes:{}, feedback:null});
export const freshRecord = m => ({version:1, course:m.id, run:freshRun(m), best:null});
export const questionFor = (m,id) => m.questions.find(q => q.id === id);
export const completed = record => Boolean(record.best);
export const runComplete = record => record.run.queue.length === 0;
export const score = record => record.run.mastered.reduce((xp,id) => xp+(record.run.hinted.includes(id)||record.run.mistakes[id]?10:20),0)+(runComplete(record)?80:0);
export const bossHealth = (m,record) => m.questions.filter(q => !record.run.mastered.includes(q.id)).reduce((hp,q) => hp+(q.boss?40:20),0);

// Same Fisher–Yates shuffle used in the original Builders League.
export function shuffle(values,rng=Math.random) {
  const a=[...values];
  for(let i=a.length-1;i>0;i--){const j=Math.floor(rng()*(i+1));[a[i],a[j]]=[a[j],a[i]];}
  return a;
}

export function readRecord(raw,m) {
  if(raw===null)return freshRecord(m);
  const p=JSON.parse(raw), ids=m.questions.map(q=>q.id);
  const knownList=a=>Array.isArray(a)&&new Set(a).size===a.length&&a.every(id=>ids.includes(id));
  if(p?.version!==1||p.course!==m.id||!p.run)throw Error('다른 형식의 기록');
  const r=p.run;
  if(!knownList(r.queue)||!knownList(r.mastered)||!knownList(r.hinted)||r.queue.length+r.mastered.length!==ids.length||new Set([...r.queue,...r.mastered]).size!==ids.length)throw Error('미션 순서 확인 필요');
  if(!r.mistakes||typeof r.mistakes!=='object'||Array.isArray(r.mistakes)||Object.entries(r.mistakes).some(([id,n])=>!ids.includes(id)||!Number.isSafeInteger(n)||n<1))throw Error('오답 기록 확인 필요');
  if(r.feedback!==null){
    const f=r.feedback,q=questionFor(m,f?.id);
    if(!q||!Number.isInteger(f.choice)||f.choice<0||f.choice>=q.options.length||f.correct!==(f.choice===q.answer)||f.correct!==r.mastered.includes(f.id))throw Error('응답 기록 확인 필요');
  }
  if(p.best!==null&&(!p.best||!Number.isInteger(p.best.xp)||p.best.xp<140||p.best.xp>200||typeof p.best.at!=='string'||!Number.isFinite(Date.parse(p.best.at))))throw Error('클리어 기록 확인 필요');
  if(!r.queue.length&&!p.best)throw Error('클리어 기록 누락');
  return p;
}

export function openStore(m,storage) {
  let record=freshRecord(m),protectedRecord=false,error='';
  try{record=readRecord(storage.getItem(storageKey(m.id)),m);}
  catch{protectedRecord=true;error='저장된 기록을 읽지 못해 현재 화면에서 진행해요. 기존 기록은 덮어쓰지 않습니다.';}
  return {
    get record(){return record;},
    get error(){return error;},
    save(){
      if(protectedRecord)return false;
      try{storage.setItem(storageKey(m.id),JSON.stringify(record));error='';return true;}
      catch{error='진행 기록을 저장하지 못했어요. 이 화면에서는 계속할 수 있습니다. 마친 뒤 기록지를 내려받으세요.';return false;}
    },
    restart(){record.run=freshRun(m);this.save();},
    reset(){
      try{storage.removeItem(storageKey(m.id));record=freshRecord(m);protectedRecord=false;error='';return true;}
      catch{error='기록을 초기화하지 못했어요. 현재 기록을 유지합니다.';return false;}
    }
  };
}

export function useHint(record,id) {
  if(record.run.feedback||record.run.queue[0]!==id)return false;
  if(!record.run.hinted.includes(id))record.run.hinted.push(id);
  return true;
}

export function answer(record,m,id,choice) {
  const r=record.run,q=questionFor(m,id);
  if(r.feedback||r.queue[0]!==id||!q||!Number.isInteger(choice)||choice<0||choice>=q.options.length)return null;
  const correct=choice===q.answer;
  r.queue.shift();
  if(correct)r.mastered.push(id);
  else{r.mistakes[id]=(r.mistakes[id]||0)+1;r.queue.push(id);}
  r.feedback={id,choice,correct};
  if(!r.queue.length){
    record.best={xp:Math.max(record.best?.xp||0,score(record)),at:record.best?.at||new Date().toISOString()};
  }
  return r.feedback;
}

export function nextQuestion(record) {record.run.feedback=null;}

export function lessonChecks(m,storage) {
  const key=m.id==='start'?'builderslab-codex-lesson-v1':`builderslab-${m.id}-lesson-v1`;
  try{
    const p=JSON.parse(storage.getItem(key)||'{}');
    return Array.isArray(p?.completed)?new Set(p.completed.filter(i=>Array.from({length:m.stepCount},(_,n)=>String(n+1)).includes(i))).size:0;
  }catch{return 0;}
}

export function recordText(m,record) {
  const r=record.run;
  return [`AI BUILDERS LAB · 과정 게임 기록`,`과정: ${m.number} ${m.name}`,`미션: ${m.title}`,`이번 도전: ${r.mastered.length} / ${m.questions.length} 해결`,`이번 도전 XP: ${score(record)}`,`클리어 기록: ${completed(record)?'있음':'아직 없음'}`,`최고 XP: ${record.best?.xp||0}`,`처음 클리어한 시각: ${record.best?.at||'아직 없음'}`,`\n다시 살펴본 개념`,...Object.keys(r.mistakes).map(id=>`- ${questionFor(m,id).title}: ${questionFor(m,id).explain}`),`\n실습 교재: https://aihubos.github.io/builderslab-curriculum/${m.lesson}#mission`,`게임 기록과 실제 실습 결과를 강사에게 함께 보여주세요.`].join('\n');
}
