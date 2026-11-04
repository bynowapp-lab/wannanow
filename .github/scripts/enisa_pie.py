"""Añade el sello de ENISA (empresa emergente) al pie de todas las páginas HTML de wannanow.app.
Idempotente: si la página ya tiene el marcador <!-- ENISA -->, no la toca."""
import glob, re, sys

IMG = '/img/enisa-empresa-emergente.webp'
TXT = {
    'es': ('BYNOW VALENCIA, S.L., la sociedad que desarrolla WannaNow, ha sido reconocida por la Empresa Nacional de '
           'Innovación (ENISA) como empresa emergente conforme a la Ley 28/2022, de fomento del ecosistema de las '
           'empresas emergentes.',
           'Gobierno de España · Ministerio de Industria y Turismo · ENISA'),
    'en': ('BYNOW VALENCIA, S.L., the company that develops WannaNow, has been recognised by ENISA (Empresa Nacional de '
           'Innovación, Spain\'s National Innovation Company) as a start-up (empresa emergente) under Law 28/2022 on the '
           'promotion of the start-up ecosystem.',
           'Government of Spain · Ministry of Industry and Tourism · ENISA'),
}


def bloque(lang, indent='        '):
    txt, alt = TXT[lang]
    return (f'{indent}<!-- ENISA -->\n'
            f'{indent}<div class="enisa-sello" style="display:flex;flex-wrap:wrap;align-items:center;justify-content:center;'
            f'gap:10px 16px;margin:18px auto 14px;max-width:760px;text-align:left">'
            f'<img src="{IMG}" alt="{alt}" width="339" height="72" loading="lazy" decoding="async" '
            f'style="height:36px;width:auto;display:block;flex:0 0 auto">'
            f'<p style="margin:0;flex:1 1 260px;font-size:.72rem;line-height:1.45;opacity:.8">{txt}</p></div>\n'
            f'{indent}<!-- /ENISA -->\n')


def lang_of(path, html):
    return 'en' if path.startswith('en/') or path.endswith('_en.html') or '<html lang="en"' in html else 'es'


def procesar(path):
    h = open(path, encoding='utf-8').read()
    if '<!-- ENISA -->' in h:
        return 'ya estaba'
    lang = lang_of(path, h)
    if '</footer>' in h:  # landings y plantillas: dentro del pie, antes de la línea legal
        m = re.search(r'(\n[ \t]*)<p>©', h[h.rindex('<footer'):])
        if m:
            i = h.rindex('<footer') + m.start() + 1
            ind = m.group(1).lstrip('\n')
            h = h[:i] + bloque(lang, ind) + h[i:]
        else:
            i = h.rindex('</footer>')
            h = h[:i] + bloque(lang) + h[i:]
    elif 'margin-top:14px;font-size:.78rem;opacity:.75;text-align:center">WannaNow' in h:  # home
        i = h.index('<p style="margin-top:14px;font-size:.78rem;opacity:.75;text-align:center">WannaNow')
        j = h.rindex('\n', 0, i) + 1
        h = h[:j] + bloque(lang, h[j:i]) + h[j:]
    elif '</body>' in h:  # páginas legales (sin pie): pie sencillo
        i = h.rindex('</body>')
        h = h[:i] + '<footer style="margin-top:40px;padding-top:12px;border-top:1px solid #ddd">\n' + bloque(lang, '') + '</footer>\n' + h[i:]
    else:
        return 'SIN SITIO'
    open(path, 'w', encoding='utf-8').write(h)
    return 'ok ' + lang


if __name__ == '__main__':
    for f in sorted(glob.glob('**/*.html', recursive=True)):
        if f.count('/') == 0 and f != 'index.html':
            continue  # archivos de verificación en la raíz
        print(procesar(f), f)
