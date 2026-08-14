#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Générateur du Journal de la Cosmétique.

Une seule source de vérité — le CORPUS ci-dessous — produit :
  · assets/articles.js                  index de la recherche
  · <rubrique>/index.html  (×6)         pages d'univers
  · recherche/index.html                page de recherche (corpus complet en HTML sans JS)
  · sitemap.xml                         toutes les URL du site

Usage :  python3 tools/generer.py
Ajouter un article = ajouter une ligne au CORPUS, puis relancer.
"""

import os, re, html
from datetime import date

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://www.lejournalcosmetique.fr"
AUJ = "13 août 2026"
AUJ_ISO = "2026-08-13"
AUJ_COURT = "13.08.2026"

# ————————————————————————————————————————————————————————————————
# RUBRIQUES — l'ordre est celui de la classification en page d'accueil
# ————————————————————————————————————————————————————————————————
RUBRIQUES = [
    dict(slug="soin-visage", sym="So", num="01", nom="Le Soin", court="Soin visage",
         sous="Visage · Routines · SPF",
         titre="Le Soin du visage",
         chapo="Hydratation, actifs, protection solaire, routines : ce que contiennent réellement les formules, "
               "à quel prix, et pour quel type de peau.",
         img="1585945037805-5fd82c2e60b1",
         alt="Texture d’une crème hydratante étalée en lumière naturelle"),
    dict(slug="maquillage", sym="Ma", num="02", nom="Le Maquillage", court="Maquillage",
         sous="Teint · Lèvres · Regard",
         titre="Le Maquillage",
         chapo="Teint, lèvres, regard : la tenue réellement constatée, les textures, le prix au gramme — "
               "et ce que valent les allégations des marques.",
         img="1522335789203-aabd1fc54bc9",
         alt="Produits de maquillage assortis photographiés sur fond gris"),
    dict(slug="parfum", sym="Pa", num="03", nom="Le Parfum", court="Parfum",
         sous="Maisons · Niche · Sillages",
         titre="Le Parfum",
         chapo="Concentrations, familles olfactives, tenue réelle, maisons à connaître : "
               "de quoi choisir un flacon sans s'en remettre à une note de tête en boutique.",
         img="1594125311687-3b1b3eafa9f4",
         alt="Flacon de parfum en verre posé sur une surface claire"),
    dict(slug="cheveux", sym="Ch", num="04", nom="Les Cheveux", court="Cheveux",
         sous="Soins · Couleur · Coiffage",
         titre="Les Cheveux",
         chapo="Shampoings, colorations, chute, cuir chevelu : ce que la science valide, "
               "ce que le marketing promet, et l’écart entre les deux.",
         img="1747858989102-cca0f4dc4a11",
         alt="Flacon de shampoing photographié sur fond neutre"),
    dict(slug="corps", sym="Co", num="05", nom="Le Corps", court="Corps",
         sous="Hydratation · Solaires · Rituels",
         titre="Le Corps",
         chapo="Solaires, baumes, mains, déodorants : les grandes contenances, là où le prix au litre "
               "pèse le plus lourd dans la décision.",
         img="1763503839418-2b45c3d7a3c3",
         alt="Pot de crème posé sur une pierre naturelle"),
    dict(slug="decryptages", sym="Sc", num="06", nom="La Science", court="Science",
         sous="INCI · Actifs · Réglementation",
         titre="La Science des formules",
         chapo="Listes INCI, réglementation européenne, labels sans définition, hygiène de vie : "
               "ce qu’il faut savoir pour juger une formule par soi-même.",
         img="1629380108574-40c083555579",
         alt="Main lisant l’étiquette INCI d’un flacon cosmétique"),
]

# ————————————————————————————————————————————————————————————————
# CORPUS — (rubrique, titre, type, date lisible, date ISO, lecture, url, mots-clés)
# url = "#" tant que l'article n'est pas écrit.
# ————————————————————————————————————————————————————————————————
A = lambda rub, titre, type_, d, iso, lect, url="#", cles=(), une=False, chapo="": dict(
    rubrique=rub, titre=titre, type=type_, date=d, iso=iso, lecture=lect, url=url,
    cles=list(cles), une=une, chapo=chapo)

CORPUS = [
    # ————————————————————————————————————————————————————————————
    # VIDE — le site part sur une base saine, sans article fictif.
    #
    # Pour publier un article : décommenter le modèle ci-dessous,
    # remplir les champs, créer la page HTML correspondante,
    # puis relancer  python3 tools/generer.py
    #
    # A("soin-visage",                                   # rubrique (slug)
    #   "Meilleures crèmes hydratantes : notre sélection",# titre
    #   "Guide d'achat",                                  # type affiché
    #   "20 août 2026", "2026-08-20",                     # date lisible, date ISO
    #   "14 min",                                         # durée de lecture
    #   "/guides/soin-visage/creme-hydratante/",          # URL réelle de l'article
    #   ("crème hydratante", "céramides", "peau sèche"),  # mots-clés pour la recherche
    #   une=True,                                         # article mis en tête de rubrique
    #   chapo="Résumé en une ou deux phrases."),
    # ————————————————————————————————————————————————————————————
]

# pages fixes ajoutées à l'index de recherche
PAGES = [
    dict(titre="À propos — qui écrit, qui teste, qui relit", url="/a-propos/", rubrique="Le média",
         type="Page", lecture="", cles=["rédaction", "équipe", "charte", "indépendance", "Triaina"]),
    dict(titre="Notre méthode — comment nous testons et notons", url="/notre-methode/", rubrique="Le média",
         type="Page", lecture="", cles=["méthode", "protocole", "indice de preuve", "test", "21 jours"]),
    dict(titre="Contact — écrire à la rédaction", url="/contact/", rubrique="Le média",
         type="Page", lecture="", cles=["contact", "partenariat", "erreur", "échantillon"]),
    dict(titre="Mentions légales", url="/mentions-legales/", rubrique="Le média",
         type="Page", lecture="", cles=["mentions légales", "éditeur", "LCEN", "hébergeur"]),
    dict(titre="Politique de confidentialité", url="/politique-de-confidentialite/", rubrique="Le média",
         type="Page", lecture="", cles=["RGPD", "cookies", "données personnelles", "vie privée"]),
]

# ————————————————————————————————————————————————————————————————
def e(s):
    return html.escape(s, quote=True)

def js(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')

def rub(slug):
    return next(r for r in RUBRIQUES if r["slug"] == slug)

def articles_de(slug):
    return [a for a in CORPUS if a["rubrique"] == slug]

def img_url(ident, w):
    return "https://images.unsplash.com/photo-%s?q=80&w=%d&auto=format&fit=crop" % (ident, w)

# ————— fragments communs —————
def nav(actif=""):
    liens = "".join(
        '\n      <a href="/%s/"%s>%s</a>' % (r["slug"], ' aria-current="page"' if r["slug"] == actif else "", e(r["court"]))
        for r in RUBRIQUES)
    return """  <nav class="nav" aria-label="Navigation principale">
    <div class="wrap">%s
      <a class="rch-lien" href="/recherche/" data-rch-open>Rechercher <span class="kbd">⌘K</span></a>
    </div>
  </nav>""" % liens

def topbar(droite="Financement : <b>0 % sponsors</b>"):
    return """  <div class="top">
    <div class="wrap">
      <span>Média indépendant — <b>Paris</b></span>
      <span class="t-off"><b>48.8566° N, 2.3522° E</b></span>
      <span data-date-jour>Édition du jour</span>
      <span class="t-off">%s</span>
    </div>
  </div>""" % droite

def entete(tagline):
    return """  <header class="head">
    <div class="wrap">
      <a class="wordmark" href="/">Le Journal de la <span class="ac">Cosmétique</span></a>
      <p class="tag">%s</p>
    </div>
  </header>""" % tagline

OVERLAY = """  <div class="rch" id="rch" role="dialog" aria-modal="true" aria-label="Rechercher sur le site">
    <div class="rch-box">
      <div class="rch-top">
        <svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.8-3.8" stroke-linecap="round"/></svg>
        <label for="rch-champ" class="sr" style="position:absolute;left:-9999px">Rechercher un article</label>
        <input id="rch-champ" type="search" placeholder="Rétinol, SPF 50, INCI, parfum…" autocomplete="off" spellcheck="false">
        <button class="esc" type="button">Esc</button>
      </div>
      <p class="rch-etat"><span class="nb">Suggestions</span><span>Le Journal de la Cosmétique</span></p>
      <div class="rch-res"></div>
      <p class="rch-bas"><span><b>↑</b> <b>↓</b> naviguer</span><span><b>↵</b> ouvrir</span><span><b>Esc</b> fermer</span><span><b>⌘K</b> ou <b>/</b> rouvrir</span></p>
    </div>
  </div>"""

def pied():
    return """  <footer>
    <div class="mq" aria-hidden="true">
      <div class="track">
        <span>Le Journal de la Cosmétique<i>◇</i>La beauté, passée au crible<i>◇</i></span>
        <span>Le Journal de la Cosmétique<i>◇</i>La beauté, passée au crible<i>◇</i></span>
      </div>
    </div>
    <div class="wrap cols">
      <span>© 2026 — Triaina, Paris</span>
      <nav aria-label="Pied de page">
        <a href="/a-propos/">À propos</a>
        <a href="/notre-methode/">Notre méthode</a>
        <a href="/contact/">Contact</a>
        <a href="/mentions-legales/">Mentions légales</a>
        <a href="/politique-de-confidentialite/">Confidentialité</a>
      </nav>
      <span>ISSN en cours d’attribution</span>
    </div>
  </footer>

%s

  <script src="/assets/articles.js"></script>
  <script src="/assets/search.js"></script>
  <script src="/assets/site.js"></script>
</body>
</html>
""" % OVERLAY

def univers(actif=""):
    els = "".join(
        '\n        <a class="el" href="/%s/"%s><span class="z">%s</span><span class="sym">%s</span><span class="nom">%s</span></a>'
        % (r["slug"], ' aria-current="page"' if r["slug"] == actif else "",
           ("%s — %d" % (r["num"], len(articles_de(r["slug"])))) if articles_de(r["slug"]) else r["num"],
           r["sym"], e(r["court"]))
        for r in RUBRIQUES)
    return """      <section class="univers" aria-label="Les autres univers">
        <h2>La classification des univers</h2>
        <div class="grid">%s
        </div>
      </section>""" % els

def tete(titre, desc, url, extra_css="", robots="index, follow, max-image-preview:large"):
    return """<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>%s</title>
  <meta name="description" content="%s">
  <link rel="canonical" href="%s%s">
  <meta name="robots" content="%s">
  <link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">
  <meta name="theme-color" content="#C8F135">

  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Le Journal de la Cosmétique">
  <meta property="og:locale" content="fr_FR">
  <meta property="og:title" content="%s">
  <meta property="og:description" content="%s">
  <meta property="og:url" content="%s%s">

  <link rel="preconnect" href="https://images.unsplash.com" crossorigin>
  <link rel="stylesheet" href="/assets/fonts.css">
  <link rel="stylesheet" href="/assets/pages.css">
  <link rel="stylesheet" href="/assets/search.css">
  <link rel="preload" href="/assets/fonts/archivo-var-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="/assets/fonts/fragment-mono-latin.woff2" as="font" type="font/woff2" crossorigin>
%s""" % (e(titre), e(desc), SITE, url, robots, e(titre), e(desc), SITE, url, extra_css)

# ————————————————————————————————————————————————————————————————
def page_rubrique(r):
    arts = articles_de(r["slug"])
    lead = next((a for a in arts if a["une"]), arts[0]) if arts else None
    autres = [a for a in arts if a is not lead]

    # ————— corps : soit les articles, soit un état « en préparation » —————
    if arts:
        liste = "".join(
            '\n        <a href="%s"><span class="ty">%s</span><span class="ti">%s</span><span class="da">%s</span><span class="le">%s</span></a>'
            % (a["url"], e(a["type"]), e(a["titre"]), e(a["date"].replace(" 2026", "")), e(a["lecture"]))
            for a in autres)
        bloc_une = """      <article>
        <a class="rub-lead" href="%s">
          <span class="ph"><img src="%s" alt="%s" width="900" height="600" fetchpriority="high"></span>
          <span class="in">
            <span class="tg">%s</span>
            <h2>%s</h2>
            <span class="ch">%s</span>
            <span class="mt"><span>%s</span><span>%s de lecture</span></span>
          </span>
        </a>
      </article>

""" % (lead["url"], img_url(r["img"], 900), e(r["alt"]), e(lead["type"]), e(lead["titre"]),
       e(lead["chapo"] or r["chapo"]), e(lead["date"]), e(lead["lecture"]))
        bloc_liste = """      <section aria-label="Tous les articles de la rubrique">
        <h2 class="rub-titre">Tous les articles — %s</h2>
        <div class="rub-liste">%s
        </div>
      </section>""" % (e(r["court"]), liste)
        ligne_meta = "<span><b>%d</b> article%s publié%s</span>" % (
            len(arts), "s" if len(arts) > 1 else "", "s" if len(arts) > 1 else "")
        itemlist = """{
        "@type": "ItemList",
        "name": "%s",
        "numberOfItems": %d,
        "itemListElement": [%s
        ]
      },""" % (e(r["titre"]), len(arts),
                "".join('\n          { "@type": "ListItem", "position": %d, "name": "%s" }%s'
                        % (i + 1, js(e(a["titre"])), "," if i < len(arts) - 1 else "")
                        for i, a in enumerate(arts)))
        desc = "%s — les articles du Journal de la Cosmétique : %s" % (r["titre"], r["sous"].lower())
    else:
        bloc_une = ""
        bloc_liste = """      <section class="vide" aria-label="Rubrique en préparation">
        <p class="k">Rubrique en préparation</p>
        <p>Les premiers articles paraîtront prochainement. Chacun sera testé ou sourcé selon le
        protocole que nous publions — vous pouvez le lire dès aujourd’hui.</p>
        <p class="l"><a href="/notre-methode/">Notre méthode de test</a><a href="/a-propos/">Qui écrit le journal</a></p>
      </section>"""
        ligne_meta = "<span>Premiers articles <b>à paraître</b></span>"
        itemlist = ""
        desc = "%s — %s. Rubrique en préparation : les premiers articles du Journal de la Cosmétique paraîtront prochainement." % (r["titre"], r["sous"])

    jsonld = """
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "CollectionPage",
        "@id": "%s/%s/#webpage",
        "url": "%s/%s/",
        "name": "%s — Le Journal de la Cosmétique",
        "description": "%s",
        "inLanguage": "fr-FR",
        "isPartOf": { "@id": "%s/#website" }
      },
      %s
      {
        "@type": "BreadcrumbList",
        "itemListElement": [
          { "@type": "ListItem", "position": 1, "name": "Accueil", "item": "%s/" },
          { "@type": "ListItem", "position": 2, "name": "%s" }
        ]
      }
    ]
  }
  </script>
</head>
""" % (SITE, r["slug"], SITE, r["slug"], e(r["titre"]), e(r["chapo"][:150]), SITE,
       itemlist, SITE, e(r["court"]))

    return (tete("%s — Le Journal de la Cosmétique" % r["titre"], desc, "/%s/" % r["slug"], jsonld) +
"""<body>
  <a class="skip" href="#contenu">Aller au contenu</a>

%s

%s

%s

  <div class="wrap">
    <nav class="crumbs" aria-label="Fil d’Ariane">
      <ol>
        <li><a href="/">Accueil</a></li>
        <li aria-current="page">%s</li>
      </ol>
    </nav>
  </div>

  <header class="phead">
    <div class="wrap">
      <p class="lab">Univers %s · %s</p>
      <h1>%s</h1>
      <p class="sf">%s</p>
      <p class="meta">
        %s
        <span>Tous <b>testés ou sourcés</b></span>
      </p>
    </div>
  </header>

  <main id="contenu" class="corps">
    <div class="wrap">

%s%s

%s

    </div>
  </main>

""" % (topbar(), entete("Univers %s — <b>%s</b><br>%s" % (r["num"], e(r["sym"]), e(r["sous"]))), nav(r["slug"]),
       e(r["court"]), r["num"], e(r["sym"]), e(r["titre"]), e(r["chapo"]), ligne_meta,
       bloc_une, bloc_liste, univers(r["slug"]))
       + pied())

# ————————————————————————————————————————————————————————————————
def page_recherche():
    total = len(CORPUS)
    blocs = ""
    for r in RUBRIQUES:
        arts = articles_de(r["slug"])
        if not arts:
            continue
        lignes = "".join(
            '\n          <a href="%s"><span class="ty">%s</span><span class="ti">%s</span><span class="da">%s</span><span class="le">%s</span></a>'
            % (a["url"], e(a["type"]), e(a["titre"]), e(a["date"].replace(" 2026", "")), e(a["lecture"]))
            for a in arts)
        blocs += """
        <section style="margin-top:38px;">
          <h2 style="font-family:var(--mono); font-size:10px; letter-spacing:.16em; text-transform:uppercase; color:var(--gris); font-weight:400; margin-bottom:6px;">
            <a href="/%s/" style="border-bottom:1px solid var(--acide-d); padding-bottom:2px;">%s — %s · %d articles</a>
          </h2>
          <div class="rub-liste">%s
          </div>
        </section>""" % (r["slug"], r["num"], e(r["titre"]), len(arts), lignes)

    css = """
  <style>
    .rch-page-form{ border:1px solid var(--hair-f); display:flex; align-items:center; gap:14px; padding:16px 20px; margin-top:8px; }
    .rch-page-form svg{ width:19px; height:19px; flex:none; }
    .rch-page-form svg circle, .rch-page-form svg path{ fill:none; stroke:var(--noir); stroke-width:2.2; }
    .rch-page-form input{ flex:1; border:0; background:transparent; font-family:var(--sans); font-size:21px; font-weight:700; color:var(--noir); padding:4px 0; }
    .rch-page-form input:focus{ outline:none; }
    .rch-page-form input::placeholder{ color:#9A9A90; font-weight:500; }
    #rch-page-etat{ margin-top:12px; font-family:var(--mono); font-size:10px; letter-spacing:.08em; text-transform:uppercase; color:var(--gris); }
    #rch-page-res a{ display:grid; grid-template-columns:1fr auto; gap:5px 16px; align-items:baseline; padding:15px 6px; border-bottom:1px solid var(--hair); }
    #rch-page-res a:hover{ background:rgba(200,241,53,.28); }
    #rch-page-res .t{ grid-column:1; grid-row:1; font-weight:700; font-size:16px; line-height:1.3; }
    #rch-page-res .t mark{ background:transparent; color:var(--cobalt); font-weight:800; }
    #rch-page-res .rb{ grid-column:1; grid-row:2; font-family:var(--mono); font-size:9.5px; letter-spacing:.06em; text-transform:uppercase; color:var(--gris); }
    #rch-page-res .mt{ grid-column:2; grid-row:1 / span 2; font-family:var(--mono); font-size:9.5px; text-transform:uppercase; color:var(--gris); white-space:nowrap; text-align:right; }
    #rch-page-res .rch-vide{ padding:40px 0; text-align:center; }
    #rch-page-res .rch-vide p{ font-size:16px; }
    #rch-page-res .rch-vide .s{ margin-top:8px; font-family:var(--mono); font-size:10px; text-transform:uppercase; color:var(--gris); }
  </style>
"""
    jsonld = """
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "SearchResultsPage",
    "url": "%s/recherche/",
    "name": "Recherche — Le Journal de la Cosmétique",
    "inLanguage": "fr-FR",
    "isPartOf": { "@id": "%s/#website" }
  }
  </script>
</head>
""" % (SITE, SITE)

    return (tete("Recherche — Le Journal de la Cosmétique",
                 "Rechercher dans les articles du Journal de la Cosmétique : soins, maquillage, parfums, cheveux, corps et science des formules.",
                 "/recherche/", css + jsonld, robots="noindex, follow") +
"""<body>
  <a class="skip" href="#contenu">Aller au contenu</a>

%s

%s

%s

  <div class="wrap">
    <nav class="crumbs" aria-label="Fil d’Ariane">
      <ol>
        <li><a href="/">Accueil</a></li>
        <li aria-current="page">Recherche</li>
      </ol>
    </nav>
  </div>

  <header class="phead">
    <div class="wrap">
      <p class="lab">Catalogue</p>
      <h1><span class="ac">Rechercher</span></h1>
      <p class="sf">%s</p>
    </div>
  </header>

  <main id="contenu" class="corps" id-page="recherche">
    <div class="wrap">
      <div id="rch-page">
        <form class="rch-page-form" role="search" onsubmit="return false;">
          <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.8-3.8" stroke-linecap="round"/></svg>
          <label for="rch-page-champ" style="position:absolute;left:-9999px">Rechercher un article</label>
          <input id="rch-page-champ" type="search" name="q" placeholder="Rétinol, SPF 50, INCI, parfum…" autocomplete="off" spellcheck="false">
        </form>
        <p id="rch-page-etat">%s</p>
        <div id="rch-page-res"></div>

        <div id="rch-page-tout">%s
        </div>
      </div>

%s

    </div>
  </main>

""" % (topbar("Catalogue : <b>%s</b>" % (("%d articles" % total) if total else "en construction")),
       entete("Tout le journal, en une page<br><b>%s</b>" % (("%d articles classés par univers" % total) if total else "les premiers articles arrivent")),
       nav(),
       ("Tapez un actif, un type de peau, une marque, un budget — ou parcourez simplement les %d articles du journal, classés par univers." % total)
         if total else "Le catalogue se remplira au fil des publications. La recherche fonctionne dès à présent sur les pages du journal.",
       ("%d articles au catalogue" % total) if total else "Aucun article publié pour l’instant",
       blocs if blocs else """
        <section class="vide" style="margin-top:38px;">
          <p class="k">Catalogue en construction</p>
          <p>Les premiers articles paraîtront prochainement. En attendant, la recherche porte sur les pages du journal.</p>
          <p class="l"><a href="/notre-methode/">Notre méthode</a><a href="/a-propos/">La rédaction</a></p>
        </section>""",
       univers())
       + pied())

# ————————————————————————————————————————————————————————————————
def index_js():
    lignes = []
    for a in CORPUS:
        r = rub(a["rubrique"])
        lignes.append('  { titre: "%s", url: "%s", rubrique: "%s", type: "%s", lecture: "%s", cles: [%s]%s }'
                      % (js(a["titre"]), a["url"], js(r["court"]), js(a["type"]), a["lecture"],
                         ", ".join('"%s"' % js(c) for c in a["cles"]),
                         ", mis_en_avant: true" if a["une"] else ""))
    for p in PAGES:
        lignes.append('  { titre: "%s", url: "%s", rubrique: "%s", type: "%s", lecture: "", cles: [%s] }'
                      % (js(p["titre"]), p["url"], js(p["rubrique"]), js(p["type"]),
                         ", ".join('"%s"' % js(c) for c in p["cles"])))
    return ("/* Index de recherche — généré par tools/generer.py, ne pas éditer à la main. */\n"
            "window.JDC_ARTICLES = [\n" + ",\n".join(lignes) + "\n];\n")

def sitemap():
    urls = [("/", "daily", "1.0", AUJ_ISO)]
    for r in RUBRIQUES:
        urls.append(("/%s/" % r["slug"], "weekly", "0.8", AUJ_ISO))
    for a in CORPUS:
        if a["url"].startswith("/"):
            urls.append((a["url"], "monthly", "0.9", a["iso"]))
    for u in ["/a-propos/", "/notre-methode/"]:
        urls.append((u, "monthly", "0.7", AUJ_ISO))
    urls.append(("/contact/", "yearly", "0.5", AUJ_ISO))
    for u in ["/mentions-legales/", "/politique-de-confidentialite/"]:
        urls.append((u, "yearly", "0.3", AUJ_ISO))
    corps = "".join(
        "  <url>\n    <loc>%s%s</loc>\n    <lastmod>%s</lastmod>\n    <changefreq>%s</changefreq>\n    <priority>%s</priority>\n  </url>\n"
        % (SITE, u, lm, cf, pr) for u, cf, pr, lm in urls)
    return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n%s</urlset>\n' % corps

# ————————————————————————————————————————————————————————————————
def ecrire(chemin, contenu):
    complet = os.path.join(RACINE, chemin)
    os.makedirs(os.path.dirname(complet), exist_ok=True)
    with open(complet, "w", encoding="utf-8") as f:
        f.write(contenu)
    print("  ✓ %-52s %6d o" % (chemin, len(contenu.encode("utf-8"))))

def main():
    print("Génération du Journal de la Cosmétique — %d articles, %d rubriques" % (len(CORPUS), len(RUBRIQUES)))
    ecrire("assets/articles.js", index_js())
    for r in RUBRIQUES:
        ecrire("%s/index.html" % r["slug"], page_rubrique(r))
    ecrire("recherche/index.html", page_recherche())
    ecrire("sitemap.xml", sitemap())
    print("Terminé.")

if __name__ == "__main__":
    main()
