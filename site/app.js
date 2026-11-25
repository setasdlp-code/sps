const dialog = document.querySelector('#film-dialog');
const body = document.querySelector('#dialog-body');
let opener;

function openFilm(key, { filter = 'todos', updateHistory = true } = {}) {
  if (!projectDetails[key]) return;
  opener = dialog.open ? opener : document.activeElement;
  body.innerHTML = projectDetails[key];
  configureNextProject(body, key, filter);
  body.querySelector('.project-permalink').href = projectUrl(key, filter);
  body.querySelectorAll('.next-project-link').forEach(link => {
    const nextKey = link.dataset.nextKey;
    if (projectDetails[nextKey]) link.addEventListener('click', event => {
      if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      openFilm(nextKey, { filter });
    });
  });
  if (updateHistory) {
    const depth = (history.state?.portfolio?.view === 'film' ? history.state.portfolio.depth : 0) + 1;
    history.pushState({ portfolio: { view: 'film', key, filter, depth } }, '', projectUrl(key, filter));
  }
  document.title = projectCatalogue[key].title + ' — Sebastián Pinzón Silva';
  if (!dialog.open) dialog.showModal();
  dialog.scrollTop = 0;
  document.body.style.overflow = 'hidden';
  document.querySelector('.close').focus({ preventScroll: true });
}

function dismissFilm() {
  if (dialog.open) dialog.close();
}

function closeFilm() {
  const state = history.state?.portfolio;
  if (state?.view === 'film' && state.depth > 0) history.go(-state.depth);
  else dismissFilm();
}

document.querySelectorAll('[data-film]').forEach(link => link.addEventListener('click', event => {
  if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
  event.preventDefault();
  openFilm(link.dataset.film, { filter: document.querySelector('.project-mosaic').dataset.activeFilter });
}));
document.querySelector('.close').addEventListener('click', closeFilm);
dialog.addEventListener('cancel', event => {
  event.preventDefault();
  closeFilm();
});
dialog.addEventListener('click', event => {
  if (event.target !== dialog) return;
  const r = dialog.getBoundingClientRect();
  if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) closeFilm();
});
dialog.addEventListener('close', () => {
  if (dialog.open) return;
  body.replaceChildren();
  document.body.style.overflow = '';
  if (opener?.isConnected && !opener.hidden) opener.focus({ preventScroll: true });
});
