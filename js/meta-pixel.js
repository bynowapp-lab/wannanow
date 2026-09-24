/* ──────────────────────────────────────────────────────────────
   WannaNow · Meta Pixel (compartido por todas las páginas)

   Para activarlo: pega aquí el ID del Pixel de tu Meta Business.
   Mientras esté vacío, NO se carga nada de Facebook.

   Solo se carga si el usuario acepta la categoría "Publicidad"
   en el banner de cookies (lo gestiona js/wannanow-comun.js).
────────────────────────────────────────────────────────────── */
window.META_PIXEL_ID = '';   // ← ejemplo: '123456789012345'

window.loadMetaPixel = function () {
    if (!window.META_PIXEL_ID) return;               // Pixel desactivado
    if (window.fbq) { fbq('consent', 'grant'); return; }
    !function(f,b,e,v,n,t,s)
    {if(f.fbq)return;n=f.fbq=function(){n.callMethod?
    n.callMethod.apply(n,arguments):n.queue.push(arguments)};
    if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
    n.queue=[];t=b.createElement(e);t.async=!0;
    t.src=v;s=b.getElementsByTagName(e)[0];
    s.parentNode.insertBefore(t,s)}(window, document,'script',
    'https://connect.facebook.net/en_US/fbevents.js');
    fbq('init', window.META_PIXEL_ID);
    fbq('track', 'PageView');
};

window.revokeMetaPixel = function () {
    if (window.fbq) fbq('consent', 'revoke');
};

// Si el usuario ya aceptó publicidad en una visita anterior, se carga al instante
try {
    var c = JSON.parse(localStorage.getItem('wannanow_cookie_consent') || 'null');
    if (c && c.categories && c.categories.marketing) window.loadMetaPixel();
} catch (e) {}
