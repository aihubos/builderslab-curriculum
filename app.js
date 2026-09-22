'use strict';
const $ = selector => document.querySelector(selector);
const $$ = selector => [...document.querySelectorAll(selector)];
const announce = message => { $('#action-status').textContent = message; };
let missionEngine;
let refreshLesson = () => {};
function gameRecord(slug) {
  try { return missionEngine.readRecord(localStorage.getItem(missionEngine.storageKey(slug)), missionEngine.missionFor(slug)); }
  catch { return null; }
}
function refreshMissions() {
  $$('[data-mission-status]').forEach(node => {
    const record = gameRecord(node.dataset.missionStatus);
    node.textContent = !record ? '게임 기록을 읽지 못했어요. 게임에서 상태를 확인하세요.' : record.best ? `✦ 게임 클리어 · 최고 ${record.best.xp} XP` : `${record.run.mastered.length} / 6 미션 해결 · 모두 해결하면 클리어`;
    node.classList.toggle('is-cleared', Boolean(record?.best));
  });
  refreshLesson();
}
if ($('[data-mission-status]')) {
  import('./assets/league/engine.mjs').then(module => {
    missionEngine = module;
    refreshMissions();
    window.addEventListener('pageshow', refreshMissions);
    window.addEventListener('storage', refreshMissions);
    document.addEventListener('visibilitychange', () => { if (!document.hidden) refreshMissions(); });
  }).catch(() => { $$('[data-mission-status]').forEach(node => { node.textContent = '게임 기록을 불러오지 못했어요. 게임 링크에서 다시 확인하세요.'; }); });
}

$$('[data-filter]').forEach(button => button.addEventListener('click', () => {
  $$('[data-filter]').forEach(item => item.setAttribute('aria-pressed', String(item === button)));
  $$('[data-group]').forEach(card => { card.hidden = button.dataset.filter !== 'all' && card.dataset.group !== button.dataset.filter; });
  $('#count').textContent = `${$$('[data-group]').filter(card => !card.hidden).length}개 과정`;
}));

$$('[data-copy]').forEach(button => button.addEventListener('click', async () => {
  const source = document.getElementById(button.dataset.copy);
  const original = button.textContent;
  try {
    await navigator.clipboard.writeText(source.textContent);
    button.textContent = '복사했어요 ✓';
    announce('요청문을 복사했습니다. 사용할 앱의 입력창에 붙여 넣으세요.');
  } catch {
    const range = document.createRange();
    range.selectNodeContents(source);
    const selection = window.getSelection();
    selection.removeAllRanges();
    selection.addRange(range);
    button.textContent = '선택된 글을 직접 복사하세요';
    announce('자동 복사가 제한되어 글을 선택했습니다. Windows는 Ctrl+C, Mac은 Command+C로 복사하세요.');
  }
  setTimeout(() => { button.textContent = original; }, 4000);
}));

if ($('#progress')) {
  const lessonId = document.querySelector('main').dataset.lessonId || 'start';
  const key = lessonId === 'start' ? 'builderslab-codex-lesson-v1' : `builderslab-${lessonId}-lesson-v1`;
  const checks = $$('[data-complete]');
  let selectedOS = 'windows';
  let storageAvailable = true;
  try {
    const saved = JSON.parse(localStorage.getItem(key) || '{}');
    if (saved && typeof saved === 'object') {
      selectedOS = saved.os === 'mac' ? 'mac' : 'windows';
      if (Array.isArray(saved.completed)) checks.forEach(input => { input.checked = saved.completed.includes(input.dataset.complete); });
    }
  } catch { storageAvailable = false; }
  function render() {
    const count = checks.filter(input => input.checked).length;
    $('#progress').value = count;
    $('#progress-label').textContent = `${count} / ${checks.length} 실습 확인`;
    $('#lesson-complete').hidden = count !== checks.length;
    checks.forEach(input => input.closest('.lesson-step').classList.toggle('is-complete', input.checked));
    $$('[data-os-choice]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.osChoice === selectedOS)));
    $$('[data-os]').forEach(panel => { panel.hidden = panel.dataset.os !== selectedOS; });
    $('#os-status').textContent = `${selectedOS === 'mac' ? 'Mac' : 'Windows'} 기준 안내입니다.`;
    $('#storage-status').textContent = storageAvailable ? '이 브라우저에만 저장됩니다.' : '저장할 수 없어 현재 화면에서만 유지됩니다.';
    if ($('[data-course-finish-title]')) {
      const clear = Boolean(gameRecord(lessonId)?.best);
      $('[data-course-finish-title]').textContent = clear ? '실습 확인과 게임 클리어를 모두 마쳤어요.' : '기본 실습 확인을 마쳤어요. 이제 마지막 게임!';
      $('[data-course-finish-copy]').textContent = clear ? '독립 과제의 실제 결과도 강사에게 보여주세요. 배운 내용을 다른 자료로 다시 사용해보세요.' : '독립 과제의 결과를 확인한 뒤 6개 게임 미션을 해결하면 이 과정을 마무리해요.';
      $('[data-course-finish-link]').textContent = clear ? '다른 과정 살펴보기 ↗' : '마지막 게임 도전하기 ↓';
      $('[data-course-finish-link]').href = clear ? 'lessons.html' : '#mission';
    }
  }
  function save() {
    try {
      localStorage.setItem(key, JSON.stringify({os: selectedOS, completed: checks.filter(input => input.checked).map(input => input.dataset.complete)}));
      storageAvailable = true;
    } catch { storageAvailable = false; }
    render();
  }
  checks.forEach(input => input.addEventListener('change', save));
  $$('[data-os-choice]').forEach(button => button.addEventListener('click', () => { selectedOS = button.dataset.osChoice; save(); }));
  $('#reset-progress').addEventListener('click', () => { $('#reset-confirm').hidden = false; $('#cancel-reset').focus(); });
  $('#cancel-reset').addEventListener('click', () => { $('#reset-confirm').hidden = true; $('#reset-progress').focus(); });
  $('#confirm-reset').addEventListener('click', () => {
    checks.forEach(input => { input.checked = false; });
    save();
    $('#reset-confirm').hidden = true;
    $('#reset-progress').focus();
    announce('완료 표시를 초기화했습니다.');
  });
  refreshLesson = render;
  render();
}

$$('[data-print]').forEach(button => button.addEventListener('click', () => window.print()));

// A single keyboard-operated presenter view; printed output contains every slide.
if ($('[data-slide]')) {
  const slides = $$('[data-slide]');
  let current = Math.max(0, Math.min(slides.length - 1, (Number(location.hash.replace('#slide-', '')) || 1) - 1));
  function showSlide(index) {
    current = Math.floor(Math.max(0, Math.min(slides.length - 1, index)));
    slides.forEach((slide, i) => { slide.hidden = i !== current; });
    $('#slide-count').textContent = `${current + 1} / ${slides.length}`;
    $('#slide-prev').disabled = current === 0;
    $('#slide-next').disabled = current === slides.length - 1;
    history.replaceState(null, '', `#slide-${current + 1}`);
  }
  $('#slide-prev').addEventListener('click', () => showSlide(current - 1));
  $('#slide-next').addEventListener('click', () => showSlide(current + 1));
  document.addEventListener('keydown', event => {
    if (event.altKey || event.ctrlKey || event.metaKey || /INPUT|TEXTAREA|SELECT/.test(event.target.tagName)) return;
    if (event.key === 'ArrowRight') { event.preventDefault(); showSlide(current + 1); }
    if (event.key === 'ArrowLeft') { event.preventDefault(); showSlide(current - 1); }
  });
  showSlide(current);
}
