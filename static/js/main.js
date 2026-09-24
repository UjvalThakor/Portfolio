/**
 * Ujval Thakor - Creative & Backend Developer Portfolio
 * Douglus-Inspired Controllers: Horizontal Scrolling, Draggable Panorama & Micro-Interactions
 */

document.addEventListener('DOMContentLoaded', () => {
  initPreloader();
  initHorizontalScroll();
  initDraggablePanorama();
  initScrollObserver();
  initMagneticButtons();
});

/* 1. PRELOADER SEQUENCE */
function initPreloader() {
  const preloader = document.getElementById('preloader');
  const wordEl = document.getElementById('preloader-word');
  const subEl = document.getElementById('preloader-sub');
  const progressBar = document.getElementById('preloader-progress');

  if (!preloader || !wordEl) return;

  if (sessionStorage.getItem('visited_preloader')) {
    preloader.style.display = 'none';
    return;
  }

  const words = ['BUILD', 'CREATIVE', 'UJVAL.'];
  let currentIdx = 0;

  if (progressBar) {
    setTimeout(() => {
      progressBar.style.width = '100%';
    }, 50);
  }

  const interval = setInterval(() => {
    currentIdx++;
    if (currentIdx < words.length) {
      wordEl.style.opacity = '0';
      wordEl.style.transform = 'translateY(-15px)';

      setTimeout(() => {
        wordEl.textContent = words[currentIdx];
        if (currentIdx === words.length - 1) {
          wordEl.style.color = '#ff6432';
          if (subEl) subEl.classList.add('active');
        }
        wordEl.style.opacity = '1';
        wordEl.style.transform = 'translateY(0)';
      }, 180);
    } else {
      clearInterval(interval);
      setTimeout(() => {
        preloader.classList.add('preloader--done');
        sessionStorage.setItem('visited_preloader', 'true');
      }, 650);
    }
  }, 480);
}

/* 2. HORIZONTAL SCROLL CONTROLLER (Douglus bi-directional horizontal navigation) */
function initHorizontalScroll() {
  const canvas = document.getElementById('horizontal-canvas');
  if (!canvas) return;

  const progressBar = document.getElementById('h-progress-bar');
  const indicatorLabel = document.getElementById('h-indicator-label');
  const btnPrev = document.getElementById('h-nav-prev');
  const btnNext = document.getElementById('h-nav-next');
  const panels = Array.from(document.querySelectorAll('.h-panel'));

  // Wheel listener: Forward wheel (deltaY > 0) -> moves right (forward);
  // Reverse wheel (deltaY < 0) -> moves left (backward / returning to previous pages)
  window.addEventListener('wheel', (e) => {
    // If hovering inside an element that needs internal vertical scroll (like terminal history)
    const verticalScrollable = e.target.closest('#dev-terminal-screen, .scrollable-y');
    if (verticalScrollable) {
      const isAtTop = verticalScrollable.scrollTop === 0 && e.deltaY < 0;
      const isAtBottom = verticalScrollable.scrollTop + verticalScrollable.clientHeight >= verticalScrollable.scrollHeight && e.deltaY > 0;
      if (!isAtTop && !isAtBottom) {
        return; // Allow natural scroll inside terminal
      }
    }

    e.preventDefault();

    // Calculate scroll amount
    const delta = e.deltaY !== 0 ? e.deltaY : e.deltaX;
    canvas.scrollBy({
      left: delta * 1.5,
      behavior: 'auto'
    });
  }, { passive: false });

  // Update progress bar & section indicator during scroll
  function updateScrollState() {
    const scrollLeft = canvas.scrollLeft;
    const maxScroll = canvas.scrollWidth - canvas.clientWidth;

    if (maxScroll > 0 && progressBar) {
      const percent = (scrollLeft / maxScroll) * 100;
      progressBar.style.width = `${Math.min(100, Math.max(0, percent))}%`;
    }

    if (indicatorLabel && panels.length > 0) {
      let currentLabel = '01 / HERO';
      panels.forEach(panel => {
        const offsetLeft = panel.offsetLeft;
        const width = panel.offsetWidth;
        if (scrollLeft >= offsetLeft - 120 && scrollLeft < offsetLeft + width - 120) {
          const panelTitle = panel.getAttribute('data-title');
          if (panelTitle) currentLabel = panelTitle;
        }
      });
      indicatorLabel.textContent = currentLabel;
    }
  }

  canvas.addEventListener('scroll', updateScrollState, { passive: true });
  updateScrollState();

  // Paging helpers for next / prev
  function getCurrentPanelIndex() {
    const currentScroll = canvas.scrollLeft;
    let closestIndex = 0;
    let closestDistance = Infinity;

    panels.forEach((p, idx) => {
      const dist = Math.abs(p.offsetLeft - currentScroll);
      if (dist < closestDistance) {
        closestDistance = dist;
        closestIndex = idx;
      }
    });
    return closestIndex;
  }

  function goToPanel(idx) {
    if (idx < 0) idx = 0;
    if (idx >= panels.length) idx = panels.length - 1;
    const target = panels[idx];
    if (target) {
      canvas.scrollTo({
        left: target.offsetLeft,
        behavior: 'smooth'
      });
    }
  }

  if (btnNext) {
    btnNext.addEventListener('click', (e) => {
      e.stopPropagation();
      const currentIdx = getCurrentPanelIndex();
      goToPanel(currentIdx + 1);
    });
  }

  if (btnPrev) {
    btnPrev.addEventListener('click', (e) => {
      e.stopPropagation();
      const currentIdx = getCurrentPanelIndex();
      goToPanel(currentIdx - 1);
    });
  }

  // Keyboard navigation: ArrowRight / ArrowLeft / PageDown / PageUp
  window.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    if (e.key === 'ArrowRight' || e.key === 'PageDown') {
      e.preventDefault();
      const currentIdx = getCurrentPanelIndex();
      goToPanel(currentIdx + 1);
    } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
      e.preventDefault();
      const currentIdx = getCurrentPanelIndex();
      goToPanel(currentIdx - 1);
    }
  });

  // Nav Links smooth scroll horizontally
  document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener('click', (e) => {
      const href = link.getAttribute('href');
      if (href === '#' || href === '') return;
      const target = document.querySelector(href);
      if (target) {
        e.preventDefault();
        canvas.scrollTo({
          left: target.offsetLeft,
          behavior: 'smooth'
        });
      }
    });
  });
}

/* 3. DRAGGABLE PANORAMA CANVAS (Hero Draggable banner) */
function initDraggablePanorama() {
  const frame = document.querySelector('.panorama-frame');
  const img = document.querySelector('.panorama-img');
  const handle = document.querySelector('.drag-circle-handle');

  if (!frame || !img) return;

  let isDown = false;
  let startX = 0;
  let currentTranslateX = -20; // percentage
  let minTranslate = -45;
  let maxTranslate = 0;

  function updateTransform(xPercent) {
    if (xPercent < minTranslate) xPercent = minTranslate;
    if (xPercent > maxTranslate) xPercent = maxTranslate;
    currentTranslateX = xPercent;
    img.style.transform = `translateX(${currentTranslateX}%)`;
  }

  frame.addEventListener('mousedown', (e) => {
    isDown = true;
    startX = e.pageX;
    frame.style.cursor = 'grabbing';
    if (handle) handle.style.transform = 'translateY(-50%) scale(1.1)';
  });

  window.addEventListener('mouseup', () => {
    if (isDown) {
      isDown = false;
      frame.style.cursor = 'grab';
      if (handle) handle.style.transform = 'translateY(-50%) scale(1)';
    }
  });

  frame.addEventListener('mousemove', (e) => {
    if (!isDown) return;
    e.preventDefault();
    const x = e.pageX;
    const walk = (x - startX) * 0.12;
    updateTransform(currentTranslateX + walk);
    startX = x;
  });

  frame.addEventListener('touchstart', (e) => {
    isDown = true;
    startX = e.touches[0].pageX;
  }, { passive: true });

  window.addEventListener('touchend', () => {
    isDown = false;
  });

  frame.addEventListener('touchmove', (e) => {
    if (!isDown) return;
    const x = e.touches[0].pageX;
    const walk = (x - startX) * 0.15;
    updateTransform(currentTranslateX + walk);
    startX = x;
  }, { passive: true });

  updateTransform(-15);
}

/* 4. REVEAL ON SCROLL */
function initScrollObserver() {
  const revealElements = document.querySelectorAll('.reveal-init');
  if (!revealElements.length) return;

  const observer = new IntersectionObserver((entries, obs) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('in-view');
        obs.unobserve(entry.target);
      }
    });
  }, {
    threshold: 0.08,
    rootMargin: '0px 0px -20px 0px'
  });

  revealElements.forEach(el => observer.observe(el));
}

/* 5. MAGNETIC BUTTONS */
function initMagneticButtons() {
  if (window.matchMedia('(pointer: coarse)').matches) return;

  const magneticBtns = document.querySelectorAll('.magnetic-btn');
  magneticBtns.forEach(btn => {
    btn.addEventListener('mousemove', (e) => {
      const rect = btn.getBoundingClientRect();
      const x = e.clientX - rect.left - rect.width / 2;
      const y = e.clientY - rect.top - rect.height / 2;
      btn.style.transform = `translate(${x * 0.22}px, ${y * 0.22}px)`;
    });

    btn.addEventListener('mouseleave', () => {
      btn.style.transform = 'translate(0px, 0px)';
    });
  });
}
