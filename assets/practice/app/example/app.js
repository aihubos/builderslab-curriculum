'use strict';
const key = 'builderslab-todo-example-v1';
const list = document.querySelector('#tasks');
const input = document.querySelector('#task');
const status = document.querySelector('#status');
let tasks = [];
let pendingDelete = null;
let blocked = false;
let storageReadable = true;
function validTasks(value) {
  return Array.isArray(value) && value.every(item => item && typeof item.id === 'string' && typeof item.title === 'string' && item.title.trim().length > 0 && item.title.length <= 120 && typeof item.done === 'boolean') && new Set(value.map(item => item.id)).size === value.length;
}
let raw = null;
try { raw = localStorage.getItem(key); }
catch { storageReadable = false; status.textContent = '저장소를 읽을 수 없어 현재 화면에서만 사용할 수 있어요.'; }
if (raw !== null) {
  try {
    const saved = JSON.parse(raw);
    if (!validTasks(saved)) throw new Error('Invalid saved data');
    tasks = saved;
  } catch {
    blocked = true;
    status.textContent = '기존 저장 데이터 형식에 문제가 있어요. 덮어쓰지 않고 멈췄습니다. 진행자에게 문의하세요.';
  }
}
function save(message) {
  if (blocked) return;
  if (!storageReadable) { status.textContent = '현재 화면에서만 변경됐어요. 저장소를 읽지 못해 기존 데이터를 덮어쓰지 않았어요.'; render(); return; }
  try { localStorage.setItem(key, JSON.stringify(tasks)); status.textContent = message; }
  catch { status.textContent = '화면에는 반영했지만 저장하지 못했어요. 이 탭을 닫거나 새로고침하면 변경이 사라질 수 있어요.'; }
  render();
}
function render() {
  list.replaceChildren();
  for (const item of tasks) {
    const li = document.createElement('li');
    li.className = item.done ? 'done' : '';
    const label = document.createElement('label');
    const check = document.createElement('input');
    check.type = 'checkbox'; check.checked = item.done;
    check.addEventListener('change', () => { item.done = check.checked; save('완료 상태를 저장했어요.'); list.querySelectorAll('input')[tasks.indexOf(item)]?.focus(); });
    const text = document.createElement('span'); text.textContent = item.title;
    label.append(check, text);
    const remove = document.createElement('button');
    remove.type = 'button'; remove.className = 'delete'; remove.textContent = '삭제';
    remove.setAttribute('aria-label', `${item.title} 삭제`);
    remove.addEventListener('click', () => { pendingDelete = item.id; render(); list.querySelector('[data-cancel]')?.focus(); });
    li.append(label, remove);
    if (pendingDelete === item.id) {
      const confirmation = document.createElement('div'); confirmation.className = 'delete-confirm';
      const question = document.createElement('span'); question.textContent = '이 항목을 삭제할까요?';
      const cancel = document.createElement('button'); cancel.type = 'button'; cancel.textContent = '유지하기'; cancel.dataset.cancel = '';
      cancel.addEventListener('click', () => { pendingDelete = null; render(); input.focus(); });
      const yes = document.createElement('button'); yes.type = 'button'; yes.textContent = '삭제 확인';
      yes.addEventListener('click', () => { tasks = tasks.filter(other => other.id !== item.id); pendingDelete = null; save('선택한 할 일을 삭제했어요.'); input.focus(); });
      confirmation.append(question, cancel, yes); li.append(confirmation);
    }
    list.append(li);
  }
  document.querySelector('#remaining').textContent = `남은 할 일 ${tasks.filter(item => !item.done).length}개`;
  document.querySelector('#empty').hidden = tasks.length > 0 || blocked;
  input.disabled = blocked;
  document.querySelector('button[type=submit]').disabled = blocked;
}
document.querySelector('#add-form').addEventListener('submit', event => {
  event.preventDefault();
  if (blocked) return;
  const title = input.value.trim();
  if (!title || title.length > 120) {
    status.textContent = !title ? '할 일을 한 글자 이상 입력해주세요.' : '120자 이내로 줄여주세요.';
    input.focus(); return;
  }
  tasks.push({id:crypto.randomUUID(), title, done:false});
  input.value = ''; save('할 일을 추가하고 저장했어요.'); input.focus();
});
render();
