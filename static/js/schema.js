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

document.querySelectorAll('#videos video').forEach(video => {
  video.addEventListener('play', () => {
    document.querySelectorAll('#videos video').forEach(other => { if (other !== video) other.pause(); });
  });
});

const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
document.querySelectorAll('.case-study').forEach(card => {
  const replay = card.querySelector('.case-replay');
  const button = card.querySelector('.case-toggle');
  const title = card.querySelector('h5').textContent;
  const timeline = window.schemaCaseTimelines[card.dataset.case];
  const counters = [...card.querySelectorAll('[data-case-count]')];
  const cue = card.querySelector('.case-cue');
  const evidence = card.querySelector('.case-evidence');
  let previousStep = -1;
  let previousScene = null;
  function updateExplanation(seconds = replay.currentTime) {
    const elapsed = seconds * 1000 + .5;
    let low = 0, high = timeline.starts.length;
    while (low + 1 < high) {
      const middle = Math.floor((low + high) / 2);
      if (timeline.starts[middle] <= elapsed) low = middle;
      else high = middle;
    }
    const step = low;
    if (step === previousStep) return;
    previousStep = step;
    const segment = timeline.segments.findLast(item => item.start <= step);
    const localStep = segment ? step - segment.start : step;
    if (segment) card.querySelector('.case-game').textContent = `AR25 · Level ${segment.level}`;
    counters.forEach((counter, side) => {
      const total = segment ? segment.counts[side] : timeline.counts[side];
      const complete = localStep >= total;
      counter.dataset.complete = String(complete);
      counter.textContent = `${complete ? 'Completed · ' : ''}${Math.min(localStep, total).toLocaleString('en-US')} actions`;
    });
    const scene = timeline.scenes.findLast(item => item.step <= step);
    if (scene === previousScene) return;
    previousScene = scene;
    cue.textContent = scene.text;
    evidence.replaceChildren();
    for (const detail of scene.detail || []) {
      const figure = document.createElement('figure');
      const content = document.createElement(detail.image ? 'img' : 'span');
      if (detail.image) {
        content.src = `assets/cases/${detail.image}`;
        content.alt = detail.label;
        content.width = 60;
        content.height = 60;
      } else {
        content.className = 'case-metric';
        content.textContent = detail.value;
      }
      const caption = document.createElement('figcaption');
      caption.textContent = detail.label;
      figure.append(content, caption);
      evidence.append(figure);
    }
    evidence.hidden = !scene.detail;
  }
  // Synchronize with displayed frames, including brief holds and loop restarts.
  // Text stays outside the video so it remains crisp at every display size.
  if ('requestVideoFrameCallback' in replay) {
    const onFrame = (_now, metadata) => {
      updateExplanation(metadata.mediaTime);
      replay.requestVideoFrameCallback(onFrame);
    };
    replay.requestVideoFrameCallback(onFrame);
  } else {
    replay.addEventListener('timeupdate', () => updateExplanation());
  }
  replay.addEventListener('seeked', () => updateExplanation());
  updateExplanation(0);
  let visible = false;
  let pausedByUser = reducedMotion.matches;
  function updateButton() {
    const paused = replay.paused;
    button.dataset.paused = String(paused);
    button.title = paused ? 'Play replay' : 'Pause replay';
    button.setAttribute('aria-label', `${paused ? 'Play' : 'Pause'} ${title} comparison`);
  }
  function updatePlayback() {
    if (visible && !pausedByUser && !document.hidden) {
      replay.play().catch(error => {
        if (error.name === 'AbortError') return;
        pausedByUser = true;
        updateButton();
      });
    } else {
      replay.pause();
    }
    updateButton();
  }
  button.addEventListener('click', () => {
    pausedByUser = !replay.paused;
    if (!pausedByUser) visible = true;
    updatePlayback();
  });
  replay.addEventListener('play', updateButton);
  replay.addEventListener('pause', updateButton);
  document.addEventListener('visibilitychange', updatePlayback);
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      visible = entries[0].isIntersecting && entries[0].intersectionRatio >= .55;
      updatePlayback();
    }, { threshold: [0, .55] });
    observer.observe(replay);
  } else {
    visible = true;
  }
  updatePlayback();
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
