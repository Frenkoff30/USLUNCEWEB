# -*- coding: utf-8 -*-
"""Poskládá statické stránky webu U Slunce ze společné kostry.

Hlavička, patička a světelný rám jsou na všech stránkách stejné, takže je
drží jedno místo a nemůžou se rozejít. Výstupem jsou hotové .html soubory,
web nepotřebuje na serveru žádný build.

Spuštění ze složky web:  python build-stranky.py
"""
import io
import os

SITE = 'https://www.penzionuslunce.cz/'
TEL_R = '+420389822499'
TEL_P = '+420389822493'
MAIL = 'lebrasynove@seznam.cz'

# razítko za odkazy na styl a skript, aby si prohlížeč po úpravě načetl novou verzi
ASSET_V = '25'

PAGES = [
    ('index.html', 'Domů'),
    ('restaurace.html', 'Restaurace'),
    ('listek.html', 'Lístek'),
    ('ubytovani.html', 'Ubytování'),
    ('kontakt.html', 'Kontakt'),
]

MOBILE_LABELS = {'listek.html': 'Jídelní a nápojový lístek'}


def icon(paths, width='1.8'):
    return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="%s" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">%s</svg>' % (width, paths))


I_PHONE = icon('<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 '
               '2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 '
               '6 6l1.3-1.2a2 2 0 0 1 2.1-.5c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/>')
I_MAIL = icon('<rect x="2" y="4" width="20" height="16" rx="2"/><path d="M22 6l-10 7L2 6"/>')
I_KEY = icon('<circle cx="8" cy="15" r="4"/><path d="M10.9 12.1L21 2M18 5l2 2M15 8l2 2"/>')
I_PIN = icon('<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>')
I_ARROW = icon('<path d="M5 12h14M13 6l6 6-6 6"/>', '2')
I_CHEVRON = icon('<path d="M9 18l6-6-6-6"/>', '2.4')
I_CHECK = icon('<path d="M20 6L9 17l-5-5"/>', '2.2')
I_CARET = icon('<path d="M6 9l6 6 6-6"/>', '2')
I_CLOSE = icon('<path d="M18 6L6 18M6 6l12 12"/>', '2')
I_PREV = icon('<path d="M15 18l-6-6 6-6"/>', '2')
I_NEXT = icon('<path d="M9 18l6-6-6-6"/>', '2')

DECO = '<div class="deco" aria-hidden="true"><div class="deco__sun"></div></div>'


def sep(color, shape=''):
    """Barevný přechod mezi sekcemi. Barva je vždy ta, ze které se odchází."""
    return '    <div class="sep sep--%s%s" aria-hidden="true"></div>\n' % (
        color, ' sep--' + shape if shape else '')


def photo(name, alt, small=False, sizes=None):
    """Fotky mají 640 na 480 bodů, menší varianta 480 na 360. Nikde se nezvětšují."""
    base = 'assets/photos/%s' % name
    if small:
        return ('<img src="%s-sm.webp" srcset="%s-sm.webp 480w, %s.webp 640w" sizes="%s" '
                'alt="%s" width="480" height="360" loading="lazy">'
                % (base, base, base, sizes or '33vw', alt))
    return '<img src="%s.webp" alt="%s" width="640" height="480" loading="lazy">' % (base, alt)


def head(title, desc, canonical, extra=''):
    url = SITE + ('' if canonical == 'index.html' else canonical)
    return '''<!DOCTYPE html>
<html lang="cs">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#7d1710">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:locale" content="cs_CZ">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{site}assets/photos/fasada.webp">
<link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Karla:wght@400;500;600;700&family=Playfair+Display:ital,wght@0,400;0,500;0,600;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/style.css?v={v}">
{extra}</head>
<body>
<a class="skip" href="#main">Přeskočit na obsah</a>
<div class="progress" aria-hidden="true"></div>
'''.format(title=title, desc=desc, url=url, site=SITE, v=ASSET_V, extra=extra)


def header(current):
    nav = '\n'.join(
        '      <a class="nav__link" href="%s"%s>%s</a>' % (
            href, ' aria-current="page"' if href == current else '', label)
        for href, label in PAGES)
    mob = '\n'.join(
        '  <a href="%s"%s>%s</a>' % (
            href, ' aria-current="page"' if href == current else '', MOBILE_LABELS.get(href, label))
        for href, label in PAGES)
    return '''<header class="header">
  <div class="wrap header__inner">
    <a class="brand" href="index.html" aria-label="U Slunce, domovská stránka">
      <span class="sunmark" aria-hidden="true"></span>
      <span class="brand__text">
        <span class="brand__name">U Slunce</span>
        <span class="brand__sub">Třeboň</span>
      </span>
    </a>

    <nav class="nav" aria-label="Hlavní navigace">
%s
    </nav>


    <button class="burger" aria-expanded="false" aria-controls="mobile-nav" aria-label="Otevřít menu">
      <span></span><span></span><span></span>
    </button>
  </div>
</header>

<div class="mobile-nav" id="mobile-nav">
%s
  <div class="mobile-nav__foot">
    <a class="btn btn--primary" href="tel:%s">Rezervace stolu</a>
    <a class="btn btn--ghost" href="tel:%s">Rezervace ubytování</a>
  </div>
</div>
''' % (nav, mob, TEL_R, TEL_P)


def footer(from_color, shape=''):
    return '''<footer class="footer">
%s  %s
  <div class="wrap">
    <div class="footer__grid">
      <div>
        <div class="brand">
          <span class="sunmark" aria-hidden="true"></span>
          <span class="brand__text">
            <span class="brand__name">U Slunce</span>
            <span class="brand__sub">Třeboň</span>
          </span>
        </div>
        <p class="footer__about">Restaurace a penzion v klidné vilové čtvrti na předměstí Třeboně,
          kousek od lázní i rybníka Svět.</p>
      </div>

      <div>
        <h4>Stránky</h4>
        <ul>
          <li><a href="restaurace.html">Restaurace</a></li>
          <li><a href="listek.html">Jídelní lístek</a></li>
          <li><a href="listek.html#napoje">Nápojový lístek</a></li>
          <li><a href="ubytovani.html">Ubytování</a></li>
        </ul>
      </div>

      <div>
        <h4>Otevřeno</h4>
        <ul class="stack">
          <li>Neděle až čtvrtek<br>10.00 až 22.00</li>
          <li>Pátek a sobota<br>10.00 až 23.00</li>
        </ul>
      </div>

      <div>
        <h4>Kontakt</h4>
        <ul class="stack">
          <li>Riegrova 1251<br>379 01 Třeboň</li>
          <li><a href="tel:{tel_r}">Restaurace 389 822 499</a></li>
          <li><a href="tel:{tel_p}">Penzion 389 822 493</a></li>
          <li><a href="mailto:{mail}">{mail}</a></li>
        </ul>
      </div>
    </div>

    <div class="footer__bottom">
      <span>Penzion U Slunce, všechna práva vyhrazena</span>
      <span>IČ 25183800</span>
      <span>Web vytvořilo <a href="https://www.webostudio.cz/" target="_blank" rel="noopener">Webo Studio</a></span>
    </div>
  </div>
</footer>

<a class="btn btn--primary call-fab" href="tel:{tel_r}">{phone} Zavolat a rezervovat</a>
'''.replace('{tel_r}', TEL_R).replace('{tel_p}', TEL_P).replace('{mail}', MAIL).replace(
        '{phone}', I_PHONE) % (sep(from_color, shape), DECO)


LIGHTBOX = '''
<div class="lightbox" role="dialog" aria-modal="true" aria-label="Zvětšená fotografie">
  <button class="lightbox__close" aria-label="Zavřít">%s</button>
  <button class="lightbox__prev" aria-label="Předchozí fotografie">%s</button>
  <button class="lightbox__next" aria-label="Další fotografie">%s</button>
  <div>
    <img alt="">
    <p class="lightbox__caption"><span></span><span class="lightbox__count"></span></p>
  </div>
</div>
''' % (I_CLOSE, I_PREV, I_NEXT)

SCRIPT = '\n<script src="assets/js/main.js?v=%s" defer></script>\n</body>\n</html>\n' % ASSET_V


def page_hero(title, lead, crumb):
    return '''  <section class="page-hero">
    %s
    <div class="wrap">
      <nav class="crumbs" aria-label="Drobečková navigace">
        <a href="index.html">Domů</a>
        %s
        <span>%s</span>
      </nav>
      <h1>%s</h1>
      <p class="lead">%s</p>
    </div>
  </section>
''' % (DECO, I_CHEVRON, crumb, title, lead)


def band(quote, by, from_color, shape='', pic=None):
    media = ''
    if pic:
        media = '    <div class="band__media" aria-hidden="true">%s</div>\n' % photo(pic[0], pic[1])
    return '''  <section class="band">
%s%s%s
    <div class="wrap">
      <p class="band__quote">%s</p>
      <p class="band__by">%s</p>
    </div>
  </section>
''' % (sep(from_color, shape), media, '' if pic else '    ' + DECO, quote, by)


def callout(h, p, from_color, shape=''):
    return '''  <section class="section section--band section--tight">
%s    %s
    <div class="wrap">
      <div class="callout" data-reveal>
        <h2>%s</h2>
        <p>%s</p>
        <div class="btn-row">
          <a class="btn btn--gold" href="tel:%s">Restaurace 389 822 499</a>
          <a class="btn btn--light" href="tel:%s">Penzion 389 822 493</a>
        </div>
      </div>
    </div>
  </section>
''' % (sep(from_color, shape), DECO, h, p, TEL_R, TEL_P)


def info_list(items, variant=''):
    out = '      <ul class="info%s" data-reveal>\n' % (' ' + variant if variant else '')
    for name, note in items:
        out += '        <li><strong>%s</strong><span>%s</span></li>\n' % (name, note)
    return out + '      </ul>\n'


# ============================================================== Úvodní strana
SCHEMA = '''<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Restaurant",
  "name": "Restaurace a penzion U Slunce",
  "servesCuisine": "Česká kuchyně",
  "url": "%s",
  "telephone": "%s",
  "email": "%s",
  "image": "%sassets/photos/fasada.webp",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "Riegrova 1251",
    "addressLocality": "Třeboň",
    "postalCode": "379 01",
    "addressCountry": "CZ"
  },
  "openingHoursSpecification": [
    { "@type": "OpeningHoursSpecification", "dayOfWeek": ["Sunday","Monday","Tuesday","Wednesday","Thursday"], "opens": "10:00", "closes": "22:00" },
    { "@type": "OpeningHoursSpecification", "dayOfWeek": ["Friday","Saturday"], "opens": "10:00", "closes": "23:00" }
  ]
}
</script>
''' % (SITE, TEL_R, MAIL, SITE)

TILES = [
    ('kuchyne-provoz', 'Kuchyň restaurace při přípravě jídel', 'Kuchyně',
     'Česká klasika, minutky, hotová jídla a ryby z okolních rybníků.',
     'restaurace.html', 'Poznat restauraci'),
    ('bar', 'Dřevěný bar restaurace s výčepem a barovými židlemi', 'Bar',
     'Točený Bernard a Regent, lahvové speciály, vína, rumy a whisky.',
     'listek.html#napoje', 'Nápojový lístek'),
    ('pokoj-s-terasou', 'Dvoulůžkový pokoj s prosklenými dveřmi na balkon', 'Penzion',
     'Pokoje a apartmány s klimatizací, kuchyňkou a vlastní koupelnou.',
     'ubytovani.html', 'Ubytování a ceny'),
]

def build_index():
    tiles = ''
    for i, (name, alt, h, p, href, label) in enumerate(TILES, 1):
        tiles += '''        <article class="tile" data-reveal>
          <div class="tile__media">%s</div>
          <span class="tile__no" aria-hidden="true">0%d</span>
          <div class="tile__body">
            <h3>%s</h3>
            <p>%s</p>
            <a class="arrow-link" href="%s">%s %s</a>
          </div>
        </article>
''' % (photo(name, alt), i, h, p, href, label, I_ARROW)

    body = '''<main id="main">

  <section class="hero">
    <div class="hero__media">
      <picture>
        <source media="(max-width: 700px)" srcset="assets/photos/hero-uvod-uzky.webp?v=%s" width="800" height="1598">
        <img src="assets/photos/hero-uvod.webp?v=%s" alt="Průčelí restaurace a penzionu U Slunce v Třeboni s cedulemi Restaurace a Pension" width="1800" height="1012" fetchpriority="high" decoding="async">
      </picture>
    </div>

    <div class="hero__panel">
      <div class="deco__sun" aria-hidden="true"></div>
      <div class="hero__inner">
      <h1 class="hero__title">U Slunce</h1>
      <div class="btn-row">
        <a class="btn btn--gold" href="tel:%s">Rezervovat stůl</a>
        <a class="btn btn--light" href="ubytovani.html">Ubytování</a>
        </div>
      </div>
    </div>

    <div class="hero__bar">
      <div class="wrap hero__bar-in">
        <span data-open>
          <span class="hero__dot" aria-hidden="true"></span>
          <b>Dnes</b> <span data-open-text>10.00 až 22.00</span>
        </span>
        <span>%s Riegrova 1251, Třeboň</span>
        <a href="tel:%s">%s 389 822 499</a>
      </div>
    </div>
  </section>

  <section class="section" id="uvod">
%s    <div class="wrap split">
      <div class="flow" data-reveal>
        <h2>Rodinné místo na předměstí lázeňské Třeboně</h2>
        <p class="lead">
          Restaurace se stylovým barem a penzion pod jednou střechou. Vlastní klidný
          areál stranou ruchu, a přesto deset minut pěšky do centra.
        </p>
        <div class="arrow-row">
          <a class="arrow-link" href="restaurace.html">Více o restauraci %s</a>
        </div>
      </div>
      <div class="stack-media" data-reveal data-delay>
        <div class="stack-media__main" data-reveal-img>
          %s
        </div>
        <div class="stack-media__inset">
          %s
        </div>
      </div>
    </div>
  </section>

  <section class="section section--paper">
%s    <div class="wrap">
      <div class="section-head is-centered" data-reveal>
        <h2>Jedno místo, tři důvody se zastavit</h2>
      </div>
      <div class="cards cards--3" data-reveal-group>
%s      </div>
    </div>
  </section>

%s</main>
''' % (ASSET_V, ASSET_V, TEL_R, I_PIN, TEL_R, I_PHONE,
       sep('band'), I_ARROW,
       photo('fasada', 'Fasáda domu s nápisy Restaurace a Pension'),
       photo('znak-slunce', 'Kovaný znak slunce nad vchodem do penzionu'),
       sep('white', 'wave2'), tiles,
       callout('Rezervace stolu i pokoje',
               'Stůl i pokoj domluvíme po telefonu. Rádi poradíme, co v Třeboni stihnout.',
               'paper', 'wave3'))

    return (head('Restaurace a penzion U Slunce, Třeboň',
                 'Restaurace a penzion U Slunce v Třeboni. Česká kuchyně, čerstvé ryby z třeboňských '
                 'rybníků, pivo Bernard a klidné ubytování s parkováním v areálu.',
                 'index.html', SCHEMA)
            + header('index.html') + body + footer('band', 'wave3') + LIGHTBOX + SCRIPT)


# ================================================================ Restaurace
def build_restaurace():
    body = """<main id="main">

%s
  <section class="section">
%s    <div class="wrap split">
      <div class="flow" data-reveal>
        <h2>Vaříme tak, jak to má být</h2>
        <p class="lead">
          Česká klasika, minutky a ryby z třeboňských rybníků. Kdo spěchá, vybere si
          z denní nabídky hotových jídel.
        </p>
        <p class="muted">
          Místa je dost i na oslavu, promoci nebo firemní setkání. Termín domluvíme po telefonu.
        </p>
        <div class="btn-row">
          <a class="btn btn--dark" href="listek.html">Jídelní lístek</a>
          <a class="btn btn--ghost" href="tel:%s">Rezervovat stůl</a>
        </div>
      </div>
      <div class="stack-media" data-reveal data-delay>
        <div class="stack-media__main" data-reveal-img>
          %s
        </div>
        <div class="stack-media__inset">
          %s
        </div>
      </div>
    </div>
  </section>

  <section class="section section--paper">
%s    <div class="wrap split split--reverse">
      <div class="split__media" data-reveal data-reveal-img>
        %s
      </div>
      <div class="flow" data-reveal data-delay>
        <h2>Bar, kde má pivo správnou pěnu</h2>
        <p class="lead">
          Bernard ve světlé jedenáctce, nefiltrované i polotmavé dvanáctce a třeboňský
          Regent. K tomu vína, rumy, whisky a lahvové speciály, které se během roku obměňují.
        </p>
        <div class="arrow-row">
          <a class="arrow-link" href="listek.html#napoje">Nápojový lístek %s</a>
        </div>
      </div>
    </div>
  </section>

  <section class="section">
%s    <div class="wrap split">
      <div class="split__media" data-reveal data-reveal-img>
        %s
      </div>
      <div class="flow" data-reveal data-delay>
        <h2>Zahrádka ve stínu pergoly</h2>
        <p class="lead">
          Klidný dvorek s dřevěnou terasou, květinami a stínící markýzou.
        </p>
        <ul class="checklist">
          <li>%s Zastřešená terasa, posedíte i za deště</li>
          <li>%s Dětský koutek s domečkem přímo na terase</li>
          <li>%s Uvnitř i venku platí stejný lístek</li>
        </ul>
      </div>
    </div>
  </section>
</main>
""" % (page_hero('Restaurace',
                 'Klidné posezení nedaleko centra Třeboně. Česká klasika, minutky a rybí speciality.',
                 'Restaurace'),
       sep('sand'), TEL_R,
       photo('jidlo-pstruh', 'Pečený pstruh se zeleninou na talíři'),
       photo('restaurace-interier', 'Interiér restaurace s obrazy a zelenými lavicemi'),
       sep('white', 'wave2'),
       photo('bar', 'Dřevěný bar restaurace s výčepem a barovými židlemi'),
       I_ARROW,
       sep('paper', 'wave4'),
       photo('zahradka-pergola', 'Krytá zahrádka se stoly pod pergolou'),
       I_CHECK, I_CHECK, I_CHECK)

    return (head('Restaurace U Slunce, Třeboň',
                 'Restaurace U Slunce v Třeboni. Česká kuchyně, minutky, hotová jídla a čerstvé ryby '
                 'z třeboňských rybníků. Stylový bar s pivem Bernard.',
                 'restaurace.html')
            + header('restaurace.html') + body + footer('white', 'wave5') + SCRIPT)


# ==================================================================== Lístek
JIDLO = [
    ('Předkrmy', ['Rybí terinka, bageta', 'Líčka z candáta na česneku, bageta', 'Vepřová paštika, chléb']),
    ('Polévky', ['Rybí s krutony', 'Silný slepičí vývar s masem a nudlemi']),
    ('Hlavní jídla', ['Candát na másle', 'Kapr filet na slanině s česnekem', 'Kapří hranolky, česnekový dip',
                      'Vepřová panenka s demi glace omáčkou', 'Steak z krkovice s vídeňskou omáčkou',
                      'Řízečky z vepřové panenky', 'Vepřová játra po anglicku',
                      'Grilované kuřecí prso s tymiánem', 'Kuřecí řízek', 'Smažený sýr Gouda']),
    ('Přílohy', ['Hranolky', 'Pažitkové brambory', 'Domácí bramborový salát s majonézou',
                 'Farmářská zelenina', 'Řemeslný chléb']),
    ('Dezerty', ['Zmrzlina dle nabídky', 'Ovocný sorbet s jahodami', 'Ovocná panna cotta']),
]

NAPOJE = [
    ('Káva a čokoláda', ['Káva turecká', 'Espresso', 'Káva bez kofeinu', 'Caffé Latté', 'Cappuccino',
                         'Káva vídeňská', 'Káva alžírská', 'Káva irská', 'Horká čokoláda', 'Grog',
                         'Svařené víno']),
    ('Čaje z konvičky', ['Assam', 'Earl Grey', 'Zelený Asia', 'Lesní plody', 'Vita orange',
                         'Bylinková zahrada', 'Mátový', 'Med, porce']),
    ('Nealkoholické nápoje', ['Coca-Cola a Coca-Cola light', 'Sprite', 'Fanta', 'Kinley tonic',
                              'Bonaqua neperlivá, jemně perlivá a perlivá', 'Točená limonáda', 'Red Bull']),
    ('Džusy', ['Pomeranč', 'Jablko', 'Černý rybíz', 'Jahoda', 'Mango']),
    ('Pivo točené', ['Bernard světlý 11°', 'Bernard nefiltrovaný 12°', 'Bernard polotmavý 12°',
                     'Regent světlý 12°']),
    ('Pivo nealkoholické', ['Bernard free', 'Bernard free švestka']),
    ('Víno a sekty', ['Rozlévané víno', 'Víno dle nabídky', 'Bohemia Demi-Sec', 'Bohemia Regia Brut',
                      'Chateau Radyně', 'Bohemia nealko', 'Moët &amp; Chandon']),
    ('Aperitivy', ['Martini Dry, Bianco, Rosso', 'Campari Bitter', 'Portské', 'Portské 10 let']),
    ('Destiláty', ['Tuzemák', 'Vodka Amundsen', 'Gin Beefeater', "Gin Hendrick's", 'Gin Roku', 'Slivovice',
                   'Hruškovice', 'Calvados', 'Mandlovka z Hustopečí']),
    ('Likéry', ['Fernet Stock a Fernet Stock citrus', 'Becherovka', 'Peprmintka', 'Vaječný likér',
                'Jägermeister', 'Sambuca', 'Griotka', 'Baileys']),
    ('Whisky', ['Jameson', 'Jameson 12 let', 'Tullamore Dew', 'Laphroaig 10 let',
                "Jack Daniel's, Honey, Single", 'Jim Beam', 'Chivas Regal', "Grant's", 'Johnnie Walker']),
    ('Brandy a cognac', ['Metaxa 3, 5, 7 a 12 hvězdiček', 'Rémy Martin V.S.O.P.', 'Courvoisier V.S.',
                         'Courvoisier V.S.O.P.', 'Courvoisier X.O. Imperial', 'Godet Pearadise']),
    ('Rumy', ['Arehucas', 'Captain Morgan', 'Havana Club, Especial, Reserva a 7 let', 'Blackwell',
              'Diplomático 8 a 12 let', 'Diplomático single vintage', 'Millonario 15 let', 'Don Papa',
              'Zaya', 'Zacapa 23 let', 'Božkov Republica', 'Bacardi', 'Legendario 7 let']),
    ('Dezerty a pochutiny', ['Zmrzlina, porce', 'Horké ovoce', 'Ledová káva se zmrzlinou a šlehačkou',
                             'Pohár Tiramisu se šlehačkou', 'Arašídy', 'Pražené mandličky',
                             'Smažené chipsy s rajčatovou a sýrovou omáčkou']),
]

ALERGENY = [
    'Obiloviny obsahující lepek a výrobky z nich', 'Korýši a výrobky z nich', 'Vejce a výrobky z nich',
    'Ryby a výrobky z nich', 'Podzemnice olejná neboli arašídy a výrobky z nich',
    'Sójové boby a výrobky z nich', 'Mléko a výrobky z něj',
    'Skořápkové plody, tedy všechny druhy ořechů', 'Celer a výrobky z něj', 'Hořčice a výrobky z ní',
    'Sezamová semena a výrobky z nich',
    'Oxid siřičitý a siřičitany v koncentracích vyšších než 10 mg na kilogram nebo litr',
    'Vlčí bob neboli lupina a výrobky z něj', 'Měkkýši a výrobky z nich',
]


def menu_columns(groups):
    out = '          <div class="menu-columns">\n'
    for title, items in groups:
        out += '            <div class="menu-group">\n'
        out += '              <h3 class="menu-group__title">%s</h3>\n              <ul>\n' % title
        for it in items:
            out += '                <li>%s</li>\n' % it
        out += '              </ul>\n            </div>\n'
    return out + '          </div>\n'


def build_listek():
    alerg = '\n'.join('            <li><span>%s</span></li>' % a for a in ALERGENY)
    body = '''<main id="main">

%s
  <section class="section">
%s    <div class="wrap">
      <div data-tabs data-reveal id="listek">
        <div class="menu-tabs" id="napoje" role="tablist" aria-label="Výběr lístku">
          <button role="tab" id="tab-jidlo" data-hash="jidlo" aria-controls="panel-jidlo" aria-selected="true" tabindex="0">Jídelní lístek</button>
          <button role="tab" id="tab-napoje" data-hash="napoje" aria-controls="panel-napoje" aria-selected="false" tabindex="-1">Nápojový lístek</button>
        </div>

        <div class="menu-panel" id="panel-jidlo" role="tabpanel" aria-labelledby="tab-jidlo">
%s          <div class="menu-note">
            Nabídku hotových jídel připravujeme každý den čerstvou. Ceny najdete v tištěném
            lístku na stole, u sezonních surovin se totiž mění.
          </div>
        </div>

        <div class="menu-panel" id="panel-napoje" role="tabpanel" aria-labelledby="tab-napoje" hidden>
%s          <div class="menu-note">
            Kromě čepovaných piv máme i velké množství zahraničních lahvových speciálů,
            které se v průběhu roku obměňují. Zeptejte se u baru.
          </div>
        </div>
      </div>
    </div>
  </section>

  <section class="section section--paper section--tight" id="alergeny">
%s    <div class="wrap wrap--narrow">
      <details class="accordion" data-reveal>
        <summary>Seznam potravinových alergenů %s</summary>
        <div class="accordion__body">
          <p>Označování podle směrnice 1169/2011 Evropské unie.</p>
          <ol>
%s
          </ol>
          <p>Všechna zde podávaná jídla a nápoje mohou obsahovat tyto alergeny
            a jejich stopové prvky. Protože nemůžeme převzít plnou odpovědnost za výrobce základních
            surovin, nejsou vhodná pro alergiky.</p>
        </div>
      </details>
    </div>
  </section>

</main>
''' % (page_hero('Jídelní a nápojový lístek',
                 'Výběr ze stálé nabídky. Denní menu a sezonní speciality vám rádi řekneme po telefonu.',
                 'Lístek'),
       sep('sand'), menu_columns(JIDLO), menu_columns(NAPOJE),
       sep('white', 'wave4'), I_CARET, alerg)

    return (head('Jídelní a nápojový lístek, U Slunce Třeboň',
                 'Jídelní a nápojový lístek restaurace U Slunce v Třeboni. Česká kuchyně, ryby, '
                 'pivo Bernard a Regent, vína, rumy a whisky. Seznam alergenů.',
                 'listek.html')
            + header('listek.html') + body + footer('paper', 'wave3') + SCRIPT)


# ================================================================= Ubytování
ROOMS = [
    ('Jednolůžkový pokoj', 'Bez kuchyňského koutu', '1 250', '1 100', False),
    ('Jednolůžkový pokoj', 'S kuchyňským koutem', '1 400', '1 300', False),
    ('Dvoulůžkový pokoj', 'Možnost přistýlky, část s terasou', '2 200', '1 700', True),
    ('Třílůžkový pokoj', 'Vhodný pro rodinu i partu', '3 300', '2 550', False),
    ('Čtyřlůžkový apartmán', 'Dvě oddělené ložnice', '4 400', '3 400', False),
    ('Přistýlka', 'K dvoulůžkovému pokoji', '600', '600', False),
]

VYBAVENI = [
    ('Klimatizace', 'Ve všech pokojích'),
    ('Wifi', 'V celém areálu'),
    ('Kuchyňský kout', 'Lednice, mikrovlnná trouba a konvice'),
    ('Vlastní koupelna', 'Se sprchovým koutem, televize na pokoji'),
    ('Parkování', 'Uzavřené, přímo u domu, bez příplatku'),
    ('Kolárna', 'Úschova kol a nabíjení elektrokol'),
]

OKOLI = [
    ('Lázně Aurora', 'Pět minut chůze, bazény, sauny i tobogán'),
    ('Rybník Svět', 'Naučná stezka kolem dokola, pět minut'),
    ('Historické centrum', 'Zámek, Schwarzenberská hrobka a náměstí, deset minut'),
    ('Lázně Berta', 'Deset minut chůze přes park'),
    ('Cyklotrasy Třeboňska', 'Ptačí rezervace Velký a Malý Tisý'),
    ('Gmünd v Rakousku', 'Aquapark 32 kilometrů za hranicí'),
]

# jemná galerie pod ubytováním, samostatnou stránku už web nemá
POKOJE = [
    ('pokoj-podkrovni', 'Podkrovní pokoj s posezením u střešního okna'),
    ('pokoj-s-terasou', 'Dvoulůžkový pokoj s prosklenými dveřmi na balkon'),
    ('apartman', 'Apartmán s obytnou částí a jídelním stolem'),
    ('kuchynka', 'Kuchyňský kout s lednicí a mikrovlnnou troubou'),
    ('koupelna', 'Koupelna se sprchovým koutem'),
    ('chodba', 'Chodba penzionu s výzdobou'),
]

SCHEMA_UB = '''<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "LodgingBusiness",
  "name": "Penzion U Slunce",
  "url": "%subytovani.html",
  "telephone": "%s",
  "email": "%s",
  "image": "%sassets/photos/areal-budova.webp",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "Riegrova 1251",
    "addressLocality": "Třeboň",
    "postalCode": "379 01",
    "addressCountry": "CZ"
  },
  "amenityFeature": [
    { "@type": "LocationFeatureSpecification", "name": "Klimatizace", "value": true },
    { "@type": "LocationFeatureSpecification", "name": "Wifi zdarma", "value": true },
    { "@type": "LocationFeatureSpecification", "name": "Parkování v areálu", "value": true }
  ],
  "petsAllowed": false
}
</script>
''' % (SITE, TEL_P, MAIL, SITE)


def build_ubytovani():
    rooms = ''
    for name, meta, main, off, accent in ROOMS:
        rooms += '''        <article class="room%s" data-reveal data-price-main="%s" data-price-off="%s">
          <h3 class="room__name">%s</h3>
          <p class="room__meta">%s</p>
          <p class="room__price"><span class="room__amount">%s</span><span class="room__unit">Kč za noc</span></p>
        </article>
''' % (' room--accent' if accent else '', main, off, name, meta, main)

    fotky = ''
    for name, alt in POKOJE:
        fotky += '''        <figure class="gallery__item" data-lightbox data-full="assets/photos/%s.webp" tabindex="0" role="button" aria-label="Zvětšit fotografii, %s" data-reveal>
          %s
          <figcaption>%s</figcaption>
        </figure>
''' % (name, alt, photo(name, alt, small=True,
                            sizes='(max-width:620px) 92vw, (max-width:940px) 46vw, 31vw'), alt)

    body = '''<main id="main">

%s
  <section class="section">
%s    <div class="wrap split">
      <div class="flow" data-reveal>
        <h2>Klid vilové čtvrti, centrum na dohled</h2>
        <p class="lead">
          Pokoje a apartmány v areálu i nad restaurací, sedm z nich s vlastním balkonem.
          Vilová čtvrť na předměstí, klid zaručený.
        </p>
        <div class="btn-row">
          <a class="btn btn--dark" href="tel:%s">Rezervovat pokoj</a>
          <a class="btn btn--ghost" href="#fotky">Prohlédnout pokoje</a>
        </div>
      </div>
      <div class="stack-media" data-reveal data-delay>
        <div class="stack-media__main" data-reveal-img>
          %s
        </div>
        <div class="stack-media__inset">
          %s
        </div>
      </div>
    </div>
  </section>

  <section class="section section--paper">
%s    <div class="wrap">
      <div class="section-head is-centered" data-reveal>
        <h2>Ceny za pokoj a noc</h2>
        <div class="center-row">
          <div class="season-switch" data-season role="group" aria-label="Přepnout sezonu">
            <button type="button" data-value="main" aria-selected="true">Hlavní sezona</button>
            <button type="button" data-value="off" aria-selected="false">Mimo sezonu</button>
          </div>
        </div>
        <p class="muted muted--sm">
          Hlavní sezona od 1. dubna do 30. září, mimo sezonu od 1. října do 31. března.
        </p>
      </div>

      <div class="room-grid" data-reveal-group>
%s      </div>

      <div class="menu-note">
        Ubytování jedné osoby ve dvoulůžkovém pokoji stojí 1 300 Kč za noc. Místní poplatek
        z pobytu je v ceně. Snídaně se podává od deváté hodiny a v ceně pokoje není.
        Změna cen vyhrazena.
      </div>

      <div class="section-head is-centered section-head--mid" data-reveal>
        <h2>Co je v ceně</h2>
      </div>
%s    </div>
  </section>

  <section class="section" id="okoli">
%s    <div class="wrap">
      <div class="section-head is-centered" data-reveal>
        <h2>Kam vyrazit na Třeboňsku</h2>
      </div>
%s    </div>
  </section>

  <section class="section section--paper" id="fotky">
%s    <div class="wrap">
      <div class="section-head is-centered" data-reveal>
        <h2>Pokoje a apartmány</h2>
      </div>
      <div class="gallery" data-reveal-group>
%s      </div>
    </div>
  </section>

  <section class="section" id="prijezd">
%s    <div class="wrap split">
      <div class="flow" data-reveal>
        <h2>Příjezd a odjezd</h2>
        <ul class="checklist">
          <li>%s Ubytovat se můžete od 14 do 20 hodin</li>
          <li>%s Pokoj prosíme uvolnit nejpozději do 10 hodin v den odjezdu</li>
          <li>%s Rezervace přijímáme telefonicky nebo e-mailem</li>
          <li>%s Domácí mazlíčci nejsou v penzionu povoleni</li>
        </ul>
      </div>
      <div data-reveal data-delay>
        <div class="contact-card">
          <div class="contact-card__icon">%s</div>
          <div>
            <h3>Rezervace ubytování</h3>
            <a class="big" href="tel:%s">389 822 493</a>
            <p class="note">Pondělí až pátek od 8 do 15 hodin. Mimo tuto dobu volejte
              <a href="tel:+420775110026">775 110 026</a> nebo
              <a href="tel:+420775110025">775 110 025</a>, a to od 10 do 22 hodin.</p>
          </div>
        </div>
      </div>
    </div>
  </section>
</main>
''' % (page_hero('Penzion',
                 'Dvacet šest lůžek ve dvanácti pokojích, vlastní klidný areál a parkování přímo u domu.',
                 'Ubytování'),
       sep('sand'), TEL_P,
       photo('areal-budova', 'Budova penzionu s vlastním parkovištěm v areálu'),
       photo('pokoj-dvouluzkovy', 'Dvoulůžkový pokoj se střešními okny'),
       sep('white', 'wave2'), rooms, info_list(VYBAVENI, 'info--tiles'),
       sep('paper', 'wave4'), info_list(OKOLI),
       sep('white', 'wave5'), fotky,
       sep('paper', 'wave3'),
       I_CHECK, I_CHECK, I_CHECK, I_CHECK,
       I_PHONE, TEL_P)

    return (head('Ubytování v penzionu U Slunce, Třeboň',
                 'Penzion U Slunce v Třeboni. Pokoje a apartmány s klimatizací, kuchyňkou a vlastní '
                 'koupelnou. Parkování v areálu, kolárna a nabíjení elektrokol.',
                 'ubytovani.html', SCHEMA_UB)
            + header('ubytovani.html') + body + footer('white', 'wave2') + LIGHTBOX + SCRIPT)


# =================================================================== Kontakt
def build_kontakt():
    body = '''<main id="main">

%s
  <section class="section">
%s    <div class="wrap">
      <div class="cards cards--2" data-reveal-group>
        <div class="contact-card" data-reveal>
          <div class="contact-card__icon">%s</div>
          <div>
            <h3>Restaurace, rezervace stolu</h3>
            <a class="big" href="tel:%s">389 822 499</a>
            <p class="note">Denně od 10 do 22 hodin, v pátek a v sobotu do 23 hodin.</p>
          </div>
        </div>

        <div class="contact-card" data-reveal>
          <div class="contact-card__icon">%s</div>
          <div>
            <h3>Penzion, rezervace ubytování</h3>
            <a class="big" href="tel:%s">389 822 493</a>
            <p class="note">Pondělí až pátek od 8 do 15 hodin. Ostatní dny od 10 do 22 hodin volejte
              <a href="tel:+420775110026">775 110 026</a> nebo
              <a href="tel:+420775110025">775 110 025</a>.</p>
          </div>
        </div>

        <div class="contact-card" data-reveal>
          <div class="contact-card__icon">%s</div>
          <div>
            <h3>E-mail</h3>
            <a class="big big--mail" href="mailto:%s">%s</a>
            <p class="note">Rezervaci ubytování vyřídíme také e-mailem.</p>
          </div>
        </div>

        <div class="contact-card" data-reveal>
          <div class="contact-card__icon">%s</div>
          <div>
            <h3>Adresa</h3>
            <p class="address">Riegrova 1251<br>379 01 Třeboň</p>
            <p class="note">Parkování přímo v areálu penzionu. IČ 25183800.</p>
          </div>
        </div>
      </div>
    </div>
  </section>

  <section class="section section--paper section--tight">
%s    <div class="wrap split">
      <div class="flow" data-reveal>
        <h2>Kdy máme otevřeno</h2>
        <ul class="hours" data-hours>
          <li data-days="sun-thu"><span class="day">Neděle až čtvrtek</span><span class="time">10.00 až 22.00</span></li>
          <li data-days="fri-sat"><span class="day">Pátek a sobota</span><span class="time">10.00 až 23.00</span></li>
        </ul>
        <p class="muted">Ubytování má vlastní časy příjezdu a odjezdu,
          najdete je <a href="ubytovani.html#prijezd" class="text-link">u penzionu</a>.</p>
      </div>
      <div data-reveal data-delay>
        <div class="map-frame">
          <iframe
            src="https://maps.google.com/maps?q=Riegrova%%201251%%2C%%20379%%2001%%20T%%C5%%99ebo%%C5%%88&amp;z=16&amp;output=embed"
            title="Mapa, Penzion U Slunce, Riegrova 1251, Třeboň"
            loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
        </div>
      </div>
    </div>
  </section>

  <section class="section section--tight">
%s    <div class="wrap wrap--narrow">
      <div class="section-head is-centered section-head--tight" data-reveal>
        <h2>Hledáme posily do týmu</h2>
      </div>
      <div class="menu-note" data-reveal>
        <p><strong>Na stálý pracovní poměr přijmeme</strong>
          číšníka nebo servírku a pokojskou.</p>
        <p>Dále hledáme <strong>brigádníky na sezonní práci</strong>
          v kuchyni, v restauraci a na úklid pokojů.</p>
        <p>Informace na telefonu
          <a href="tel:+420602102113" class="text-link">602 102 113</a>.</p>
      </div>
    </div>
  </section>
</main>
''' % (page_hero('Kontakt', 'Riegrova 1251, Třeboň. Rezervace přijímáme telefonicky i e-mailem.', 'Kontakt'),
       sep('sand'), I_PHONE, TEL_R, I_KEY, TEL_P, I_MAIL, MAIL, MAIL, I_PIN,
       sep('white', 'wave2'), sep('paper', 'wave4'))

    return (head('Kontakt, Restaurace a penzion U Slunce Třeboň',
                 'Kontakty na restauraci a penzion U Slunce, Riegrova 1251, Třeboň. Telefon, e-mail, '
                 'otevírací doba a mapa.',
                 'kontakt.html')
            + header('kontakt.html') + body + footer('white', 'wave5') + SCRIPT)


BUILDERS = {
    'index.html': build_index,
    'restaurace.html': build_restaurace,
    'listek.html': build_listek,
    'ubytovani.html': build_ubytovani,
    'kontakt.html': build_kontakt,
}

if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    for name, fn in BUILDERS.items():
        with io.open(os.path.join(here, name), 'w', encoding='utf-8', newline='\n') as f:
            f.write(fn())
        print('hotovo', name)
