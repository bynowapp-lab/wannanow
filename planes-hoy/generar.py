#!/usr/bin/env python3
"""Genera /planes-valencia-hoy/index.html cada mañana.

- Lee la Agenda de la ciudad del Ayuntamiento de València (datos reutilizables
  citando la fuente, según su aviso legal) y elige 3-4 actividades vigentes hoy.
- No copia textos del Ayuntamiento: usa textos propios (textos.json) o una frase
  genérica por categoría.
- Si la agenda no responde, reutiliza la última lectura (ultimo.json).
Solo usa la librería estándar de Python.
"""
import json, os, re, sys, urllib.request, html as H
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
TZ = ZoneInfo('Europe/Madrid')
URL = 'https://www.valencia.es/cas/agenda-de-la-ciudad'
BASE_EVENTO = 'https://www.valencia.es/cas/agenda-de-la-ciudad/-/content/'

DIAS = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']
MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto',
         'septiembre', 'octubre', 'noviembre', 'diciembre']
MESES_C = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']

# Categorías preferidas (más atractivas para "qué hacer hoy")
PRIORIDAD = {'FESTIVALES': 0, 'FIESTAS': 0, 'MÚSICA': 1, 'DEPORTES': 1, 'OCIO ALTERNATIVO': 1,
             'EXPOSICIONES': 2, 'TEATRO': 2, 'AGENDA INFANTIL': 2, 'CINE': 2, 'ESPECTÁCULOS': 2,
             'MERCADOS': 2, 'RUTAS CULTURALES': 3, 'VISITAS GUIADAS': 3, 'FERIAS': 3, 'DANZA': 2,
             'CIRCO': 2, 'TALLERES': 3}

FRASE_CAT = {
    'MÚSICA': 'Música en directo dentro de la programación de la ciudad.',
    'DEPORTES': 'Actividad deportiva abierta a la ciudadanía.',
    'EXPOSICIONES': 'Exposición que puedes visitar estos días.',
    'TEATRO': 'Propuesta de artes escénicas en cartel estos días.',
    'CINE': 'Programación de cine y actividades culturales.',
    'AGENDA INFANTIL': 'Plan pensado para ir con niños.',
    'FESTIVALES': 'Festival en marcha estos días en la ciudad.',
    'FIESTAS': 'Fiesta popular en la ciudad.',
    'OCIO ALTERNATIVO': 'Un plan diferente para estos días.',
    'VISITAS GUIADAS': 'Visita guiada para conocer mejor la ciudad.',
    'RUTAS CULTURALES': 'Ruta cultural para recorrer la ciudad.',
    'MERCADOS': 'Mercado o mercadillo en la ciudad.',
    'TALLERES': 'Talleres y actividades participativas.',
    'JORNADAS': 'Jornadas con actividades abiertas al público.',
    'CONFERENCIAS': 'Charlas y conferencias abiertas al público.',
}

BLOQUES = {
    0: ['<strong>Mercado Central</strong>: abierto de 7:30 a 15:00 (de lunes a sábado).',
        'Ojo: muchos museos <strong>cierran los lunes</strong> (Bellas Artes, Centre del Carme y L’ETNO abren de martes a domingo).',
        'Buen día para un paseo por el <strong>Jardín del Turia</strong> o la playa, y para descubrir planes espontáneos cerca en la app.'],
    1: ['<strong>Mercado Central</strong>: de 7:30 a 15:00.',
        'Museos <strong>gratis</strong> todos los días que abren: <strong>Bellas Artes</strong> (10–20 h), <strong>Centre del Carme</strong> (11–21 h) y <strong>L’ETNO</strong> (10–20 h).',
        'Por la tarde, exposiciones, talleres y actividades en centros culturales.'],
    4: ['<strong>Mercado Central</strong>: de 7:30 a 15:00.',
        'Museos gratis: <strong>Bellas Artes</strong>, <strong>Centre del Carme</strong> y <strong>L’ETNO</strong>.',
        'Por la noche, el inicio del fin de semana: conciertos, teatro y ambiente en Ruzafa, el Carmen y la zona de la playa.'],
    5: ['<strong>Mercado Central</strong>: abierto hasta las 15:00 (el domingo cierra).',
        '<strong>IVAM</strong>: entrada gratuita el sábado por la tarde (15–19 h). <strong>Museo Nacional de Cerámica</strong>: gratis desde las 16:00.',
        'Tardeo y noche: el día con más ambiente para salir.'],
    6: ['<strong>Rastro de València</strong>: domingos y festivos de 9:00 a 14:00, en el parque Amelia Chiner (Av. dels Tarongers).',
        '<strong>Museos municipales gratis</strong> los domingos y festivos: L’Almoina, Museo de la Ciudad, Museo del Arroz, Museo Fallero…',
        '<strong>IVAM</strong> gratis todo el día y <strong>Museo Nacional de Cerámica</strong> gratis de 10 a 14 h. El Mercado Central está cerrado.'],
}
BLOQUES[2] = BLOQUES[1]
BLOQUES[3] = BLOQUES[1][:2] + ['Tarde-noche de jueves: buen día para el tardeo y la música en directo.']


def leer_agenda():
    req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0 (compatible; WannaNowBot/1.0; +https://wannanow.app/)'})
    with urllib.request.urlopen(req, timeout=40) as r:
        t = r.read().decode('utf-8', 'replace')
    i = t.index('var eventosInicio = [') + len('var eventosInicio = ')
    depth = 0
    for j in range(i, len(t)):
        if t[j] == '[':
            depth += 1
        elif t[j] == ']':
            depth -= 1
            if depth == 0:
                break
    return json.loads(t[i:j + 1])


def dia_local(ms):
    return datetime.fromtimestamp(int(ms) / 1000, TZ).date()


def normalizar(evs):
    out = []
    for e in evs:
        try:
            ini = date.fromisoformat(e['startDateSort'])
            fin = dia_local(e['endDate'])
            if fin < ini:
                fin = ini
            out.append({'titulo': e['content'].strip(), 'cat': (e.get('categoria') or '').strip().upper(),
                        'ini': ini.isoformat(), 'fin': fin.isoformat(), 'slug': e['url'].strip()})
        except Exception:
            continue
    return out


def fecha_c(d):
    return f'{d.day} {MESES_C[d.month - 1]}'


def elegir(evs, hoy, textos):
    excl = set(textos.get('_excluir', []))
    cand = []
    for e in evs:
        ini, fin = date.fromisoformat(e['ini']), date.fromisoformat(e['fin'])
        dur = (fin - ini).days
        if not (ini <= hoy <= fin) or dur > 150 or e['slug'] in excl:
            continue
        if re.match(r'^CC ', e['titulo']):
            continue
        cur = 0 if e['slug'] in textos else 1
        cand.append((cur, PRIORIDAD.get(e['cat'], 4), dur, e))
    cand.sort(key=lambda x: (x[0], x[1], x[2]))
    elegidos, cats = [], set()
    for *_, e in cand:
        if e['cat'] in cats and len(cand) > 4:
            continue
        elegidos.append(e)
        cats.add(e['cat'])
        if len(elegidos) == 4:
            break
    return elegidos


def tarjeta(e, hoy, textos):
    ini, fin = date.fromisoformat(e['ini']), date.fromisoformat(e['fin'])
    tag = ''
    if fin == hoy:
        tag = '<span class="tag">Último día</span>'
    elif (fin - hoy).days <= 3:
        tag = '<span class="tag">Últimos días</span>'
    elif ini == hoy:
        tag = '<span class="tag">Empieza hoy</span>'
    rango = f'Del {fecha_c(ini)} al {fecha_c(fin)}' if ini != fin else f'{fecha_c(ini)}'
    texto = textos.get(e['slug']) or FRASE_CAT.get(e['cat'], 'Actividad incluida en la agenda de la ciudad.')
    cat = H.escape(e['cat'].capitalize()) if e['cat'] else 'Agenda'
    titulo = textos.get('_titulos', {}).get(e['slug']) or e['titulo']
    if titulo.isupper():
        titulo = titulo.capitalize()
    return (f'                <article class="reveal"><span class="cat">{cat}</span>'
            f'<h3>{H.escape(titulo)}</h3><p class="fechas">{rango}{tag}</p>'
            f'<p>{texto}</p><a href="{BASE_EVENTO}{e["slug"]}" target="_blank" rel="noopener">Horarios y detalles en valencia.es →</a></article>')


# ─────────── Destacados: planes elegidos por WannaNow (planes-hoy/destacados.json) ───────────
def cargar_destacados(hoy):
    """Planes destacados a mano (p. ej., artistas que publican en WannaNow).
    Cada entrada: id, titulo, titulo_en, cat, cat_en, ini, fin, mostrar_desde (opcional),
    lugar, lugar_en, texto, texto_en, url, url_texto, url_texto_en, excluir_si_titulo (lista).
    Solo salen si hoy está entre mostrar_desde (o ini) y fin."""
    try:
        ds = json.load(open(os.path.join(AQUI, 'destacados.json'), encoding='utf-8'))
    except Exception:
        return []
    out = []
    for d in ds if isinstance(ds, list) else ds.get('destacados', []):
        try:
            ini, fin = date.fromisoformat(d['ini']), date.fromisoformat(d['fin'])
            desde = date.fromisoformat(d.get('mostrar_desde') or d['ini'])
            if desde <= hoy <= fin:
                out.append(d)
        except Exception:
            continue
    return out[:2]


def _tag_dest(d, hoy, en=False):
    ini, fin = date.fromisoformat(d['ini']), date.fromisoformat(d['fin'])
    if hoy < ini:
        return '<span class="tag">' + (('Starts tomorrow' if en else 'Empieza mañana') if (ini - hoy).days == 1 else ('Coming soon' if en else 'Próximamente')) + '</span>'
    if fin == hoy:
        return '<span class="tag">' + ('Last day' if en else 'Último día') + '</span>'
    if ini == hoy:
        return '<span class="tag">' + ('Starts today' if en else 'Empieza hoy') + '</span>'
    return ''


def tarjeta_destacado(d, hoy, en=False):
    ini, fin = date.fromisoformat(d['ini']), date.fromisoformat(d['fin'])
    if en:
        rango = f'{fecha_c_en(ini)} – {fecha_c_en(fin)}' if ini != fin else fecha_c_en(ini)
        titulo, cat, lugar = d.get('titulo_en') or d['titulo'], d.get('cat_en') or d.get('cat', ''), d.get('lugar_en') or d.get('lugar', '')
        texto, enlace = d.get('texto_en') or d['texto'], d.get('url_texto_en') or 'More info and tickets →'
        sello = 'Also on WannaNow'
    else:
        rango = f'Del {fecha_c(ini)} al {fecha_c(fin)}' if ini != fin else fecha_c(ini)
        titulo, cat, lugar = d['titulo'], d.get('cat', ''), d.get('lugar', '')
        texto, enlace = d['texto'], d.get('url_texto') or 'Más información y entradas →'
        sello = 'También en WannaNow'
    lugar_html = f'<p class="fechas">{H.escape(lugar)}</p>' if lugar else ''
    return (f'                <article class="reveal"><span class="cat">{H.escape(cat)} · {sello}</span>'
            f'<h3>{H.escape(titulo)}</h3><p class="fechas">{rango}{_tag_dest(d, hoy, en)}</p>{lugar_html}'
            f'<p>{texto}</p><a href="{H.escape(d["url"])}" target="_blank" rel="noopener">{enlace}</a></article>')


def schema_destacados(ds, en=False):
    """JSON-LD Event para los destacados (datos estructurados de eventos)."""
    if not ds:
        return ''
    items = []
    for d in ds:
        ev = {'@type': 'Event', 'name': (d.get('titulo_en') if en else None) or d['titulo'],
              'startDate': d.get('inicio_iso') or d['ini'], 'endDate': d.get('fin_iso') or d['fin'],
              'eventStatus': 'https://schema.org/EventScheduled',
              'eventAttendanceMode': 'https://schema.org/OfflineEventAttendanceMode',
              'description': re.sub(r'<[^>]+>', '', (d.get('texto_en') if en else None) or d['texto']),
              'url': d['url']}
        if d.get('recinto'):
            ev['location'] = {'@type': 'Place', 'name': d['recinto'], 'address': {'@type': 'PostalAddress',
                              'streetAddress': d.get('direccion', ''), 'addressLocality': 'València',
                              'postalCode': d.get('cp', ''), 'addressCountry': 'ES'}}
        if d.get('artista'):
            ev['performer'] = {'@type': 'Person', 'name': d['artista']}
            ev['organizer'] = {'@type': 'Person', 'name': d['artista'], 'url': d.get('artista_url', d['url'])}
        items.append(ev)
    data = items[0] if len(items) == 1 else items
    return ('\n                <script type="application/ld+json">' + json.dumps(dict({'@context': 'https://schema.org'}, **data) if isinstance(data, dict) else {'@context': 'https://schema.org', '@graph': data}, ensure_ascii=False) + '</script>')


def quitar_duplicados(elegidos, ds):
    claves = [k.lower() for d in ds for k in d.get('excluir_si_titulo', [])]
    return [e for e in elegidos if not any(k in e['titulo'].lower() for k in claves)]


def main():
    hoy = datetime.now(TZ).date()
    if len(sys.argv) > 1:
        hoy = date.fromisoformat(sys.argv[1])
    textos = json.load(open(os.path.join(AQUI, 'textos.json'), encoding='utf-8'))
    cache = os.path.join(AQUI, 'ultimo.json')
    try:
        evs = normalizar(leer_agenda())
        json.dump({'leido': hoy.isoformat(), 'eventos': evs}, open(cache, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        leido = hoy
    except Exception as ex:
        print('Aviso: no se pudo leer la agenda, uso la última lectura:', ex)
        c = json.load(open(cache, encoding='utf-8'))
        evs, leido = c['eventos'], date.fromisoformat(c['leido'])
    elegidos = elegir(evs, hoy, textos)
    destacados = cargar_destacados(hoy)
    if destacados:
        elegidos = quitar_duplicados(elegidos, destacados)[:max(0, 4 - len(destacados))]
    dia = DIAS[hoy.weekday()]
    larga = f'{dia} {hoy.day} de {MESES[hoy.month - 1]}'
    bloque = '                    <ul>\n' + '\n'.join(f'                        <li>{x}</li>' for x in BLOQUES[hoy.weekday()]) + '\n                    </ul>'
    tpl = open(os.path.join(AQUI, 'plantilla.html'), encoding='utf-8').read()
    rep = {
        '{{TITLE}}': f'Planes en Valencia hoy, {larga} | WannaNow',
        '{{DESC}}': f'Qué hacer hoy, {larga}, en Valencia: planes de la agenda de la ciudad, museos y mercados abiertos y lo que pasa ahora en la app WannaNow.',
        '{{LABEL}}': f'Hoy · {larga}',
        '{{DIA}}': dia,
        '{{FECHA_LARGA}}': larga,
        '{{FECHA_CORTA}}': f'Hoy · {dia} {hoy.day} {MESES_C[hoy.month - 1]}',
        '{{FECHA_CORTA_MIN}}': f'{leido.day} de {MESES[leido.month - 1]} de {leido.year}',
        '{{FECHA_ACT}}': f'{larga} de {hoy.year}',
        '{{ISO}}': hoy.isoformat(),
        '{{EVENTOS}}': '\n'.join([tarjeta_destacado(d, hoy) for d in destacados] + [tarjeta(e, hoy, textos) for e in elegidos]) + schema_destacados(destacados) or '                <article><p>Hoy no hay actividades destacadas en la agenda municipal. Mira lo que está pasando ahora en la app.</p></article>',
        '{{BLOQUE_DIA}}': bloque,
    }
    for k, v in rep.items():
        tpl = tpl.replace(k, v)
    os.makedirs(os.path.join(RAIZ, 'planes-valencia-hoy'), exist_ok=True)
    open(os.path.join(RAIZ, 'planes-valencia-hoy', 'index.html'), 'w', encoding='utf-8').write(tpl)
    # sitemap: fecha de modificación de hoy
    sm = os.path.join(RAIZ, 'sitemap.xml')
    if os.path.exists(sm):
        t = open(sm, encoding='utf-8').read()
        t2 = re.sub(r'(<loc>https://wannanow.app/planes-valencia-hoy/</loc>\s*(?:<xhtml:link[^>]*/>\s*)*<lastmod>)[0-9-]+', r'\g<1>' + hoy.isoformat(), t)
        if t2 != t:
            open(sm, 'w', encoding='utf-8').write(t2)
    print(hoy, '|', len(evs), 'actividades leídas |', [e['titulo'] for e in elegidos])
    try:
        generar_en(elegidos, hoy, leido, textos, destacados)
    except Exception as ex:
        print('Aviso: no se pudo generar la versión en inglés:', ex)


# ─────────────────────────── ENGLISH (/en/things-to-do-valencia-today/) ───────────────────────────
DAYS_EN = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
MONTHS_EN = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
             'October', 'November', 'December']
MONTHS_EN_C = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
CAT_EN = {'MÚSICA': 'Music', 'DEPORTES': 'Sport', 'EXPOSICIONES': 'Exhibitions', 'TEATRO': 'Theatre', 'CINE': 'Cinema',
          'AGENDA INFANTIL': 'Kids', 'FESTIVALES': 'Festivals', 'FIESTAS': 'Festivities', 'OCIO ALTERNATIVO': 'Something different',
          'VISITAS GUIADAS': 'Guided tours', 'RUTAS CULTURALES': 'Cultural routes', 'MERCADOS': 'Markets', 'TALLERES': 'Workshops',
          'JORNADAS': 'Talks & meetups', 'CONFERENCIAS': 'Talks', 'ESPECTÁCULOS': 'Shows', 'DANZA': 'Dance', 'CIRCO': 'Circus',
          'FERIAS': 'Fairs', 'ENCUENTROS': 'Meetups', 'MUSEOS MUNICIPALES': 'Museums'}
FRASE_CAT_EN = {
    'MÚSICA': 'Live music as part of the city programme.',
    'DEPORTES': 'Sports activity open to everyone.',
    'EXPOSICIONES': 'An exhibition you can visit these days.',
    'TEATRO': 'Performing arts on stage these days.',
    'CINE': 'Film screenings and cultural activities.',
    'AGENDA INFANTIL': 'A plan to enjoy with kids.',
    'FESTIVALES': 'A festival running in the city these days.',
    'FIESTAS': 'A local festivity in the city.',
    'OCIO ALTERNATIVO': 'Something different to do these days.',
    'VISITAS GUIADAS': 'A guided tour to get to know the city better.',
    'RUTAS CULTURALES': 'A cultural route around the city.',
    'MERCADOS': 'A market in the city.',
    'TALLERES': 'Workshops and hands-on activities.',
    'JORNADAS': 'A programme of activities open to the public.',
    'CONFERENCIAS': 'Talks open to the public.',
}
BLOQUES_EN = {
    0: ['<strong>Mercado Central</strong> (Central Market): open 7:30 am – 3 pm (Monday to Saturday).',
        'Heads-up: many museums <strong>close on Mondays</strong> (the Museo de Bellas Artes, Centre del Carme and L’ETNO open Tuesday to Sunday).',
        'A good day for a walk in the <strong>Turia Gardens</strong> or on the beach — and for finding spontaneous plans nearby in the app.'],
    1: ['<strong>Mercado Central</strong>: 7:30 am – 3 pm.',
        '<strong>Free museums</strong> every day they open: <strong>Museo de Bellas Artes</strong> (10 am – 8 pm), <strong>Centre del Carme</strong> (11 am – 9 pm) and <strong>L’ETNO</strong> (10 am – 8 pm).',
        'In the afternoon: exhibitions, workshops and activities at cultural centres.'],
    4: ['<strong>Mercado Central</strong>: 7:30 am – 3 pm.',
        'Free museums: <strong>Museo de Bellas Artes</strong>, <strong>Centre del Carme</strong> and <strong>L’ETNO</strong>.',
        'At night the weekend kicks off: concerts, theatre and nightlife in Ruzafa, El Carmen and by the beach.'],
    5: ['<strong>Mercado Central</strong>: open until 3 pm (closed on Sundays).',
        '<strong>IVAM</strong>: free entry on Saturday afternoon (3 – 7 pm). <strong>National Ceramics Museum</strong>: free from 4 pm.',
        'Afternoon drinks and nightlife: the liveliest day to go out.'],
    6: ['<strong>Rastro de València</strong> flea market: Sundays and public holidays, 9 am – 2 pm, at Parque Amelia Chiner (Av. dels Tarongers).',
        '<strong>Free municipal museums</strong> on Sundays and public holidays: L’Almoina, the City Museum, the Rice Museum, the Fallas Museum…',
        '<strong>IVAM</strong> free all day and the <strong>National Ceramics Museum</strong> free from 10 am to 2 pm. The Mercado Central is closed.'],
}
BLOQUES_EN[2] = BLOQUES_EN[1]
BLOQUES_EN[3] = BLOQUES_EN[1][:2] + ['Thursday evening: a good day for afternoon drinks and live music.']


def fecha_c_en(d):
    return f'{d.day} {MONTHS_EN_C[d.month - 1]}'


def tarjeta_en(e, hoy, t_en, t_es):
    ini, fin = date.fromisoformat(e['ini']), date.fromisoformat(e['fin'])
    tag = ''
    if fin == hoy:
        tag = '<span class="tag">Last day</span>'
    elif (fin - hoy).days <= 3:
        tag = '<span class="tag">Last few days</span>'
    elif ini == hoy:
        tag = '<span class="tag">Starts today</span>'
    rango = f'{fecha_c_en(ini)} – {fecha_c_en(fin)}' if ini != fin else fecha_c_en(ini)
    texto = t_en.get(e['slug']) or FRASE_CAT_EN.get(e['cat'], 'An activity from the city agenda.')
    cat = H.escape(CAT_EN.get(e['cat'], e['cat'].capitalize() if e['cat'] else 'Agenda'))
    titulo = t_en.get('_titulos', {}).get(e['slug']) or t_es.get('_titulos', {}).get(e['slug']) or e['titulo']
    if titulo.isupper():
        titulo = titulo.capitalize()
    return (f'                <article class="reveal"><span class="cat">{cat}</span>'
            f'<h3>{H.escape(titulo)}</h3><p class="fechas">{rango}{tag}</p>'
            f'<p>{texto}</p><a href="{BASE_EVENTO}{e["slug"]}" target="_blank" rel="noopener" hreflang="es">Times and details on valencia.es (in Spanish) →</a></article>')


def generar_en(elegidos, hoy, leido, textos, destacados=()):
    tpl_path = os.path.join(AQUI, 'plantilla_en.html')
    if not os.path.exists(tpl_path):
        return
    try:
        t_en = json.load(open(os.path.join(AQUI, 'textos_en.json'), encoding='utf-8'))
    except Exception:
        t_en = {}
    day = DAYS_EN[hoy.weekday()]
    larga = f'{day} {hoy.day} {MONTHS_EN[hoy.month - 1]}'
    bloque = '                    <ul>\n' + '\n'.join(f'                        <li>{x}</li>' for x in BLOQUES_EN[hoy.weekday()]) + '\n                    </ul>'
    tpl = open(tpl_path, encoding='utf-8').read()
    rep = {
        '{{TITLE}}': f'Things to do in Valencia today, {larga} | WannaNow',
        '{{DESC}}': f'What to do in Valencia today, {larga}: picks from the city agenda, free museums and markets open today, and what\'s on right now in the WannaNow app.',
        '{{LABEL}}': f'Today · {larga}',
        '{{DIA}}': day,
        '{{FECHA_LARGA}}': larga,
        '{{FECHA_CORTA}}': f'Today · {day[:3]} {hoy.day} {MONTHS_EN_C[hoy.month - 1]}',
        '{{FECHA_CORTA_MIN}}': f'{leido.day} {MONTHS_EN[leido.month - 1]} {leido.year}',
        '{{FECHA_ACT}}': f'{larga} {hoy.year}',
        '{{ISO}}': hoy.isoformat(),
        '{{EVENTOS}}': '\n'.join([tarjeta_destacado(d, hoy, en=True) for d in destacados] + [tarjeta_en(e, hoy, t_en, textos) for e in elegidos]) + schema_destacados(destacados, en=True) or '                <article><p>No highlights in the city agenda today. See what\'s happening right now in the app.</p></article>',
        '{{BLOQUE_DIA}}': bloque,
    }
    for k, v in rep.items():
        tpl = tpl.replace(k, v)
    out = os.path.join(RAIZ, 'en', 'things-to-do-valencia-today')
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, 'index.html'), 'w', encoding='utf-8').write(tpl)
    sm = os.path.join(RAIZ, 'sitemap.xml')
    if os.path.exists(sm):
        t = open(sm, encoding='utf-8').read()
        t2 = re.sub(r'(<loc>https://wannanow.app/en/things-to-do-valencia-today/</loc>\s*(?:<xhtml:link[^>]*/>\s*)*<lastmod>)[0-9-]+', r'\g<1>' + hoy.isoformat(), t)
        if t2 != t:
            open(sm, 'w', encoding='utf-8').write(t2)
    print('EN ok')


if __name__ == '__main__':
    main()
