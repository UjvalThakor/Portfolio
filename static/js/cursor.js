/**
 * Custom Cursor Implementation
 * 1. Image 1 Effect: Solid dot + Black Follower Ring + Fluid Distortion Aura
 * 2. Image 2 Effect: Photo hover transforms ring into white circle with "DRAG ME"
 */

(function initCustomCursor() {
  if (window.matchMedia('(pointer: coarse)').matches && !window.matchMedia('(any-pointer: fine)').matches) {
    return;
  }

  // 1. Solid Dot
  const dot = document.createElement('div');
  dot.className = 'custom-cursor-dot';

  // 2. Hollow Ring
  const ring = document.createElement('div');
  ring.className = 'custom-cursor-ring';

  const label = document.createElement('span');
  label.className = 'cursor-label';
  label.textContent = 'DRAG ME';
  ring.appendChild(label);

  // 3. Fluid Distortion Aura (Wave ripples trailing the cursor)
  const aura = document.createElement('div');
  aura.className = 'cursor-aura';

  document.body.appendChild(aura);
  document.body.appendChild(dot);
  document.body.appendChild(ring);

  let mouseX = -200;
  let mouseY = -200;
  let prevMouseX = -200;
  let prevMouseY = -200;

  let ringX = -200;
  let ringY = -200;

  let auraX = -200;
  let auraY = -200;
  let auraAngle = 0;
  let isMoving = false;
  let isDragging = false;

  window.addEventListener('mousemove', (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
    dot.style.transform = `translate3d(${mouseX}px, ${mouseY}px, 0) translate(-50%, -50%)`;

    if (!isMoving) {
      isMoving = true;
      document.body.classList.add('cursor-active');
      requestAnimationFrame(renderCursor);
    }
  }, { passive: true });

  function renderCursor() {
    // Ring follows mouse with smooth interpolation (crisp 0.25 spring)
    ringX += (mouseX - ringX) * 0.25;
    ringY += (mouseY - ringY) * 0.25;
    
    const dragScale = isDragging ? ' scale(0.92)' : '';
    ring.style.transform = `translate3d(${ringX}px, ${ringY}px, 0) translate(-50%, -50%)${dragScale}`;

    // Calculate mouse velocity & angle for fluid trailing aura
    const vx = mouseX - prevMouseX;
    const vy = mouseY - prevMouseY;
    const speed = Math.sqrt(vx * vx + vy * vy);

    if (speed > 1.2) {
      auraAngle = Math.atan2(vy, vx) * (180 / Math.PI);
    }

    // Aura follows with slightly looser spring
    auraX += (mouseX - auraX) * 0.1;
    auraY += (mouseY - auraY) * 0.1;

    const stretchX = 1 + Math.min(speed * 0.035, 0.75);
    const stretchY = 1 - Math.min(speed * 0.015, 0.25);

    aura.style.transform = `translate3d(${auraX}px, ${auraY}px, 0) translate(-50%, -50%) rotate(${auraAngle}deg) scale(${stretchX}, ${stretchY})`;

    prevMouseX = mouseX;
    prevMouseY = mouseY;

    const diff = Math.abs(mouseX - ringX) + Math.abs(mouseY - ringY) + Math.abs(mouseX - auraX) + Math.abs(mouseY - auraY);
    if (diff > 0.05 || speed > 0.1) {
      requestAnimationFrame(renderCursor);
    } else {
      isMoving = false;
    }
  }

  // Mousedown & mouseup for drag tactile feedback
  window.addEventListener('mousedown', () => {
    isDragging = true;
    document.body.classList.add('cursor-dragging');
    if (!isMoving) {
      isMoving = true;
      requestAnimationFrame(renderCursor);
    }
  });

  window.addEventListener('mouseup', () => {
    isDragging = false;
    document.body.classList.remove('cursor-dragging');
    if (!isMoving) {
      isMoving = true;
      requestAnimationFrame(renderCursor);
    }
  });

  // Dynamic Hover Target State Handler
  function updateHoverState(el) {
    if (!el || !(el instanceof Element)) {
      document.body.classList.remove('cursor-hover-photo', 'cursor-hover-project', 'cursor-hover-link');
      return;
    }

    // 1. Photo / Panorama hover -> dynamic frosted "DRAG ME" icon
    const photoTarget = el.closest('.panorama-frame, .panorama-container, .panorama-img, [data-cursor="drag"]');
    if (photoTarget) {
      label.textContent = 'DRAG ME';
      document.body.classList.add('cursor-hover-photo');
      document.body.classList.remove('cursor-hover-project', 'cursor-hover-link');
      return;
    }

    // 2. Project card hover -> "VIEW"
    const projectCard = el.closest('.h-project-card, .project-card, [data-cursor="view"]');
    if (projectCard) {
      label.textContent = 'VIEW';
      document.body.classList.add('cursor-hover-project');
      document.body.classList.remove('cursor-hover-photo', 'cursor-hover-link');
      return;
    }

    // 3. Links & interactive elements
    const interactive = el.closest('a, button, .term-chip, .sim-btn, .pipeline-node, input, select, textarea, .passion-word, .passion-widget-squircle, .passion-widget-circle, [data-cursor="pointer"]');
    if (interactive) {
      document.body.classList.add('cursor-hover-link');
      document.body.classList.remove('cursor-hover-photo', 'cursor-hover-project');
      return;
    }

    // Default: reset all custom hover classes
    document.body.classList.remove('cursor-hover-photo', 'cursor-hover-project', 'cursor-hover-link');
  }

  document.addEventListener('mouseover', (e) => {
    updateHoverState(e.target);
  });

  document.addEventListener('mouseout', (e) => {
    if (e.relatedTarget) {
      updateHoverState(e.relatedTarget);
    } else {
      updateHoverState(null);
    }
  });

  /* ========================================================================
     LIQUID WAVE TEXT DISTORTION CONTROLLER (Exact Douglus Navigation Effect)
     ======================================================================== */
  function initLiquidTextDistortion() {
    const filter = document.getElementById('filter-liquid');
    const feTurbulence = document.getElementById('fe-liquid-turbulence');
    const feDisplacement = document.getElementById('fe-liquid-displacement');

    if (!filter || !feTurbulence || !feDisplacement) return;

    const targets = document.querySelectorAll('.nav-center-link, .nav-social-link, .nav-brand a, .has-liquid-link');
    if (!targets.length) return;

    let currentScale = 0;
    let targetScale = 0;
    let animFrame = null;
    const activeTargets = new Set();
    let lastMouseX = 0;
    let lastMouseY = 0;
    let lastTime = performance.now();

    // Wrap target contents with inner span and underline deco line
    targets.forEach((el) => {
      if (!el.querySelector('.menu__link-inner')) {
        const innerText = el.innerHTML;
        el.innerHTML = '';

        const innerSpan = document.createElement('span');
        innerSpan.className = 'menu__link-inner';
        innerSpan.innerHTML = innerText;
        el.appendChild(innerSpan);

        const decoLine = document.createElement('span');
        decoLine.className = 'menu__link-deco';
        el.appendChild(decoLine);
      }

      el.addEventListener('mouseenter', (e) => {
        activeTargets.add(el);
        const inner = el.querySelector('.menu__link-inner');
        const line = el.querySelector('.menu__link-deco');
        if (inner) inner.style.filter = 'url(#filter-liquid)';
        if (line) line.style.filter = 'url(#filter-liquid)';

        lastMouseX = e.clientX;
        lastMouseY = e.clientY;
        lastTime = performance.now();

        // Initial burst on enter
        targetScale = Math.max(targetScale, 38);
        startAnimation();
      });

      el.addEventListener('mousemove', (e) => {
        if (!activeTargets.has(el)) return;
        const now = performance.now();
        const dt = Math.max(1, now - lastTime);
        const dx = e.clientX - lastMouseX;
        const dy = e.clientY - lastMouseY;
        const speed = Math.sqrt(dx * dx + dy * dy) / dt; // px per ms

        lastMouseX = e.clientX;
        lastMouseY = e.clientY;
        lastTime = now;

        // Velocity-driven displacement impulse (faster scrubbing = more intense ripples)
        const impulse = Math.min(48, speed * 26 + 18);
        targetScale = Math.max(targetScale, impulse);
        startAnimation();
      });

      el.addEventListener('mouseleave', () => {
        activeTargets.delete(el);
      });
    });

    function startAnimation() {
      if (!animFrame) {
        animFrame = requestAnimationFrame(updateDistortion);
      }
    }

    function updateDistortion() {
      const now = performance.now();

      // Smooth interpolation & rapid decay when mouse slows or leaves
      currentScale += (targetScale - currentScale) * 0.22;
      targetScale *= 0.86;

      if (feDisplacement) {
        // High-frequency jitter creates boiling liquid wave effect from video
        const jitter = (Math.random() - 0.5) * (currentScale * 0.28);
        feDisplacement.scale.baseVal = Math.max(0, currentScale + jitter);
      }

      if (feTurbulence && currentScale > 0.8) {
        // Dynamic horizontal wave shift
        const freqY = 0.65 + Math.sin(now * 0.012) * 0.15;
        feTurbulence.setAttribute('baseFrequency', `0.01 ${freqY.toFixed(3)}`);
        feTurbulence.setAttribute('seed', Math.floor(now * 0.04) % 100);
      }

      if (currentScale > 0.3 || targetScale > 0.3 || activeTargets.size > 0) {
        animFrame = requestAnimationFrame(updateDistortion);
      } else {
        // Settle completely to crystal clear text
        currentScale = 0;
        targetScale = 0;
        if (feDisplacement) feDisplacement.scale.baseVal = 0;
        targets.forEach((el) => {
          const inner = el.querySelector('.menu__link-inner');
          const line = el.querySelector('.menu__link-deco');
          if (inner) inner.style.filter = 'none';
          if (line) line.style.filter = 'none';
        });
        animFrame = null;
      }
    }
  }

  // Initialize on load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initLiquidTextDistortion);
  } else {
    initLiquidTextDistortion();
  }

  // Direct element binding for instantaneous, flicker-free entrance on panorama
  const initPanoramaHover = () => {
    const panoramaElements = document.querySelectorAll('.panorama-frame, .panorama-container');
    panoramaElements.forEach((el) => {
      el.addEventListener('mouseenter', () => {
        label.textContent = 'DRAG ME';
        document.body.classList.add('cursor-hover-photo');
        document.body.classList.remove('cursor-hover-project', 'cursor-hover-link');
      });
      el.addEventListener('mouseleave', (e) => {
        if (!e.relatedTarget || !e.relatedTarget.closest('.panorama-frame, .panorama-container')) {
          document.body.classList.remove('cursor-hover-photo');
        }
      });
    });
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPanoramaHover);
  } else {
    initPanoramaHover();
  }

  // Hide on leaving browser window
  document.addEventListener('mouseleave', () => {
    dot.style.opacity = '0';
    ring.style.opacity = '0';
  });

  document.addEventListener('mouseenter', () => {
    dot.style.opacity = '1';
    ring.style.opacity = '1';
  });
})();
