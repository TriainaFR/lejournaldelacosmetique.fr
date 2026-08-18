#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Générateur du Journal de la Cosmétique.

Une seule source de vérité — le CORPUS ci-dessous — produit :
  · index.html                          la une du journal
  · assets/articles.js                  index de la recherche
  · <rubrique>/index.html  (×6)         pages d'univers
  · recherche/index.html                page de recherche (corpus complet en HTML sans JS)
  · sitemap.xml                         toutes les URL du site
  · llms.txt                            carte du site pour les moteurs génératifs

Usage :  python3 tools/generer.py
Ajouter un article = ajouter une ligne au CORPUS, puis relancer.

Les visuels (img=) sont des fichiers locaux de images/articles/ dont la provenance
est consignée dans images/manifeste.json. Aucune image distante n'est appelée.
"""

import os, re, html
from datetime import date

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://www.lejournaldelacosmetique.fr"
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
         img="/images/rubriques/soin-visage.jpg",
         alt="Deux disques de gel translucide se superposent sur un fond rosé"),
    dict(slug="maquillage", sym="Ma", num="02", nom="Le Maquillage", court="Maquillage",
         sous="Teint · Lèvres · Regard",
         titre="Le Maquillage",
         chapo="Teint, lèvres, regard : la tenue réellement constatée, les textures, le prix au gramme — "
               "et ce que valent les allégations des marques.",
         img="/images/rubriques/maquillage.jpg",
         alt="Gros plan sur les godets colorés d’une palette de fards à paupières"),
    dict(slug="parfum", sym="Pa", num="03", nom="Le Parfum", court="Parfum",
         sous="Maisons · Niche · Sillages",
         titre="Le Parfum",
         chapo="Concentrations, familles olfactives, tenue réelle, maisons à connaître : "
               "de quoi choisir un flacon sans s'en remettre à une note de tête en boutique.",
         img="/images/rubriques/parfum.jpg",
         alt="Deux flacons de parfum en verre transparent posés sur du marbre"),
    dict(slug="cheveux", sym="Ch", num="04", nom="Les Cheveux", court="Cheveux",
         sous="Soins · Couleur · Coiffage",
         titre="Les Cheveux",
         chapo="Shampoings, colorations, chute, cuir chevelu : ce que la science valide, "
               "ce que le marketing promet, et l’écart entre les deux.",
         img="/images/rubriques/cheveux.jpg",
         alt="Macrographie d’une chevelure brune, fibre par fibre"),
    dict(slug="corps", sym="Co", num="05", nom="Le Corps", court="Corps",
         sous="Hydratation · Solaires · Rituels",
         titre="Le Corps",
         chapo="Solaires, baumes, mains, déodorants : les grandes contenances, là où le prix au litre "
               "pèse le plus lourd dans la décision.",
         img="/images/rubriques/corps.jpg",
         alt="Pot de baume ouvert vu du dessus, sur un fond clair"),
    dict(slug="science", sym="Sc", num="06", nom="La Science", court="Science",
         sous="INCI · Actifs · Réglementation",
         titre="La Science des formules",
         chapo="Listes INCI, réglementation européenne, labels sans définition, hygiène de vie : "
               "ce qu’il faut savoir pour juger une formule par soi-même.",
         img="/images/rubriques/science.jpg",
         alt="Flacons de laboratoire en verre contenant un liquide ambré, alignés sur une surface réfléchissante"),
]

# ————————————————————————————————————————————————————————————————
# CORPUS — (rubrique, titre, type, date lisible, date ISO, lecture, url, mots-clés)
# url = "#" tant que l'article n'est pas écrit.
# img/alt = visuel local (images/articles/…) utilisé en une et sur les cartes.
# ————————————————————————————————————————————————————————————————
A = lambda rub, titre, type_, d, iso, lect, url="#", cles=(), une=False, chapo="", img="", alt="": dict(
    rubrique=rub, titre=titre, type=type_, date=d, iso=iso, lecture=lect, url=url,
    cles=list(cles), une=une, chapo=chapo, img=img, alt=alt)

CORPUS = [
    # ————— Science —————
    A("science",
      "Ingrédients cosmétiques : notre guide complet pour décrypter la liste INCI",
      "Décryptage",
      "17 août 2026", "2026-08-17",
      "16 min",
      "/science/ingredients-cosmetiques-decryptage-inci-complet/",
      ("INCI", "ingrédients cosmétiques", "liste INCI", "étiquette", "allergènes",
       "phénoxyéthanol", "parabènes", "conservateurs", "actifs", "réglementation",
       "CosIng", "nomenclature"),
      une=True,
      chapo="La liste INCI classe les ingrédients par concentration décroissante, en latin pour le végétal "
            "et en anglais pour le chimique. Ce qu'elle révèle, ce qu'elle cache, et comment la lire en cinq minutes.",
      img="/images/articles/inci-lire-etiquette-rayon.jpg",
      alt="Une personne examine le flacon d’un produit cosmétique dans le rayon d’un magasin"),

    # ————— Soin visage —————
    A("soin-visage",
      "Soin visage : le guide complet pour une peau éclatante",
      "Guide",
      "17 août 2026", "2026-08-17",
      "14 min",
      "/soin-visage/soin-visage-guide-complet-peau-eclatante/",
      ("soin visage", "routine", "sérum", "crème hydratante", "SPF", "nettoyant",
       "type de peau", "peau sèche", "peau grasse", "peau sensible", "rétinol",
       "niacinamide", "vitamine C", "acide hyaluronique", "exfoliation"),
      une=True,
      chapo="Nettoyer, traiter, hydrater, protéger : quatre gestes, un ordre unique — du plus léger au plus riche. "
            "Le guide complet, type de peau par type de peau.",
      img="/images/articles/soin-visage-texture-creme.jpg",
      alt="Trace de crème blanche déposée sur un fond beige"),

    # ————— Cheveux —————
    A("cheveux",
      "Soin cheveux : le guide complet par type et besoin",
      "Guide",
      "17 août 2026", "2026-08-17",
      "15 min",
      "/cheveux/soin-cheveux-guide-complet-type-besoin/",
      ("soin cheveux", "soin capillaire", "routine capillaire", "shampoing", "après-shampoing",
       "masque cheveux", "soin sans rinçage", "huile capillaire", "cheveux secs", "cheveux gras",
       "cheveux fins", "cheveux bouclés", "cheveux colorés", "kératine", "céramides", "cuir chevelu"),
      chapo="Le shampoing traite le cuir chevelu, tout le reste traite les longueurs. Le guide complet du soin "
            "capillaire, type par type — avec les fréquences, les actifs et les erreurs qui coûtent le plus cher.",
      img="/images/articles/cheveux-peigne-longueurs.jpg",
      alt="Une main peigne de longs cheveux bruns"),

    # ————— Maquillage —————
    A("maquillage",
      "Maquillage : le guide complet des techniques et tendances 2026",
      "Guide",
      "17 août 2026", "2026-08-17",
      "16 min",
      "/maquillage/guide-complet-techniques-tendances-maquillage/",
      ("maquillage", "techniques de maquillage", "ordre d'application", "primer", "fond de teint",
       "correcteur", "poudre", "blush", "smoky eye", "cut crease", "eyeliner", "rouge à lèvres",
       "tendances maquillage 2026", "glass skin", "monochrome", "tenue"),
      chapo="L’écart entre un résultat net et un résultat approximatif ne tient pas au prix des produits : "
            "il tient à la préparation, à l’ordre des couches et à la quantité posée.",
      img="/images/articles/maquillage-pinceaux-produits.jpg",
      alt="Pinceaux de maquillage et produits disposés sur un fond beige"),

    # ————— Corps —————
    A("corps",
      "Soin corps : hydratation, gommage et rituels beauté",
      "Guide",
      "17 août 2026", "2026-08-17",
      "13 min",
      "/corps/soin-corps-hydratation-gommage-rituels-beaute/",
      ("soin corps", "hydratation corps", "gommage corps", "exfoliation", "lait corps", "crème corps",
       "huile corps", "beurre de karité", "urée", "acide hyaluronique", "céramides", "glycérine",
       "peau sèche", "kératose pilaire", "barrière cutanée"),
      chapo="Tout se joue dans les trois minutes qui suivent la douche : passé ce délai, la même crème "
            "n’a plus grand-chose à retenir. Le moment compte autant que le produit.",
      img="/images/articles/corps-application-lotion.jpg",
      alt="Des mains appliquent une lotion sortie d’un flacon pompe blanc"),

    # ————— Parfum —————
    A("parfum",
      "Parfum : tout comprendre pour choisir son jus",
      "Guide",
      "17 août 2026", "2026-08-17",
      "17 min",
      "/parfum/parfum-femme-guide-complet-choisir-son-jus/",
      ("parfum", "eau de parfum", "eau de toilette", "extrait de parfum", "familles olfactives",
       "roue de Michael Edwards", "Société Française des Parfumeurs", "pyramide olfactive",
       "sillage", "tenue", "allergènes parfum", "règlement 2023/1545", "IFRA", "liste INCI"),
      chapo="« Eau de parfum » n’est pas une norme, la pyramide olfactive n’est pas une propriété physique et "
            "les standards IFRA ne sont pas du droit. Ce qui est opposable, en revanche, est écrit sur l’étiquette.",
      img="/images/articles/parfum-flacon-lumiere.jpg",
      alt="Flacon de parfum en verre éclairé par des lumières bleues et roses"),

    # ————— Science —————
    A("science",
      "Niacinamide : ce que la littérature établit vraiment",
      "Décryptage",
      "17 août 2026", "2026-08-17",
      "15 min",
      "/science/niacinamide-bienfaits-concentration-associations/",
      ("niacinamide", "nicotinamide", "vitamine B3", "vitamine PP", "acide nicotinique", "NAD+",
       "céramides", "mélanosomes", "barrière cutanée", "concentration", "vitamine C", "rétinol",
       "allégations cosmétiques", "grossesse"),
      chapo="Une grande partie de ce qu\u2019on prête à la niacinamide vient de résultats obtenus en boîte de culture, "
            "présentés comme des effets cliniques. Le tri, effet par effet.",
      img="/images/articles/niacinamide-flacon-pipette.jpg",
      alt="Flacon de sérum en verre et son compte-gouttes, sur un fond beige"),

    # ————— Soin visage —————
    A("soin-visage",
      "Crème solaire visage : choisir son SPF selon son phototype",
      "Guide",
      "17 août 2026", "2026-08-17",
      "14 min",
      "/soin-visage/creme-solaire-visage-spf-phototype/",
      ("crème solaire", "SPF", "protection UVA", "logo UVA", "phototype", "Fitzpatrick",
       "filtres minéraux", "filtres organiques", "oxyde de zinc", "dioxyde de titane",
       "quantité", "réapplication", "photovieillissement"),
      chapo="Le SPF ne mesure que les UVB, le marquage PA n\u2019est pas européen, et personne ne filtre 99 %. "
            "Ce qui décide vraiment, c\u2019est la quantité appliquée.",
      img="/images/articles/solaire-lumiere-stores.jpg",
      alt="Visage traversé par la lumière du soleil filtrée par des stores"),

    # ————————————————————————————————————————————————————————————
    # Pour publier un nouvel article : ajouter une entrée sur ce modèle,
    # créer la page HTML correspondante, puis relancer
    #   python3 tools/generer.py
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

""" % (lead["url"], e(lead["img"]), e(lead["alt"]), e(lead["type"]), e(lead["titre"]),
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
#  LA UNE
# ————————————————————————————————————————————————————————————————
def publies():
    """Articles réellement en ligne, du plus récent au plus ancien."""
    return sorted([a for a in CORPUS if a["url"].startswith("/")],
                  key=lambda a: a["iso"], reverse=True)

def page_accueil():
    """La une du journal.

    Trois règles de peuplement, qui garantissent qu'aucune section n'est
    ni vide ni interminable, quel que soit le nombre d'articles publiés :
      · le rail est plafonné à RAIL_MAX, et laisse toujours au moins
        un article au « fil » (le -1) ;
      · le fil est plafonné à FIL_MAX, le surplus renvoyant au catalogue ;
      · une colonne de format n'existe que si un article l'habite.
    """
    RAIL_MAX = 4    # plafond mesuré : au-delà, le rail dépasse la hauteur de la une
    FIL_MAX  = 12   # au-delà, on renvoie au catalogue

    arts = publies()
    lead = next((a for a in arts if a["une"]), arts[0]) if arts else None
    suite = [a for a in arts if a is not lead]
    n_rail = len(suite) if len(suite) <= 1 else min(RAIL_MAX, len(suite) - 1)
    rail, reste = suite[:n_rail], suite[n_rail:]
    fil, surplus = reste[:FIL_MAX], reste[FIL_MAX:]
    n = len(arts)
    dernier_iso = arts[0]["iso"] if arts else AUJ_ISO

    # ————— tête —————
    if n:
        titre = "Le Journal de la Cosmétique — Soins, maquillage & parfums passés au crible"
        desc = ("Média indépendant français : formules relues ligne à ligne, sources publiques citées, "
                "aucun lien d’affiliation. Soins, maquillage, parfums, cheveux, corps et science des formules.")
        og_img = SITE + lead["img"]
    else:
        titre = "Le Journal de la Cosmétique — le média qui passe la beauté au crible"
        desc = "Média indépendant français consacré aux soins, au maquillage, aux parfums et à la science des formules."
        og_img = SITE + "/assets/favicon.svg"

    itemlist = ""
    if n:
        items = ",\n".join(
            '          { "@type": "ListItem", "position": %d, "url": "%s%s", "name": "%s" }'
            % (i + 1, SITE, a["url"], js(e(a["titre"]))) for i, a in enumerate(arts))
        itemlist = """      {
        "@type": "ItemList",
        "@id": "%s/#articles",
        "name": "Les articles du Journal de la Cosmétique",
        "numberOfItems": %d,
        "itemListElement": [
%s
        ]
      },
""" % (SITE, n, items)

    tete_html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{e(titre)}</title>
  <meta name="description" content="{e(desc)}">
  <link rel="canonical" href="{SITE}/">
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
  <link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">
  <meta name="theme-color" content="#C8F135">
  <meta name="apple-mobile-web-app-title" content="Le Journal de la Cosmétique">
  <meta name="application-name" content="Le Journal de la Cosmétique">

  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Le Journal de la Cosmétique">
  <meta property="og:locale" content="fr_FR">
  <meta property="og:title" content="{e(titre)}">
  <meta property="og:description" content="{e(desc)}">
  <meta property="og:url" content="{SITE}/">
  <meta property="og:image" content="{og_img}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{e(titre)}">
  <meta name="twitter:description" content="{e(desc)}">
  <meta name="twitter:image" content="{og_img}">

  <link rel="stylesheet" href="/assets/fonts.css">
  <link rel="stylesheet" href="/assets/accueil.css">
  <link rel="stylesheet" href="/assets/search.css">
  <link rel="preload" href="/assets/fonts/archivo-var-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="/assets/fonts/fragment-mono-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="sitemap" type="application/xml" href="/sitemap.xml">

  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@graph": [
      {{
        "@type": "WebSite",
        "@id": "{SITE}/#website",
        "url": "{SITE}/",
        "name": "Le Journal de la Cosmétique",
        "alternateName": "lejournaldelacosmetique.fr",
        "description": "Média indépendant consacré aux soins, au maquillage, aux parfums, aux cheveux et à la science des formules cosmétiques.",
        "inLanguage": "fr-FR",
        "publisher": {{ "@id": "{SITE}/#organization" }},
        "potentialAction": {{
          "@type": "SearchAction",
          "target": {{ "@type": "EntryPoint", "urlTemplate": "{SITE}/recherche?q={{search_term_string}}" }},
          "query-input": "required name=search_term_string"
        }}
      }},
      {{
        "@type": "NewsMediaOrganization",
        "@id": "{SITE}/#organization",
        "name": "Le Journal de la Cosmétique",
        "alternateName": "JDC",
        "url": "{SITE}/",
        "foundingDate": "2026",
        "logo": {{
          "@type": "ImageObject",
          "url": "{SITE}/assets/favicon.svg",
          "width": 64,
          "height": 64
        }},
        "parentOrganization": {{
          "@type": "Organization",
          "name": "Triaina",
          "address": {{ "@type": "PostalAddress", "addressLocality": "Paris", "addressCountry": "FR" }}
        }},
        "publishingPrinciples": "{SITE}/notre-methode/",
        "actionableFeedbackPolicy": "{SITE}/contact/",
        "knowsAbout": ["Cosmétique", "Soin de la peau", "Maquillage", "Parfum", "Capillaire", "Ingrédients cosmétiques (INCI)"],
        "contactPoint": {{
          "@type": "ContactPoint",
          "contactType": "Rédaction",
          "email": "redaction@lejournaldelacosmetique.fr",
          "availableLanguage": "fr"
        }}
      }},
{itemlist}      {{
        "@type": "WebPage",
        "@id": "{SITE}/#webpage",
        "url": "{SITE}/",
        "name": "{js(e(titre))}",
        "isPartOf": {{ "@id": "{SITE}/#website" }},
        "about": {{ "@id": "{SITE}/#organization" }},
        "datePublished": "2026-08-13",
        "dateModified": "{dernier_iso}",
        "inLanguage": "fr-FR"
      }}
    ]
  }}
  </script>

  <script>document.documentElement.classList.add('js');</script>
</head>
"""

    # ————— à la une —————
    bloc_une = ""
    if lead:
        lignes_rail = "".join(f"""
            <a href="{a["url"]}">
              <span class="vg"><img src="{e(a["img"])}" alt="{e(a["alt"])}" loading="lazy"></span>
              <span class="tx">
                <span class="n">{e(rub(a["rubrique"])["court"])} · {e(a["type"])}</span>
                <h3>{e(a["titre"])}</h3>
                <span class="mt">{e(a["date"].replace(" 2026", ""))} — lecture {e(a["lecture"])}</span>
              </span>
            </a>""" for a in rail)
        if rail:
            corps_rail = f"""          <div class="rl">{lignes_rail}
          </div>
          <a class="tout" href="/recherche/">Tout le catalogue du journal →</a>"""
        else:
            corps_rail = """          <div class="vide">
            <p>C’est le premier article du journal. Les suivants paraissent au rythme des tests
            et des vérifications — jamais à celui des sorties de marques.</p>
            <p class="l"><a href="/notre-methode/">Notre méthode</a><a href="/a-propos/">Qui écrit le journal</a></p>
          </div>"""
        bloc_une = f"""    <section class="une" aria-labelledby="t-une">
      <div class="wrap">
        <div class="sec-t rv">
          <span class="puce"></span>
          <h2 id="t-une">À la une</h2>
          <span class="fil"></span>
          <span class="mono">{n} article{"s" if n > 1 else ""} publié{"s" if n > 1 else ""}</span>
        </div>
        <div class="plateau rv">
          <a class="lead" href="{lead["url"]}">
            <span class="visuel"><img src="{e(lead["img"])}" alt="{e(lead["alt"])}" fetchpriority="high"></span>
            <span class="texte">
              <span class="tg"><span class="ty">{e(lead["type"])}</span><span class="rb">{e(rub(lead["rubrique"])["court"])}</span></span>
              <h3>{e(lead["titre"])}</h3>
              <span class="ch">{e(lead["chapo"])}</span>
              <span class="mt"><span>{e(lead["date"])}</span><span>Lecture {e(lead["lecture"])}</span><span>Camille Laveran</span></span>
            </span>
          </a>
          <div class="rail">
            <p class="k">Également au sommaire</p>
{corps_rail}
          </div>
        </div>
      </div>
    </section>
"""

    # ————— le fil —————
    bloc_fil = ""
    if fil:
        lignes = "".join(f"""
            <a href="{a["url"]}">
              <span class="vg"><img src="{e(a["img"])}" alt="{e(a["alt"])}" loading="lazy"></span>
              <span class="ti">{e(a["titre"])}</span>
              <span class="sb"><i>{e(rub(a["rubrique"])["court"])}</i> · {e(a["type"])} · lecture {e(a["lecture"])}</span>
              <span class="da">{e(a["date"])}</span>
            </a>""" for a in fil)
        if surplus:
            lignes += f"""
            <a class="plus" href="/recherche/">
              <span class="ti">Les {len(surplus)} autres articles du journal</span>
              <span class="sb">Catalogue complet, classé par univers</span>
            </a>"""
        bloc_fil = f"""    <section class="flux" aria-labelledby="t-flux">
      <div class="wrap">
        <div class="sec-t rv">
          <span class="puce"></span>
          <h2 id="t-flux">Le fil</h2>
          <span class="fil"></span>
          <a class="mono sec-lien" href="/recherche/">Tout le catalogue →</a>
        </div>
        <div class="liste rv">{lignes}
        </div>
      </div>
    </section>
"""

    # ————— la classification illustrée —————
    def image_rubrique(r):
        p = r.get("img") or ""
        if p and os.path.exists(os.path.join(RACINE, p.lstrip("/"))):
            return p, r.get("alt", "")
        a = articles_de(r["slug"])
        return (a[0]["img"], "") if a else ("", "")

    elems = ""
    for r in RUBRIQUES:
        nb = len(articles_de(r["slug"]))
        img, _ = image_rubrique(r)
        fond = ('<span class="ph"><img src="%s" alt="" loading="lazy"></span>' % e(img)) if img \
               else '<span class="trame"></span>'
        etat = ("%s — %d article%s" % (r["num"], nb, "s" if nb > 1 else "")) if nb \
               else ("%s — à paraître" % r["num"])
        elems += ('\n          <a class="elem%s" href="/%s/">%s<span class="in">'
                  '<span class="z">%s</span><span class="sym">%s</span>'
                  '<span class="nom">%s</span><span class="ss">%s</span></span></a>'
                  % ("" if nb else " att", r["slug"], fond, etat,
                     r["sym"], e(r["nom"]), e(r["sous"])))

    # ————— les formats, peuplés depuis le corpus réel —————
    DEFINITION_TYPE = {
        "Guide": "Une catégorie prise du début à la fin : ce qu’il faut, dans quel ordre, à quelle fréquence.",
        "Décryptage": "Un actif, une allégation, une étiquette : ce que le texte dit vraiment, une fois traduit.",
        "Banc d’essai": "Des produits portés vingt-et-un jours sur deux profils de peau : ce qui tient, ce qui lâche.",
        "Enquête": "Labels sans définition, réglementation, prix : ce qui se joue derrière l’étiquette.",
    }
    FMT_LIGNES = 3

    bloc_formats = ""
    if arts:
        par_type = {}
        for a in arts:
            par_type.setdefault(a["type"], []).append(a)
        ordre = sorted(par_type, key=lambda t: (-len(par_type[t]), t))

        cols = ""
        for t in ordre:
            lot = par_type[t]
            tete, reste_t = lot[0], lot[1:1 + FMT_LIGNES]
            trop = len(lot) - 1 - len(reste_t)
            d = DEFINITION_TYPE.get(t, "")
            cols += f"""
            <div class="f-col">
              <p class="f-k"><span class="f-ty">{e(t)}</span><span class="f-nb">{len(lot)} article{"s" if len(lot) > 1 else ""}</span></p>
              {f'<p class="f-def">{e(d)}</p>' if d else ''}
              <a class="f-une" href="{tete["url"]}">
                <span class="f-ph"><img src="{e(tete["img"])}" alt="{e(tete["alt"])}" loading="lazy"></span>
                <span class="f-rb">{e(rub(tete["rubrique"])["court"])} — {e(tete["date"].replace(" 2026", ""))} · lecture {e(tete["lecture"])}</span>
                <span class="f-ti">{e(tete["titre"])}</span>
              </a>""" + "".join(f"""
              <a class="f-li" href="{a["url"]}">
                <span class="f-ti">{e(a["titre"])}</span>
                <span class="f-rb">{e(rub(a["rubrique"])["court"])} · lecture {e(a["lecture"])}</span>
              </a>""" for a in reste_t) + (f"""
              <a class="f-li f-plus" href="/recherche/">
                <span class="f-ti">Les {trop} autres</span>
                <span class="f-rb">Au catalogue</span>
              </a>""" if trop > 0 else "") + """
            </div>"""

        bloc_formats = f"""    <section class="formats" aria-labelledby="t-formats">
      <div class="wrap">
        <div class="sec-t rv">
          <span class="puce"></span>
          <h2 id="t-formats">Les formats du journal</h2>
          <span class="fil"></span>
          <span class="mono">{len(ordre)} format{"s" if len(ordre) > 1 else ""} · {n} article{"s" if n > 1 else ""}</span>
        </div>
        <div class="f-grid rv">{cols}
        </div>
        <p class="charte rv">
          <span>Sources publiques citées — règlement (CE) n° 1223/2009, base CosIng, avis de l’ANSM.</span>
          <a href="/notre-methode/">Notre méthode</a>
          <a href="/a-propos/">Qui écrit le journal</a>
        </p>
      </div>
    </section>
"""

    corps = f"""<body>
  <a class="skip" href="#contenu">Aller au contenu</a>

{topbar()}

  <header class="head">
    <div class="wrap">
      <div class="grid">
        <p class="wordmark" aria-label="Le Journal de la Cosmétique">
          <span class="w1">Le Journal</span>
          <span class="w2">de la</span>
          <span class="w3">Cosmétique</span>
        </p>
        <div class="side">
          <div class="molecule" aria-hidden="true">
            <svg viewBox="0 0 120 120" fill="none">
              <circle cx="60" cy="60" r="56" stroke="#0C0C0A" stroke-width="1" stroke-dasharray="3 5"/>
              <line x1="60" y1="60" x2="98" y2="34" stroke="#0C0C0A" stroke-width="1.6"/>
              <line x1="60" y1="60" x2="26" y2="30" stroke="#0C0C0A" stroke-width="1.6"/>
              <line x1="60" y1="60" x2="52" y2="102" stroke="#0C0C0A" stroke-width="1.6"/>
              <circle cx="60" cy="60" r="11" fill="#C8F135" stroke="#0C0C0A" stroke-width="2"/>
              <circle cx="98" cy="34" r="7" fill="#0C0C0A"/>
              <circle cx="26" cy="30" r="7" fill="#2B3BE8"/>
              <circle cx="52" cy="102" r="7" fill="#0C0C0A"/>
            </svg>
          </div>
          <p>Le média qui passe la beauté <b>au crible</b> — formules relues, prix vérifiés, promesses testées.</p>
        </div>
      </div>
      <div class="baseline">
        <span>Soin / Maquillage / Parfum / Cheveux / Corps / Science</span>
        <span>Produits achetés au prix public</span>
        <span>Aucun lien d’affiliation</span>
      </div>
    </div>
  </header>

{nav()}

  <div class="data" aria-hidden="true">
    <div class="track">
      <span>Produits achetés au prix public<i>◇</i></span>
      <span>Vingt-et-un jours de test minimum<i>◇</i></span>
      <span>Formules relues ligne à ligne<i>◇</i></span>
      <span>Aucun lien d’affiliation<i>◇</i></span>
      <span>Verdicts publiés sans droit de regard des marques<i>◇</i></span>
      <span>Produits achetés au prix public<i>◇</i></span>
      <span>Vingt-et-un jours de test minimum<i>◇</i></span>
      <span>Formules relues ligne à ligne<i>◇</i></span>
      <span>Aucun lien d’affiliation<i>◇</i></span>
      <span>Verdicts publiés sans droit de regard des marques<i>◇</i></span>
    </div>
  </div>

  <main id="contenu">

{bloc_une}{bloc_fil}
    <section class="periodique" aria-labelledby="t-univers">
      <div class="wrap">
        <div class="sec-t rv">
          <span class="puce"></span>
          <h2 id="t-univers">La classification des univers</h2>
          <span class="fil"></span>
          <span class="mono">6 éléments</span>
        </div>
        <div class="grid rv">{elems}
        </div>
      </div>
    </section>

{bloc_formats}
  </main>

"""

    reveals = """  <script>
    (function(){
      if (!('IntersectionObserver' in window)) {
        document.querySelectorAll('.rv').forEach(function(el){ el.classList.add('in'); });
        return;
      }
      var io = new IntersectionObserver(function(entries){
        entries.forEach(function(en){
          if (en.isIntersecting){ en.target.classList.add('in'); io.unobserve(en.target); }
        });
      }, { rootMargin:'0px 0px -8% 0px', threshold:.06 });
      document.querySelectorAll('.rv').forEach(function(el){ io.observe(el); });
    })();
  </script>

"""
    return tete_html + corps + pied().replace(OVERLAY, reveals + OVERLAY)


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
    arts = publies()
    urls = [("/", "daily", "1.0", arts[0]["iso"] if arts else AUJ_ISO)]
    for r in RUBRIQUES:
        # lastmod d'une rubrique = date de son article le plus récent
        lot = articles_de(r["slug"])
        lm = max(a["iso"] for a in lot) if lot else AUJ_ISO
        urls.append(("/%s/" % r["slug"], "weekly", "0.8", lm))
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
def llms_txt():
    """Carte du site pour les moteurs génératifs, peuplée depuis le CORPUS."""
    arts = publies()
    n = len(arts)

    intro = ("Le Journal de la Cosmétique est un média français indépendant consacré aux soins, au maquillage, "
             "aux parfums, aux cheveux, au corps et à la science des formules cosmétiques. "
             + ("%d articles sont publiés à ce jour." % n if n else "Les premiers articles paraîtront prochainement."))

    blocs_rub = ""
    for r in RUBRIQUES:
        lot = articles_de(r["slug"])
        if not lot:
            continue
        blocs_rub += "\n### %s\n\n" % r["titre"]
        for a in lot:
            blocs_rub += "- [%s](%s%s) — %s · lecture %s. %s\n" % (
                a["titre"], SITE, a["url"], a["type"], a["lecture"], a["chapo"])

    return """# Le Journal de la Cosmétique

> %s

Édité par Triaina (SAS, Paris), fondé en 2026. Directeur de la publication : Lucas Lecoq-Pellizzon.
Rédaction : Camille Laveran, consultante et rédactrice.

## Ce que ce média s'engage à faire

- Les produits comparés sont achetés au prix public ; aucun échantillon de marque n'entre dans un comparatif.
- Les allégations sont confrontées aux sources primaires : règlement (CE) n° 1223/2009, base CosIng, recommandations et avis publics des agences sanitaires. Les sources sont citées et cliquables.
- Chaque article distingue explicitement ce qui a été testé de ce qui a été documenté. Quand un guide ne repose pas sur un test, il le dit et précise sur quoi il repose.
- Aucun lien d'affiliation, aucun contenu sponsorisé, aucune relecture par les marques avant publication.
- Les photographies d'illustration proviennent de banques sous licence libre, sont hébergées localement et créditées ; leur provenance est consignée dans %s/images/manifeste.json.
- Les erreurs sont corrigées, datées et signalées en pied d'article quand elles changent le sens du texte.

## Articles publiés
%s
## Rubriques

- [Soin visage](%s/soin-visage/) : hydratation, actifs, protection solaire, routines
- [Maquillage](%s/maquillage/) : teint, lèvres, regard
- [Parfum](%s/parfum/) : concentrations, familles olfactives, étiquetage des allergènes
- [Cheveux](%s/cheveux/) : soins, couleur, coiffage, cuir chevelu
- [Corps](%s/corps/) : hydratation, gommage, rituels
- [Science & décryptages](%s/science/) : INCI, réglementation, actifs, niveaux de preuve

## Le média

- [À propos](%s/a-propos/) : genèse, mission, charte éditoriale, direction de la publication
- [Notre méthode](%s/notre-methode/) : protocole de test, lecture des listes INCI, hiérarchie des sources, indépendance, politique de correction
- [Contact](%s/contact/) : conditions de partenariat, demandes juridiques — contact@lejournaldelacosmetique.fr
- [Mentions légales](%s/mentions-legales/) — [Confidentialité](%s/politique-de-confidentialite/) : aucun cookie, aucun traceur, aucun fichier de visiteurs

## Formats

Guides (une catégorie prise du début à la fin), décryptages (un actif, une allégation, une étiquette),
bancs d'essai (produits portés vingt-et-un jours sur deux profils de peau) et enquêtes
(labels, réglementation, stratégies de prix). Un format n'est annoncé sur le site que lorsqu'un article l'occupe.

## Citer ce site

Les contenus sont librement citables avec mention de la source et lien vers l'article d'origine.
Les crawlers des moteurs génératifs sont explicitement autorisés (voir %s/robots.txt).
""" % (intro, SITE, blocs_rub, SITE, SITE, SITE, SITE, SITE, SITE, SITE, SITE, SITE, SITE, SITE, SITE)

# ————————————————————————————————————————————————————————————————
def versionner():
    """Estampille les feuilles de style et les scripts d'une empreinte de contenu.

    Sans cela, un CSS modifié reste servi jusqu'à 4 h par le cache CDN
    (constaté le 18 août 2026 : cf-cache-status HIT, max-age=14400).
    Une empreinte dans l'URL rend l'invalidation automatique à chaque déploiement.
    Passe idempotente : toute empreinte existante est retirée avant d'être réécrite.
    """
    import hashlib

    empreintes = {}
    def empreinte(chemin):
        if chemin not in empreintes:
            complet = os.path.join(RACINE, chemin.lstrip("/"))
            if not os.path.exists(complet):
                empreintes[chemin] = ""
            else:
                with open(complet, "rb") as f:
                    empreintes[chemin] = hashlib.sha256(f.read()).hexdigest()[:8]
        return empreintes[chemin]

    motif = re.compile(r'(/assets/[A-Za-z0-9._-]+\.(?:css|js))(\?v=[0-9a-f]+)?')
    n_fichiers = 0
    for racine, _, fichiers in os.walk(RACINE):
        if "/.git" in racine or "/docs" in racine or "/tools" in racine:
            continue
        for nom in fichiers:
            if nom != "index.html":
                continue
            chemin = os.path.join(racine, nom)
            src = open(chemin, encoding="utf-8").read()
            neuf = motif.sub(lambda m: m.group(1) + ("?v=%s" % empreinte(m.group(1)) if empreinte(m.group(1)) else ""), src)
            if neuf != src:
                open(chemin, "w", encoding="utf-8").write(neuf)
                n_fichiers += 1
    print("  ✓ %-52s %d page%s estampillée%s" % ("versionnement des assets", n_fichiers,
          "s" if n_fichiers > 1 else "", "s" if n_fichiers > 1 else ""))

# ————————————————————————————————————————————————————————————————
def ecrire(chemin, contenu):
    complet = os.path.join(RACINE, chemin)
    os.makedirs(os.path.dirname(complet), exist_ok=True)
    with open(complet, "w", encoding="utf-8") as f:
        f.write(contenu)
    print("  ✓ %-52s %6d o" % (chemin, len(contenu.encode("utf-8"))))

def main():
    print("Génération du Journal de la Cosmétique — %d articles, %d rubriques" % (len(CORPUS), len(RUBRIQUES)))
    ecrire("index.html", page_accueil())
    ecrire("assets/articles.js", index_js())
    for r in RUBRIQUES:
        ecrire("%s/index.html" % r["slug"], page_rubrique(r))
    ecrire("recherche/index.html", page_recherche())
    ecrire("sitemap.xml", sitemap())
    ecrire("llms.txt", llms_txt())
    versionner()
    print("Terminé.")

if __name__ == "__main__":
    main()
