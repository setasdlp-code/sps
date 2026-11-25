document.querySelector('#year').textContent = new Date().getFullYear();
const copyButton = document.querySelector('#copy-bio');
const status = document.querySelector('#copy-status');
copyButton.addEventListener('click', async () => {
  const text = document.querySelector('#biography-copy').innerText.trim();
  try {
    await navigator.clipboard.writeText(text);
    status.textContent = 'Texto copiado.';
  } catch {
    const selection = window.getSelection();
    const range = document.createRange();
    range.selectNodeContents(document.querySelector('#biography-copy'));
    selection.removeAllRanges();
    selection.addRange(range);
    status.textContent = 'Selecciona y copia el texto con el teclado.';
  }
});
