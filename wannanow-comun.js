/* WannaNow · menú, modales legales y consentimiento de cookies (compartido) */
    /* ── Hamburger Menu & Legal Modals ─────────── */
    (() => {
        const hamburgerBtn  = document.getElementById('hamburgerBtn');
        const hamDropdown   = document.getElementById('hamDropdown');
        const openPrivacidad = document.getElementById('openPrivacidad');
        const openTerminos   = document.getElementById('openTerminos');
        const modalPrivacidad = document.getElementById('modalPrivacidad');
        const modalTerminos   = document.getElementById('modalTerminos');
        const closePrivacidad = document.getElementById('closePrivacidad');
        const closeTerminos   = document.getElementById('closeTerminos');
        const backdropPrivacidad = document.getElementById('backdropPrivacidad');
        const backdropTerminos   = document.getElementById('backdropTerminos');

        const allModals = [modalPrivacidad, modalTerminos].filter(Boolean);

        // Toggle dropdown
        hamburgerBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const isOpen = hamDropdown.classList.toggle('is-open');
            hamburgerBtn.classList.toggle('is-open', isOpen);
            hamburgerBtn.setAttribute('aria-expanded', isOpen);
        });

        // Close dropdown on outside click
        document.addEventListener('click', (e) => {
            if (!hamDropdown.contains(e.target) && e.target !== hamburgerBtn) {
                hamDropdown.classList.remove('is-open');
                hamburgerBtn.classList.remove('is-open');
                hamburgerBtn.setAttribute('aria-expanded', 'false');
            }
        });

        // Open modals
        function openModal(modal) {
            if (!modal) return;
            modal.classList.add('is-open');
            document.body.style.overflow = 'hidden';
            hamDropdown.classList.remove('is-open');
            hamburgerBtn.classList.remove('is-open');
            hamburgerBtn.setAttribute('aria-expanded', 'false');
        }

        function closeModal(modal) {
            if (!modal) return;
            modal.classList.remove('is-open');
            document.body.style.overflow = '';
        }

        openPrivacidad?.addEventListener('click', (e) => { e.preventDefault(); openModal(modalPrivacidad); });
        openTerminos?.addEventListener('click',   (e) => { e.preventDefault(); openModal(modalTerminos); });

        closePrivacidad?.addEventListener('click', () => closeModal(modalPrivacidad));
        closeTerminos?.addEventListener('click',   () => closeModal(modalTerminos));

        backdropPrivacidad?.addEventListener('click', () => closeModal(modalPrivacidad));
        backdropTerminos?.addEventListener('click',   () => closeModal(modalTerminos));

        // Close on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                allModals.forEach(closeModal);
            }
        });

        /* ── Cookie Consent Banner (no bloqueante) ─────────── */
        const CONSENT_KEY = 'wannanow_cookie_consent';
        const cookieBanner = document.getElementById('cookieBanner');
        const cookieAcceptBtn = document.getElementById('cookieAcceptBtn');
        const cookieRejectBtn = document.getElementById('cookieRejectBtn');
        const cookieConfigureBtn = document.getElementById('cookieConfigureBtn');

        const cookiePrefsOverlay = document.getElementById('cookiePrefsOverlay');
        const prefAnalytics = document.getElementById('prefAnalytics');
        const prefMarketing = document.getElementById('prefMarketing');
        const prefPersonalization = document.getElementById('prefPersonalization');
        const cookiePrefsSave = document.getElementById('cookiePrefsSave');
        const cookiePrefsRejectAll = document.getElementById('cookiePrefsRejectAll');

        function getConsent() {
            try {
                const raw = localStorage.getItem(CONSENT_KEY);
                return raw ? JSON.parse(raw) : null;
            } catch (err) {
                return null;
            }
        }

        // categories: { analytics: bool, personalization: bool }. Las necesarias
        // no requieren consentimiento porque son imprescindibles para el servicio.
        function saveConsent(categories) {
            try {
                localStorage.setItem(CONSENT_KEY, JSON.stringify({
                    categories: categories,
                    date: new Date().toISOString()
                }));
            } catch (err) {
                // localStorage no disponible: el aviso podrá reaparecer, no es crítico
            }
            applyConsent(categories);
        }

        // Punto único donde activar/desactivar scripts de terceros según lo aceptado.
        // Ejemplo: if (categories.analytics) { /* cargar analítica */ }
        function applyConsent(categories) {
            window.wannanowConsent = categories;
            if (categories && categories.marketing) {
                window.loadMetaPixel && window.loadMetaPixel();
            } else {
                window.revokeMetaPixel && window.revokeMetaPixel();
            }
        }

        function hideBanner() {
            if (!cookieBanner) return;
            cookieBanner.classList.remove('is-open');
            setTimeout(() => cookieBanner.classList.remove('is-visible'), 400);
        }

        function showBannerIfNeeded() {
            if (!cookieBanner) return;
            const consent = getConsent();
            if (consent) {
                applyConsent(consent.categories);
                return;
            }
            cookieBanner.classList.add('is-visible');
            requestAnimationFrame(() => {
                requestAnimationFrame(() => cookieBanner.classList.add('is-open'));
            });
        }

        function openPrefs() {
            if (!cookiePrefsOverlay) return;
            const consent = getConsent();
            if (prefAnalytics) prefAnalytics.checked = !!consent?.categories?.analytics;
            if (prefPersonalization) prefPersonalization.checked = !!consent?.categories?.personalization;
            if (prefMarketing) prefMarketing.checked = !!consent?.categories?.marketing;
            cookiePrefsOverlay.classList.add('is-visible');
            requestAnimationFrame(() => {
                requestAnimationFrame(() => cookiePrefsOverlay.classList.add('is-open'));
            });
        }

        function closePrefs() {
            if (!cookiePrefsOverlay) return;
            cookiePrefsOverlay.classList.remove('is-open');
            setTimeout(() => cookiePrefsOverlay.classList.remove('is-visible'), 350);
        }

        // "Aceptar todas": consentimiento a todas las categorías opcionales.
        cookieAcceptBtn?.addEventListener('click', () => {
            saveConsent({ analytics: true, personalization: true, marketing: true });
            hideBanner();
        });

        // "Rechazar": solo cookies necesarias. La navegación continúa con normalidad,
        // simplemente no se cargan analítica/personalización.
        cookieRejectBtn?.addEventListener('click', () => {
            saveConsent({ analytics: false, personalization: false, marketing: false });
            hideBanner();
        });

        // "Configurar": abre el panel para elegir categoría por categoría.
        cookieConfigureBtn?.addEventListener('click', () => {
            openPrefs();
        });

        cookiePrefsSave?.addEventListener('click', () => {
            saveConsent({
                analytics: !!prefAnalytics?.checked,
                personalization: !!prefPersonalization?.checked,
                marketing: !!prefMarketing?.checked
            });
            closePrefs();
            hideBanner();
        });

        cookiePrefsRejectAll?.addEventListener('click', () => {
            saveConsent({ analytics: false, personalization: false, marketing: false });
            closePrefs();
            hideBanner();
        });

        cookiePrefsOverlay?.addEventListener('click', (e) => {
            if (e.target === cookiePrefsOverlay) closePrefs();
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') closePrefs();
        });

        showBannerIfNeeded();
    })();
