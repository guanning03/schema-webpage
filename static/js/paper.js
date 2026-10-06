const tocLinks = [...document.querySelectorAll('.page-toc a')];
const sectionIds = tocLinks.map(link => document.querySelector(link.getAttribute('href'))).filter(Boolean);
let scheduled = false;
function updateToc() {
  let active = sectionIds[0];
  for (const section of sectionIds) {
    if (section.getBoundingClientRect().top <= 180) active = section;
  }
  for (const link of tocLinks) {
    if (link.hash === `#${active.id}`) link.setAttribute('aria-current', 'location');
    else link.removeAttribute('aria-current');
  }
  scheduled = false;
}
window.addEventListener('scroll', () => {
  if (!scheduled) { scheduled = true; requestAnimationFrame(updateToc); }
}, { passive: true });
updateToc();

const tabs = [...document.querySelectorAll('[role="tab"]')];
function activateTab(tab, moveFocus = false) {
  for (const item of tabs) {
    const selected = item === tab;
    item.setAttribute('aria-selected', String(selected));
    item.tabIndex = selected ? 0 : -1;
    const panel = document.getElementById(item.getAttribute('aria-controls'));
    panel.hidden = !selected;
    if (!selected) panel.querySelectorAll('video').forEach(video => video.pause());
  }
  if (moveFocus) tab.focus();
}
tabs.forEach((tab, index) => {
  tab.addEventListener('click', () => activateTab(tab));
  tab.addEventListener('keydown', event => {
    let target;
    if (event.key === 'ArrowRight') target = (index + 1) % tabs.length;
    if (event.key === 'ArrowLeft') target = (index - 1 + tabs.length) % tabs.length;
    if (event.key === 'Home') target = 0;
    if (event.key === 'End') target = tabs.length - 1;
    if (target !== undefined) { event.preventDefault(); activateTab(tabs[target], true); }
  });
});

const arcSelect = document.getElementById('arc-game');
arcSelect.addEventListener('change', () => {
  const video = document.getElementById('arc-video');
  const game = arcSelect.value;
  video.pause();
  video.src = `assets/videos/arc3_fable5_${game}.mp4`;
  video.poster = `assets/posters/arc3_fable5_${game}.jpg`;
  video.load();
  document.getElementById('arc-caption').textContent = game === 'ls20'
    ? 'LS20: discover movement, symbol transformations, and energy constraints, then reuse the program to plan through all seven levels.'
    : 'FT09: discover how clicking a tile changes its neighbors, encode the interaction rule, and solve the game through program-guided planning.';
});

document.querySelectorAll('video').forEach(video => {
  video.addEventListener('play', () => {
    document.querySelectorAll('video').forEach(other => { if (other !== video) other.pause(); });
  });
});

const copyButton = document.getElementById('copy-citation');
copyButton.addEventListener('click', async () => {
  const citation = document.getElementById('citation').textContent;
  const status = document.getElementById('copy-status');
  try {
    await navigator.clipboard.writeText(citation);
    copyButton.textContent = 'Copied!';
    status.textContent = 'BibTeX copied to clipboard.';
    setTimeout(() => { copyButton.textContent = 'Copy BibTeX'; }, 2000);
  } catch {
    const selection = window.getSelection();
    const range = document.createRange();
    range.selectNodeContents(document.getElementById('citation'));
    selection.removeAllRanges();
    selection.addRange(range);
    status.textContent = 'Citation selected. Press Command+C or Control+C to copy.';
    copyButton.textContent = 'Citation selected';
  }
});

const figureDialog = document.getElementById('figure-dialog');
const enlarged = document.getElementById('enlarged-figure');
document.querySelectorAll('.zoomable').forEach(img => {
  img.tabIndex = 0;
  img.setAttribute('role', 'button');
  img.setAttribute('aria-label', `Enlarge figure: ${img.alt}`);
  function showFigure() {
    enlarged.src = img.src;
    enlarged.alt = img.alt;
    figureDialog.showModal();
  }
  img.addEventListener('click', showFigure);
  img.addEventListener('keydown', event => {
    if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); showFigure(); }
  });
});
document.getElementById('close-figure').addEventListener('click', () => figureDialog.close());
figureDialog.addEventListener('click', event => {
  if (event.target !== figureDialog) return;
  const box = figureDialog.getBoundingClientRect();
  if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) figureDialog.close();
});
