const filters = [...document.querySelectorAll('[data-filter]')];
const cards = [...document.querySelectorAll('[data-stage]')];
function selectStage(stage) {
  filters.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.filter === stage)));
  cards.forEach(card => { card.hidden = stage !== 'all' && card.dataset.stage !== stage; });
  document.querySelector('#result-count').textContent = `${filters.find(button => button.dataset.filter === stage).textContent.replace('9', '').trim()} · ${cards.filter(card => !card.hidden).length}개 분반`;
}
filters.forEach(button => button.addEventListener('click', () => selectStage(button.dataset.filter)));
document.querySelectorAll('[data-pick]').forEach(link => link.addEventListener('click', () => selectStage(link.dataset.pick)));
let printState;
window.addEventListener('beforeprint', () => {
  printState = cards.map(card => ({hidden: card.hidden, open: card.querySelector('details').open}));
  cards.forEach(card => { card.hidden = false; card.querySelector('details').open = true; });
});
window.addEventListener('afterprint', () => {
  if (printState) cards.forEach((card, i) => { card.hidden = printState[i].hidden; card.querySelector('details').open = printState[i].open; });
});
document.querySelector('#print').addEventListener('click', () => window.print());
