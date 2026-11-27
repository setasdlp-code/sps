const form = document.querySelector('.contact-form');
const status = document.querySelector('.contact-status');

if (new URLSearchParams(location.search).get('enviado') === '1') {
  status.textContent = 'Mensaje enviado. Gracias.';
}

form.addEventListener('submit', async event => {
  event.preventDefault();
  const button = form.querySelector('button');
  button.disabled = true;
  status.textContent = 'Enviando…';
  try {
    const response = await fetch(form.action, {
      method: 'POST',
      headers: { Accept: 'application/json' },
      body: new FormData(form)
    });
    const result = await response.json();
    if (!response.ok || !result.success) throw new Error(result.message || response.status);
    form.reset();
    status.textContent = 'Mensaje enviado. Gracias.';
  } catch {
    status.textContent = 'No se pudo enviar. Intenta de nuevo en unos minutos.';
  } finally {
    button.disabled = false;
  }
});
