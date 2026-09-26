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
  initPassionPanel();
  initContactInteractions();
  initMobileNav();
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
    // If target or any ancestor is a vertically scrollable element with remaining scroll space, allow native vertical scrolling
    let target = e.target;
    let isInsideScrollable = false;
    while (target && target !== canvas && target !== document.body) {
      if (target.scrollHeight > target.clientHeight) {
        const style = window.getComputedStyle(target);
        if (
          style.overflowY === 'auto' || style.overflowY === 'scroll' ||
          style.overflow === 'auto' || style.overflow === 'scroll'
        ) {
          const atTop = target.scrollTop <= 0 && e.deltaY < 0;
          const atBottom = (target.scrollTop + target.clientHeight >= target.scrollHeight - 2) && e.deltaY > 0;
          if (!atTop && !atBottom) {
            isInsideScrollable = true;
            break;
          }
        }
      }
      target = target.parentElement;
    }

    if (isInsideScrollable) {
      return; // Allow native vertical scroll
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

    if (panels.length > 0) {
      let currentLabel = '01 / HERO';
      let activeId = 'hero';
      panels.forEach(panel => {
        const offsetLeft = panel.offsetLeft;
        const width = panel.offsetWidth;
        if (scrollLeft >= offsetLeft - 160 && scrollLeft < offsetLeft + width - 160) {
          const panelTitle = panel.getAttribute('data-title');
          if (panelTitle) currentLabel = panelTitle;
          activeId = panel.id;
        }
      });
      if (indicatorLabel) indicatorLabel.textContent = currentLabel;

      // Update fixed navigation active highlights
      const navWork = document.getElementById('nav-link-work');
      const navAbout = document.getElementById('nav-link-about');
      const navContact = document.getElementById('nav-link-contact');
      if (navWork && navAbout && navContact) {
        navWork.classList.toggle('is-active', activeId === 'work');
        navAbout.classList.toggle('is-active', activeId === 'about' || activeId === 'passion');
        navContact.classList.toggle('is-active', activeId === 'contact');
      }
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
  const badge = document.getElementById('panorama-cursor-badge');

  if (!frame || !img) return;

  let isDown = false;
  let startX = 0;
  let currentTranslateX = -20; // percentage
  let minTranslate = -45;
  let maxTranslate = 0;

  let mouseX = 0;
  let mouseY = 0;
  let currentX = 0;
  let currentY = 0;
  let isHovered = false;
  let animId = null;

  function animateBadge() {
    currentX += (mouseX - currentX) * 0.28;
    currentY += (mouseY - currentY) * 0.28;

    if (badge) {
      badge.style.left = `${currentX}px`;
      badge.style.top = `${currentY}px`;
    }

    if (isHovered || Math.abs(mouseX - currentX) > 0.1 || Math.abs(mouseY - currentY) > 0.1) {
      animId = requestAnimationFrame(animateBadge);
    }
  }

  function updateTransform(xPercent) {
    if (xPercent < minTranslate) xPercent = minTranslate;
    if (xPercent > maxTranslate) xPercent = maxTranslate;
    currentTranslateX = xPercent;
    img.style.transform = `translateX(${currentTranslateX}%)`;
  }

  frame.addEventListener('mouseenter', (e) => {
    isHovered = true;
    frame.classList.add('is-hovered');
    document.body.classList.add('cursor-hover-photo');

    const rect = frame.getBoundingClientRect();
    mouseX = e.clientX - rect.left;
    mouseY = e.clientY - rect.top;
    currentX = mouseX;
    currentY = mouseY;

    if (badge) {
      badge.style.left = `${currentX}px`;
      badge.style.top = `${currentY}px`;
    }

    cancelAnimationFrame(animId);
    animId = requestAnimationFrame(animateBadge);
  });

  frame.addEventListener('mousemove', (e) => {
    const rect = frame.getBoundingClientRect();
    mouseX = e.clientX - rect.left;
    mouseY = e.clientY - rect.top;

    if (!isHovered) {
      isHovered = true;
      frame.classList.add('is-hovered');
      document.body.classList.add('cursor-hover-photo');
      cancelAnimationFrame(animId);
      animId = requestAnimationFrame(animateBadge);
    }
  });

  frame.addEventListener('mouseleave', () => {
    isHovered = false;
    frame.classList.remove('is-hovered');
    document.body.classList.remove('cursor-hover-photo');
  });

  frame.addEventListener('mousedown', (e) => {
    isDown = true;
    startX = e.pageX;
    frame.classList.add('is-dragging');
    document.body.classList.add('cursor-dragging');
  });

  window.addEventListener('mouseup', () => {
    if (isDown) {
      isDown = false;
      frame.classList.remove('is-dragging');
      document.body.classList.remove('cursor-dragging');
    }
  });

  window.addEventListener('mousemove', (e) => {
    if (!isDown) return;
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

/* 6. PASSION & DISCIPLINES INTERACTION (Douglus 02/ Panel) */
function initPassionPanel() {
  const words = document.querySelectorAll('.passion-word');
  const smiley = document.querySelector('.passion-widget-circle');
  const dial = document.querySelector('.passion-widget-squircle');
  const moreBtn = document.querySelector('.passion-pill-btn');
  const canvas = document.getElementById('horizontal-canvas');

  // Word selection interaction
  words.forEach(word => {
    word.addEventListener('click', () => {
      words.forEach(w => w.classList.remove('is-active'));
      word.classList.add('is-active');
    });
  });

  // Widget 1 (Squircle): Tactile dial - spins dial on click, does NOT change emoji
  const widget1 = document.getElementById('widget-dev-squircle') || document.querySelector('.passion-widget-squircle');
  if (widget1) {
    let dialAngle = 0;
    widget1.addEventListener('click', () => {
      dialAngle += 90;
      const dialInner = widget1.querySelector('.widget-dial');
      if (dialInner) dialInner.style.transform = `rotate(${dialAngle}deg)`;
    });
  }

  // Widget 2 (Circle): Option B (Sideways Bracket Wink)
  // Has tactile spring bounce & wink micro-interaction on click
  const smileWidget = document.getElementById('widget-dev-circle') || document.querySelector('.passion-widget-circle');
  const smileContainer = document.getElementById('widget-smile-container');

  if (smileWidget && smileContainer) {
    let isWinkBlinking = false;

    smileWidget.addEventListener('click', () => {
      if (isWinkBlinking) return;
      isWinkBlinking = true;

      // Spring tactile bounce & playful nod
      smileWidget.style.transform = 'scale(0.88) translateY(3px)';
      smileContainer.style.transform = 'rotate(-12deg) scale(0.92)';

      setTimeout(() => {
        smileWidget.style.transform = 'scale(1.12) translateY(-4px)';
        smileContainer.style.transform = 'rotate(10deg) scale(1.08)';
      }, 120);

      setTimeout(() => {
        smileWidget.style.transform = '';
        smileContainer.style.transform = '';
        isWinkBlinking = false;
      }, 340);
    });
  }

  // Smooth scroll to about panel
  if (moreBtn && canvas) {
    moreBtn.addEventListener('click', (e) => {
      const aboutPanel = document.getElementById('about');
      if (aboutPanel) {
        e.preventDefault();
        canvas.scrollTo({
          left: aboutPanel.offsetLeft,
          behavior: 'smooth'
        });
      }
    });
  }
}

/* 7. CONTACT STAGE MICRO-INTERACTIONS (Douglus Editorial Live Systems) */
function initContactInteractions() {
  // Copy Email to Clipboard with tactile badge feedback
  const copyBtn = document.getElementById('chat-copy-email-btn');
  if (copyBtn) {
    copyBtn.addEventListener('click', async () => {
      const email = copyBtn.getAttribute('data-email') || 'ujvalthakor14@gmail.com';
      try {
        await navigator.clipboard.writeText(email);
        const label = copyBtn.querySelector('.pill-copy-text');
        const icon = copyBtn.querySelector('.pill-icon');
        const origText = label ? label.textContent : 'Copy Email';
        const origIcon = icon ? icon.textContent : '📋';

        copyBtn.classList.add('is-copied');
        if (label) label.textContent = 'COPIED TO CLIPBOARD ✓';
        if (icon) icon.textContent = '✓';

        setTimeout(() => {
          copyBtn.classList.remove('is-copied');
          if (label) label.textContent = origText;
          if (icon) icon.textContent = origIcon;
        }, 2200);
      } catch (err) {
        // Fallback for non-https contexts
        const textarea = document.createElement('textarea');
        textarea.value = email;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);

        copyBtn.classList.add('is-copied');
        const label = copyBtn.querySelector('.pill-copy-text');
        if (label) label.textContent = 'COPIED TO CLIPBOARD ✓';
        setTimeout(() => {
          copyBtn.classList.remove('is-copied');
          if (label) label.textContent = 'Copy Email';
        }, 2200);
      }
    });
  }

  // Squircle Widget tactile click
  const contactSquircle = document.querySelector('.chat-widget-squircle');
  if (contactSquircle) {
    contactSquircle.addEventListener('click', () => {
      contactSquircle.style.transform = 'scale(0.88) rotate(-8deg)';
      setTimeout(() => {
        contactSquircle.style.transform = 'scale(1.1) rotate(4deg)';
      }, 120);
      setTimeout(() => {
        contactSquircle.style.transform = '';
      }, 300);
    });
  }
}

/* 8. MOBILE NAVIGATION DRAWER */
function initMobileNav() {
  const toggleBtn = document.getElementById('mobile-toggle');
  const drawer = document.getElementById('mobile-drawer');
  const backdrop = document.getElementById('mobile-drawer-backdrop');
  const closeBtn = document.getElementById('mobile-drawer-close');

  if (!toggleBtn || !drawer) return;

  function openDrawer() {
    drawer.classList.add('is-open');
    toggleBtn.classList.add('is-open');
    toggleBtn.setAttribute('aria-expanded', 'true');
    drawer.setAttribute('aria-hidden', 'false');
    if (backdrop) backdrop.classList.add('is-open');
    document.body.style.overflow = 'hidden';
  }

  function closeDrawer() {
    drawer.classList.remove('is-open');
    toggleBtn.classList.remove('is-open');
    toggleBtn.setAttribute('aria-expanded', 'false');
    drawer.setAttribute('aria-hidden', 'true');
    if (backdrop) backdrop.classList.remove('is-open');
    document.body.style.overflow = '';
  }

  toggleBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    if (drawer.classList.contains('is-open')) {
      closeDrawer();
    } else {
      openDrawer();
    }
  });

  if (closeBtn) {
    closeBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      closeDrawer();
    });
  }

  if (backdrop) {
    backdrop.addEventListener('click', closeDrawer);
  }

  // Close when clicking any nav link
  const drawerLinks = drawer.querySelectorAll('a');
  drawerLinks.forEach((link) => {
    link.addEventListener('click', closeDrawer);
  });

  // Close on Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && drawer.classList.contains('is-open')) {
      closeDrawer();
    }
  });
}


