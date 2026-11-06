"""Menú hamburguesa (móvil) con todas las secciones + «Hoy» en el menú superior de las páginas en español.
Idempotente: las páginas con data-menu="v2" no se tocan."""
import glob, re

ES = [('/', 'Inicio'), ('/planes-valencia-hoy/', 'Planes para hoy en Valencia'),
      ('/que-hacer-fin-de-semana-valencia/', 'Este fin de semana'), ('/que-hacer-valencia/', 'Qué hacer en Valencia'),
      ('/eventos-valencia/', 'Eventos en Valencia'), ('/planes-valencia/', 'Planes en Valencia'),
      ('/ocio-valencia/', 'Ocio en Valencia'), ('/sobre-wannanow/', '¿Qué es WannaNow?'), ('/prensa/', 'Prensa')]
ES_LEGAL = [('/politica-de-privacidad/', 'Política de Privacidad'), ('/terminos-y-condiciones/', 'Términos y Condiciones'),
            ('/politica-de-cookies/', 'Política de Cookies')]
EN = [('/en/', 'Home'), ('/en/things-to-do-valencia-today/', 'Things to do in Valencia today'),
      ('/en/things-to-do-valencia/', 'Things to do in Valencia'), ('/en/what-is-wannanow/', 'What is WannaNow?')]
EN_LEGAL = [('/politica-de-privacidad/', 'Privacy Policy (ES)'), ('/terminos-y-condiciones/', 'Terms &amp; Conditions (ES)'),
            ('/politica-de-cookies/', 'Cookie Policy (ES)')]
SEP = ' style="border-top:1px solid rgba(31,21,51,.1);margin-top:6px;padding-top:14px;font-size:13px"'
SMALL = ' style="font-size:13px"'
PLANTILLAS = {'planes-hoy/plantilla.html': '/planes-valencia-hoy/', 'planes-hoy/plantilla_en.html': '/en/things-to-do-valencia-today/',
              'planes-hoy/plantilla_finde.html': '/que-hacer-fin-de-semana-valencia/'}


def url_of(path):
    if path in PLANTILLAS:
        return PLANTILLAS[path]
    return '/' if path == 'index.html' else '/' + path[:-len('index.html')]


def dropdown(path, lang, lang_link, ind):
    here = url_of(path)
    main, legal = (EN, EN_LEGAL) if lang == 'en' else (ES, ES_LEGAL)
    rows = []
    for href, txt in main:
        cur = ' aria-current="page" style="font-weight:700;color:var(--pink)"' if href == here else ''
        rows.append(f'{ind}    <a href="{href}" class="nav-link"{cur}>{txt}</a>')
    for i, (href, txt) in enumerate(legal):
        hl = ' hreflang="es"' if lang == 'en' else ''
        rows.append(f'{ind}    <a href="{href}" class="nav-link"{hl}{SEP if i == 0 else SMALL}>{txt}</a>')
    rows.append(f'{ind}    {lang_link}')
    return (f'<div class="hamburger-dropdown" id="hamDropdown" data-menu="v2" '
            f'style="max-height:calc(100vh - 84px);overflow-y:auto">\n' + '\n'.join(rows) + f'\n{ind}</div>')


def procesar(path):
    h = open(path, encoding='utf-8').read()
    if 'id="hamDropdown"' not in h:
        return 'sin menú'
    if 'data-menu="v2"' in h:
        return 'ya estaba'
    lang = 'en' if path.startswith('en/') or path.endswith('_en.html') else 'es'
    m = re.search(r'( *)<div class="hamburger-dropdown" id="hamDropdown">(.*?)</div>', h, re.S)
    ind, inner = m.group(1), m.group(2)
    want = 'en' if lang == 'es' else 'es'
    sw = re.search(r'<a href="[^"]*" class="nav-link" hreflang="%s" lang="%s">[^<]*</a>' % (want, want), inner)
    if sw:
        lang_link = sw.group(0)
    else:  # sin versión equivalente: el mismo destino que el «EN»/«ES» del menú superior, o la portada
        t = re.search(r'<li><a href="([^"]*)" hreflang="%s"' % want, h)
        dest = t.group(1) if t else ('/en/' if want == 'en' else '/')
        lang_link = (f'<a href="{dest}" class="nav-link" hreflang="en" lang="en">English</a>' if want == 'en'
                     else f'<a href="{dest}" class="nav-link" hreflang="es" lang="es">Español</a>')
    h = h[:m.start(0)] + ind + dropdown(path, lang, lang_link, ind) + h[m.end(0):]
    # «Hoy» en el menú superior (solo español)
    if lang == 'es' and '<a href="/planes-valencia-hoy/"' not in h[h.index('<ul class="nav-links"'):h.index('</ul>', h.index('<ul class="nav-links"'))]:
        u = h.index('<ul class="nav-links"')
        li = h.index('<li>', u)
        ind2 = h[h.rindex('\n', 0, li) + 1:li]
        cur = ' aria-current="page"' if url_of(path) == '/planes-valencia-hoy/' else ''
        h = h[:li] + f'<li><a href="/planes-valencia-hoy/"{cur}>Hoy</a></li>\n' + ind2 + h[li:]
        h = h.replace('<ul class="nav-links" id="navLinks">', '<ul class="nav-links" id="navLinks" style="gap:clamp(14px,2.2vw,36px);white-space:nowrap">', 1)
    open(path, 'w', encoding='utf-8').write(h)
    return 'ok ' + lang


if __name__ == '__main__':
    for f in sorted(glob.glob('**/*.html', recursive=True)):
        print(procesar(f), f)
