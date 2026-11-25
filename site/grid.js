const mosaic = document.querySelector('.project-mosaic');
const filterLinks = [...document.querySelectorAll('header nav [data-filter]')];
const tiles = [...mosaic.querySelectorAll('.project-tile')];
const counter = document.querySelector('.grid-count');
const validFilters = new Set(filterLinks.map(link => link.dataset.filter));
const filterPaths = { todos: '/', direccion: '/?tipo=direccion', fotografia: '/fotografia/', camara: '/camara/', iluminacion: '/iluminacion/', edicion: '/edicion/', asesoria: '/asesoria-creativa/' };

function filterProjects(filter, updateUrl = false) {
  if (!validFilters.has(filter)) filter = 'todos';
  const ordered = [...tiles].sort((a, b) => Number(a.getAttribute('data-rank-' + filter)) - Number(b.getAttribute('data-rank-' + filter)));
  let count = 0;
  ordered.forEach(tile => {
    const visible = filter === 'todos' || tile.dataset.categories.split(' ').includes(filter);
    tile.hidden = !visible;
    tile.href = projectUrl(tile.dataset.key, filter);
    if (visible) count++;
    mosaic.append(tile);
  });
  ordered.filter(tile => !tile.hidden).forEach((tile, index) => {
    const fullMobile = index === 0 || (count === 2 && index === 1) || (count === 4 && index === 3) || (count === 6 && index === 5);
    const desktop = (count === 4 && index === 3) ? '1200px' : index === 0 ? '720px' : '600px';
    tile.querySelector('img').sizes = '(max-width:620px) ' + (fullMobile ? 'calc(100vw - 40px)' : 'calc((100vw - 44px) / 2)') + ', (max-width:900px) 60vw, ' + desktop;
  });
  mosaic.dataset.visibleCount = count;
  mosaic.dataset.activeFilter = filter;
  filterLinks.forEach(link => {
    if (link.dataset.filter === filter) link.setAttribute('aria-current', 'page');
    else link.removeAttribute('aria-current');
  });
  document.title = (filter === 'todos' ? 'Portafolio' : filterLinks.find(link => link.dataset.filter === filter).textContent) + ' — Sebastián Pinzón Silva';
  counter.textContent = count + (count === 1 ? ' proyecto' : ' proyectos');
  if (updateUrl && location.pathname + location.search !== filterPaths[filter]) {
    history.pushState({ portfolio: { view: 'grid', filter } }, '', filterPaths[filter]);
  }
}

filterLinks.forEach(link => link.addEventListener('click', event => {
  if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0) return;
  event.preventDefault();
  filterProjects(link.dataset.filter, true);
}));
function currentFilter() {
  const query = new URLSearchParams(location.search).get('tipo');
  if (validFilters.has(query)) return query;
  return Object.keys(filterPaths).find(key => new URL(filterPaths[key], location.origin).pathname === location.pathname && key !== 'direccion') || 'todos';
}
filterProjects(currentFilter());
history.replaceState({ portfolio: { view: 'grid', filter: currentFilter() } }, '', location.href);
window.addEventListener('popstate', () => {
  const state = history.state?.portfolio;
  if (state?.view === 'film') {
    filterProjects(state.filter);
    openFilm(state.key, { filter: state.filter, updateHistory: false });
  } else {
    dismissFilm();
    filterProjects(state?.filter || currentFilter());
  }
});
