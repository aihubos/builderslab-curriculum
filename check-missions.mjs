// One local check for learning progress, retry, resume and course isolation.
import assert from 'node:assert/strict';
import {missions} from './assets/league/data.mjs';
import {freshRecord, readRecord, answer, nextQuestion, useHint, score, completed, runComplete, bossHealth, openStore, storageKey, lessonChecks} from './assets/league/engine.mjs';

function solve(r,m){
  while(r.run.queue.length){
    const q=m.questions.find(q=>q.id===r.run.queue[0]);
    assert.equal(answer(r,m,q.id,q.answer).correct,true);
    assert.equal(answer(r,m,q.id,q.answer),null,'Repeated click must not award twice');
    nextQuestion(r);
  }
}
for(const m of missions){
  let r=freshRecord(m);
  assert.equal(bossHealth(m,r),140);
  for(const q of m.questions.slice(0,-1)){
    answer(r,m,q.id,q.answer);nextQuestion(r);
    r=readRecord(JSON.stringify(r),m);
    assert.equal(completed(r),false,'The final boss must also be solved');
  }
  assert.equal(bossHealth(m,r),40);
  solve(r,m);
  assert.equal(completed(r),true);assert.equal(runComplete(r),true);
  assert.equal(score(r),200);assert.equal(bossHealth(m,r),0);
  assert.equal(readRecord(JSON.stringify(r),m).best.xp,200);
}
const m=missions[0],q=m.questions[0],r=freshRecord(m);
assert.equal(answer(r,m,q.id,99),null);
assert.equal(answer(r,m,q.id,1.2),null);
assert.equal(answer(r,m,'wrong-id',q.answer),null);
useHint(r,q.id);answer(r,m,q.id,(q.answer+1)%4);
assert.equal(r.run.queue.at(-1),q.id);
assert.equal(r.run.mastered.length,0);assert.equal(score(r),0);
assert.equal(readRecord(JSON.stringify(r),m).run.feedback.correct,false);
nextQuestion(r);solve(r,m);assert.equal(score(r),190);
assert.equal(r.run.mistakes[q.id],1);

const memory=new Map();let writes=0;
const storage={getItem:k=>memory.get(k)??null,setItem:(k,v)=>{writes++;memory.set(k,v)},removeItem:k=>memory.delete(k)};
const store=openStore(m,storage);solve(store.record,m);store.save();
const previousBest=store.record.best.at;
store.restart();assert.equal(store.record.best.xp,200);assert.equal(store.record.best.at,previousBest);
useHint(store.record,q.id);solve(store.record,m);store.save();
assert.equal(store.record.best.xp,200,'Practice preserves best score without farming XP');
assert.equal(memory.size,1,'Other courses stay untouched');
assert.equal(lessonChecks(m,storage),0,'Game must not tick lesson checkboxes');
assert.equal(openStore(missions[1],storage).record.best,null);
const before=writes;
for(const raw of ['{oops','null','{}',JSON.stringify({...freshRecord(m),best:{xp:9999,at:'bad'}}),JSON.stringify({...freshRecord(m),run:{...freshRecord(m).run,queue:[]}})]){
  memory.set(storageKey(m.id),raw);
  const bad=openStore(m,storage);assert.ok(bad.error);bad.save();
  assert.equal(memory.get(storageKey(m.id)),raw);
}
assert.equal(writes,before,'Unreadable existing records must not be overwritten');
const blocked=openStore(m,{getItem(){throw Error('blocked')},setItem(){throw Error('blocked')},removeItem(){throw Error('blocked')}});
solve(blocked.record,m);assert.equal(blocked.save(),false);assert.ok(blocked.error);
assert.equal(completed(blocked.record),true,'Play stays possible without storage');
assert.equal(blocked.reset(),false);
const quota=openStore(m,{getItem:()=>null,setItem(){throw Error('quota')},removeItem(){}});
assert.equal(quota.save(),false);assert.ok(quota.error);
console.log('PASS: all 6 bosses, wrong-answer retry, hints, resume, double clicks, best score, course isolation and unavailable storage');
