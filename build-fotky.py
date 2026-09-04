# -*- coding: utf-8 -*-
"""Přegeneruje fotografie webu U Slunce z originálů.

Zásada: nikdy nezvětšovat nad rozlišení předlohy (640x480).
Předchozí verze webu roztahovala tytéž snímky na 2200 az 2560 px,
proto vypadaly rozmazane.
"""
import os
from PIL import Image, ImageEnhance, ImageFilter

SRC = 'podklady-originaly'
OUT = 'web/assets/photos'

# webove jmeno -> soubor originalu
MAP = {
    'apartman':               'p_P1060001.JPG',
    'areal-budova':           'p_P1060042.JPG',
    'areal-detail':           'p_P1060056.JPG',
    'areal-dvur':             'p_P7135026a.jpg',
    'areal-vjezd':            'p_P1060057.JPG',
    'bar':                    'r2_DSC05515a.jpg',
    'chodba':                 'p_P1060052.JPG',
    'fasada':                 'r2_DSC05504a.jpg',
    'koupelna':               'p_P7134998a.jpg',
    'kuchyne-provoz':         'r2_P1060009.JPG',
    'kuchyne-talire':         'r2_P1060010.JPG',
    'kuchynka':               'p_P1060005.JPG',
    'parkovani':              'p_P1060036.JPG',
    'parkoviste':             'p_P1060049.JPG',
    'pokoj-dvouluzkovy':      'p_P7134988a.jpg',
    'pokoj-podkrovni':        'p_P7134979a.jpg',
    'pokoj-s-terasou':        'p_P7134970.JPG',
    'restaurace-interier':    'r2_P1060032.JPG',
    'restaurace-salonek':     'r2_DSC05512a.jpg',
    'restaurace-vstup':       'r2_P1060028.JPG',
    'ulice':                  'r2_P1060035.JPG',
    'zahradka-detsky-koutek': 'r_P1060015.JPG',
    'zahradka-kvetiny':       'r_P1060024.JPG',
    'zahradka-pergola':       'r_P1060018.JPG',
    'zahradka-slunce':        'r_P1060026.JPG',
    'zahradka-vchod':         'r_P1060022.JPG',
    'znak-slunce':            'r2_P1060041.JPG',
}

# Hlavička úvodní strany. Předloha má 640 bodů, takže se tu jako v jediném
# místě zvětšuje. Hero proto zabírá jen pravý sloupec, ne celou šířku, a
# zvětšení spadlo z troj- na necelý dvojnásobek. Ostří se jednou a mírně,
# stupňované doostřování dělalo kolem hran hala a šum ve dřevě.
HERO = {
    # Hero zabira jen pravy sloupec, ne celou sirku, proto staci zvetsit
    # necelych dvakrat misto trikrat. To je jediny zpusob, jak z predlohy
    # o 640 bodech dostat ostrost.
    'hero-uvod':      ('r2_DSC05515a.jpg', (130, 0, 640, 480), 1300),
    # na telefonu jde fotka pres celou obrazovku, proto vyska na sirku;
    # displej ma kolem 400 bodu, takze se vyrez spis zmensuje nez zvetsuje
    'hero-uvod-uzky': ('r2_DSC05515a.jpg', (140, 0, 500, 480), 800),
}


def prep(im):
    """Jemna korekce tonu, at fotky z kompaktu nepusobi plose."""
    im = im.convert('RGB')
    im = ImageEnhance.Color(im).enhance(1.06)
    im = ImageEnhance.Contrast(im).enhance(1.04)
    return im


def save(im, name, size, radius=1.0, percent=110, threshold=3, q=84):
    src_w = im.size[0]
    if size[0] > src_w:
        raise ValueError('zakazano zvetsovat: %s (%d -> %d)' % (name, src_w, size[0]))
    if im.size != size:
        im = im.resize(size, Image.LANCZOS)
    im = im.filter(ImageFilter.UnsharpMask(radius=radius, percent=percent, threshold=threshold))
    path = os.path.join(OUT, name + '.webp')
    im.save(path, 'WEBP', quality=q, method=6)
    return os.path.getsize(path)


total = 0
for name, src in sorted(MAP.items()):
    im = prep(Image.open(os.path.join(SRC, src)))
    total += save(im, name, (640, 480), radius=1.0, percent=105)
    total += save(im, name + '-sm', (480, 360), radius=.9, percent=125)

def upscale(im, width):
    """Jeden čistý krok a mírné doostření. Víc už není ostrost, jen halo."""
    ratio = im.size[1] / float(im.size[0])
    im = im.resize((width, int(round(width * ratio))), Image.LANCZOS)
    return im.filter(ImageFilter.UnsharpMask(radius=1.1, percent=62, threshold=3))


for name, (src, box, width) in sorted(HERO.items()):
    im = upscale(prep(Image.open(os.path.join(SRC, src))).crop(box), width)
    path = os.path.join(OUT, name + '.webp')
    im.save(path, 'WEBP', quality=88, method=6)
    total += os.path.getsize(path)
    print('  %s %dx%d  %.0f kB' % (name, im.size[0], im.size[1], os.path.getsize(path) / 1024.))

print('hotovo, %d souboru, %.0f kB' % (len(MAP) * 2 + len(HERO), total / 1024))
