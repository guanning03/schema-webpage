const tabs = [...document.querySelectorAll('[role="tab"]')];
document.querySelectorAll('a[aria-disabled="true"]').forEach(link => {
  link.addEventListener('click', event => event.preventDefault());
});
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

function setupGameSelector(group, filePrefix, benchmark) {
  const select = document.getElementById(`${group}-game`);
  const video = document.getElementById(`${group}-video`);
  select.addEventListener('change', () => {
    const option = select.selectedOptions[0];
    const stem = `${filePrefix}${select.value}`;
    video.pause();
    video.src = `assets/videos/${stem}.mp4`;
    video.poster = `assets/posters/${stem}.jpg`;
    video.setAttribute('aria-label', `Schema gameplay on ${benchmark}: ${option.dataset.game}`);
    const download = video.querySelector('a');
    download.href = video.src;
    download.textContent = `Download the ${option.dataset.game} replay`;
    document.getElementById(`${group}-caption`).textContent = option.dataset.caption;
    video.load();
  });
}
setupGameSelector('arc', 'arc3_fable5_', 'ARC-AGI-3');
setupGameSelector('dig', 'digbench_schema_', 'DiG-bench');

document.querySelectorAll('video').forEach(video => {
  video.addEventListener('play', () => {
    document.querySelectorAll('video').forEach(other => { if (other !== video) other.pause(); });
  });
});

const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
document.querySelectorAll('.case-study').forEach(card => {
  const gif = card.querySelector('.case-gif');
  const button = card.querySelector('.case-toggle');
  const title = card.querySelector('h5').textContent;
  let visible = false;
  let paused = reducedMotion.matches;
  function update() {
    const source = visible && !paused ? gif.dataset.gif : gif.dataset.poster;
    if (gif.getAttribute('src') !== source) gif.setAttribute('src', source);
    button.dataset.paused = String(paused);
    button.title = paused ? 'Play replay' : 'Pause replay';
    button.setAttribute('aria-label', `${paused ? 'Play' : 'Pause'} ${title} comparison`);
  }
  button.addEventListener('click', () => { paused = !paused; update(); });
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      visible = entries[0].isIntersecting;
      update();
    }, { threshold: .1 });
    observer.observe(gif);
  } else {
    visible = true;
  }
  update();
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
