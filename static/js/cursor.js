/**
 * Custom Cursor Implementation
 * 1. Image 1 Effect: Solid dot + Black Follower Ring + Fluid Distortion Aura
 * 2. Image 2 Effect: Photo hover transforms ring into white circle with "DRAG ME"
 */

(function initCustomCursor() {
  if (window.matchMedia('(pointer: coarse)').matches || !window.matchMedia('(pointer: fine)').matches) {
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

  window.addEventListener('mousemove', (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
    dot.style.transform = `translate(${mouseX}px, ${mouseY}px)`;

    if (!isMoving) {
      isMoving = true;
      requestAnimationFrame(renderCursor);
    }
  }, { passive: true });

  function renderCursor() {
    // Ring follows mouse with smooth interpolation
    ringX += (mouseX - ringX) * 0.22;
    ringY += (mouseY - ringY) * 0.22;
    ring.style.transform = `translate(${ringX}px, ${ringY}px)`;

    // Calculate mouse velocity & angle for fluid trailing aura (Image 1 effect)
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

    aura.style.transform = `translate(${auraX}px, ${auraY}px) rotate(${auraAngle}deg) scale(${stretchX}, ${stretchY})`;

    prevMouseX = mouseX;
    prevMouseY = mouseY;

    const diff = Math.abs(mouseX - ringX) + Math.abs(mouseY - ringY) + Math.abs(mouseX - auraX) + Math.abs(mouseY - auraY);
    if (diff > 0.08 || speed > 0.1) {
      requestAnimationFrame(renderCursor);
    } else {
      isMoving = false;
    }
  }

  // Mousedown & mouseup for drag feedback
  window.addEventListener('mousedown', () => {
    document.body.classList.add('cursor-dragging');
  });

  window.addEventListener('mouseup', () => {
    document.body.classList.remove('cursor-dragging');
  });

  // Hover target listeners via event delegation
  document.addEventListener('mouseover', (e) => {
    const target = e.target;
    
    // 1. Photo hover -> transforms into Image 2 white circle "DRAG ME"
    const photoContainer = target.closest('.panorama-frame, .panorama-container, .panorama-img');
    if (photoContainer) {
      label.textContent = 'DRAG ME';
      document.body.classList.add('cursor-hover-photo');
      return;
    }

    // 2. Project card hover -> "VIEW"
    const projectCard = target.closest('.h-project-card, .project-card');
    if (projectCard) {
      label.textContent = 'VIEW';
      document.body.classList.add('cursor-hover-project');
      return;
    }

    // 3. Links & interactive elements
    const interactive = target.closest('a, button, .term-chip, .sim-btn, .pipeline-node');
    if (interactive) {
      document.body.classList.add('cursor-hover-link');
    }
  });

  document.addEventListener('mouseout', (e) => {
    const target = e.target;
    
    if (target.closest('.panorama-frame, .panorama-container, .panorama-img')) {
      document.body.classList.remove('cursor-hover-photo');
    }
    if (target.closest('.h-project-card, .project-card')) {
      document.body.classList.remove('cursor-hover-project');
    }
    if (target.closest('a, button, .term-chip, .sim-btn, .pipeline-node')) {
      document.body.classList.remove('cursor-hover-link');
    }
  });

  // Hide on leave window
  document.addEventListener('mouseleave', () => {
    dot.style.opacity = '0';
    ring.style.opacity = '0';
    aura.style.opacity = '0';
  });

  document.addEventListener('mouseenter', () => {
    dot.style.opacity = '1';
    ring.style.opacity = '1';
    aura.style.opacity = '0.85';
  });
})();
