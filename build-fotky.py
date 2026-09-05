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

# Docasna nahrada z fotobanky, nez dorazi vlastni fotky jidla. Unsplash
# License, komercni uziti bez uvadeni autora:
# https://unsplash.com/photos/photo-1584300005420-38486f627b07
STOCK = {'jidlo-pstruh'}

# webove jmeno -> soubor originalu
MAP = {
    'apartman':               'p_P1060001.JPG',
    'areal-budova':           'p_P1060042.JPG',
    'areal-detail':           'p_P1060056.JPG',
    'areal-dvur':             'p_P7135026a.jpg',
    'areal-vjezd':            'p_P1060057.JPG',
    'bar':                    'r2_DSC05515a.jpg',
    'chodba':                 'p_P1060052.JPG',
    'jidlo-pstruh':           'stock-pstruh.jpg',
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

# Hlavička úvodní strany: průčelí domu s cedulemi Restaurace a Pension.
# Předloha má 1200 bodů, takže se zvětšuje jen málo. Ostří se jednou a mírně,
# stupňované doostřování dělalo kolem hran hala.
HERO = {
    # Hero jde pres celou sirku okna, proto se bere cely snimek. Jeho pomer
    # 16:9 sedi na sirokou obrazovku, takze prohlizec skoro nic neurizne.
    'hero-uvod':      ('hero foto.jpg', (0, 0, 1200, 675), 1800),
    # na telefonu jde fotka pres celou obrazovku, ta je ale skoro dvakrat
    # vyssi nez sirsi; vyrez proto musi byt uzky jako displej, jinak by z nej
    # prohlizec ubral dalsi kus po stranach. Zacina az za napisem Restaurace,
    # at se zadne slovo neurizne, a konci u vstupni cedule.
    'hero-uvod-uzky': ('hero foto.jpg', (334, 0, 684, 675), 800),
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
