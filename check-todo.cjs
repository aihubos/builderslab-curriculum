// Runnable check for corrupt/blocked storage: never overwrite existing records.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const source = fs.readFileSync(__dirname + '/assets/practice/app/example/app.js', 'utf8');
function load(raw, readThrows = false, writeThrows = false) {
  const nodes = new Map(); const handlers = {}; let writes = 0;
  function node() { return {value:'', textContent:'', disabled:false, hidden:false, children:[], className:'', focus(){}, append(...x){this.children.push(...x)}, replaceChildren(){this.children=[]}, setAttribute(){}, addEventListener(){}, querySelectorAll(){return []}}; }
  const document = {querySelector(sel){if(!nodes.has(sel))nodes.set(sel,node());return nodes.get(sel)},createElement(){return node()}};
  document.querySelector('#add-form').addEventListener = (event, fn) => {handlers[event] = fn};
  const context = vm.createContext({document, localStorage:{getItem(){if(readThrows)throw Error('blocked');return raw},setItem(){writes++;if(writeThrows)throw Error('quota')}}, crypto:{randomUUID:()=>String(Math.random())},confirm:()=>true,Set});
  vm.runInContext(source,context);
  return {nodes,context,writes:()=>writes,add(value){nodes.get('#task').value=value;handlers.submit({preventDefault(){}})}};
}
for (const bad of ['{bad','null','{}','[{"id":"a","title":"","done":false}]','[{"id":"a","title":"x","done":false},{"id":"a","title":"y","done":false}]']) {
  const app=load(bad); assert.equal(app.nodes.get('#task').disabled,true);app.add('keep original');assert.equal(app.writes(),0);
}
const normal=load(null);normal.add('   ');normal.add('x'.repeat(121));assert.equal(normal.writes(),0);
normal.add('same');normal.add('same');normal.add('<b>memo</b>');assert.equal(normal.nodes.get('#tasks').children.length,3);assert.equal(normal.writes(),3);
const readBlocked=load(null,true);readBlocked.add('unsaved');assert.equal(readBlocked.nodes.get('#tasks').children.length,1);assert.equal(readBlocked.writes(),0);
const writeBlocked=load(null,false,true);writeBlocked.add('unsaved');assert.equal(writeBlocked.nodes.get('#tasks').children.length,1);assert.match(writeBlocked.nodes.get('#status').textContent,/저장하지 못/);
console.log('PASS: todo input boundaries, duplicates, corrupt data preservation, blocked storage');
