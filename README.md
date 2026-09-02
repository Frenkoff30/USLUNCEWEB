# Restaurace a penzion U Slunce, Třeboň

Statický web pro Restauraci a penzion U Slunce, Riegrova 1251, Třeboň.

## Struktura

```
index.html        Úvodní stránka
restaurace.html   Restaurace, bar, zahrádka
listek.html       Jídelní a nápojový lístek, alergeny
ubytovani.html    Pokoje, ceník, okolí
galerie.html      Fotogalerie s filtrem a lightboxem
kontakt.html      Kontakty, otevírací doba, mapa, kariéra
assets/css/       Stylopis
assets/js/        Interakce
assets/photos/    Fotografie ve formátu WebP
assets/img/       Favicon
```

## Použité technologie

Čisté HTML, CSS a JavaScript bez závislostí. Písma Playfair Display a Karla
se načítají z Google Fonts. Web nepotřebuje žádný build, stačí nahrát obsah
složky na hosting.

## Vlastnosti

* Responzivní od 360 px výše
* Fotografie ve WebP, doostřené a zvětšené z původních podkladů
* Přístupnost: přeskočení na obsah, viditelné focus stavy, ARIA popisky,
  respektování `prefers-reduced-motion`
* Strukturovaná data schema.org pro restauraci a ubytování
* Bez cookies a bez sledovacích skriptů

## Lokální náhled

```
python -m http.server 8080
```

Potom otevřít http://localhost:8080
