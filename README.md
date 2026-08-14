# Le Journal de la Cosmétique

Média français indépendant consacré aux soins, au maquillage, aux parfums, aux cheveux et à la science des formules cosmétiques. Édité par **Triaina** (SAS, Paris).

Site statique, sans dépendance ni étape de build : du HTML, du CSS et un peu de JavaScript vanilla.

---

## Démarrer en local

```bash
PORT=8173 node .claude/serve.mjs
```

Puis ouvrir <http://localhost:8173>. Aucune installation préalable : `serve.mjs` est un petit serveur statique sans dépendance.

---

## Structure

```
index.html                     Accueil
soin-visage/ maquillage/       Les 6 rubriques (générées)
parfum/ cheveux/ corps/
decryptages/
recherche/                     Recherche + catalogue (générée, noindex)
a-propos/                      Le média, la charte, la direction de publication
notre-methode/                 Protocole de test, indice de preuve, sources
contact/                       Formulaire et conditions de partenariat
mentions-legales/              Informations LCEN + santé & cosmétovigilance
politique-de-confidentialite/  RGPD — zéro cookie, zéro traceur

assets/
  fonts.css  fonts/            Archivo + Fragment Mono, auto-hébergées
  pages.css                    Design system des pages internes
  search.css  search.js        Recherche : overlay + page
  site.js                      Comportements communs (date du jour)
  articles.js                  Index de recherche (généré)
  favicon.svg

tools/generer.py               Générateur — source de vérité du contenu
robots.txt  sitemap.xml  llms.txt
```

---

## Publier un article

Le contenu a **une seule source de vérité** : le `CORPUS` de `tools/generer.py`.

1. Écrire la page de l'article (par exemple `guides/soin-visage/creme-hydratante/index.html`).
2. Ajouter une ligne au `CORPUS` — un modèle commenté figure en tête de liste.
3. Régénérer :

```bash
python3 tools/generer.py
```

L'article apparaît alors automatiquement dans sa rubrique, dans la recherche et dans le `sitemap.xml`. **Ne pas éditer à la main** les fichiers générés : les six pages de rubrique, `recherche/index.html`, `assets/articles.js` et `sitemap.xml`.

---

## Design

Direction artistique « Labo » : grille suisse, blanc cassé `#FBFBF4`, noir `#0C0C0A`, vert acide `#C8F135` en surlignage, cobalt `#2B3BE8` pour les libellés. Typographie **Archivo** (variable, largeur 62–125 %) pour les titres et le texte, **Fragment Mono** pour les données, références et horodatages.

Règles tenues sur toutes les pages : un seul `h1`, repères sémantiques et `aria-label`, lien d'évitement, `:focus-visible`, contrastes AA, aucun débordement horizontal en mobile, page correcte sans JavaScript, `prefers-reduced-motion` respecté.

---

## SEO / GEO

- JSON-LD sur chaque page (`WebSite` + `SearchAction`, `NewsMediaOrganization`, `CollectionPage`, `BreadcrumbList`)
- `robots.txt` autorisant explicitement les crawlers IA, avec `Content-Signal`
- `llms.txt` décrivant le média et sa méthode pour les moteurs de réponse
- `sitemap.xml` généré ; `/recherche/` en `noindex` et hors sitemap
- Polices auto-hébergées et préchargées, aucun appel à Google Fonts, aucun cookie, aucun traceur

---

## Éditorial

Le site est en phase de lancement : **aucun article n'est encore publié**, et rien sur le site ne prétend le contraire. Les engagements affichés (produits achetés au prix public, 21 jours de test minimum, deux profils de peau, sources publiques citées, zéro affiliation, relecture santé) sont des règles à tenir, pas des résultats passés.

Directeur de la publication : Lucas Lecoq-Pellizzon, président de Triaina.

---

© 2026 Triaina — Paris. Tous droits réservés.
