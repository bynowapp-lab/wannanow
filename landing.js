/* WannaNow · landings: cursor personalizado y apariciones al hacer scroll (sin librerías) */
(() => {
    const cur = document.getElementById('cursor');
    const ring = document.getElementById('cursorRing');
    if (cur && ring && matchMedia('(pointer:fine)').matches) {
        let mx = -100, my = -100, rx = -100, ry = -100;
        document.addEventListener('mousemove', e => { mx = e.clientX; my = e.clientY; });
        (function loop() {
            rx += (mx - rx) * 0.14; ry += (my - ry) * 0.14;
            cur.style.transform  = `translate(${mx - 6}px, ${my - 6}px)`;
            ring.style.transform = `translate(${rx - 20}px, ${ry - 20}px)`;
            requestAnimationFrame(loop);
        })();
    } else {
        document.body.style.cursor = 'auto';
    }

    const els = document.querySelectorAll('.reveal');
    if (!('IntersectionObserver' in window)) { els.forEach(el => el.classList.add('is-in')); return; }
    const io = new IntersectionObserver(entries => {
        entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); } });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    els.forEach(el => io.observe(el));

    // Sombra del menú al hacer scroll
    const nav = document.querySelector('body > nav');
    if (nav) addEventListener('scroll', () => { nav.style.boxShadow = scrollY > 80 ? '0 4px 0 var(--ink)' : 'none'; }, { passive: true });
})();
