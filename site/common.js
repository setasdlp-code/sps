const year = document.querySelector('#year');
if (year) year.textContent = new Date().getFullYear();

function projectUrl(key, filter = 'todos') {
  return '/' + key + '/' + (filter !== 'todos' ? '?tipo=' + encodeURIComponent(filter) : '');
}

function configureNextProject(container, key, filter = 'todos') {
  const section = container.querySelector('.next-project');
  if (!section) return;
  const order = projectOrders[filter]?.includes(key) ? projectOrders[filter] : projectOrders.todos;
  if (order.length < 2) {
    section.hidden = true;
    return;
  }
  section.hidden = false;
  const nextKey = order[(order.indexOf(key) + 1) % order.length];
  const project = projectCatalogue[nextKey];
  const link = section.querySelector('.next-project-link');
  link.href = projectUrl(nextKey, filter);
  link.dataset.nextKey = nextKey;
  // Image attributes are escaped by the static generator from local asset metadata.
  const template = document.createElement('template');
  template.innerHTML = '<img ' + project.imageAttributes + ' loading="lazy" decoding="async">';
  const image = template.content.firstElementChild;
  image.alt = 'Imagen de ' + project.title;
  link.querySelector('img').replaceWith(image);
  link.querySelector('.next-project-caption > span').textContent = project.title;
}

if (typeof projectCatalogue !== 'undefined') {
  const key = location.pathname.split('/').filter(Boolean)[0];
  if (projectCatalogue[key]) {
    const requested = new URLSearchParams(location.search).get('tipo');
    const filter = projectOrders[requested]?.includes(key) ? requested : 'todos';
    configureNextProject(document, key, filter);
    document.querySelectorAll('header nav [data-filter]').forEach(link => {
      if (link.dataset.filter === filter) link.setAttribute('aria-current', 'page');
      else link.removeAttribute('aria-current');
    });
  }
}
