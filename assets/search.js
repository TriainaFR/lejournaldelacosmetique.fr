/* ————————————————————————————————————————————————
   Recherche — Le Journal de la Cosmétique
   Deux modes, une seule source (window.JDC_ARTICLES) :
   · overlay        — sur toute page contenant #rch
   · page /recherche/ — filtre la liste et lit ?q=
   Sans JS, la page /recherche/ affiche le corpus complet
   en HTML : rien n'est perdu.
   ———————————————————————————————————————————————— */
(function () {
  'use strict';

  var CORPUS = window.JDC_ARTICLES || [];
  /* les pages institutionnelles sont cherchables mais ne comptent pas comme articles */
  var NB_ARTICLES = CORPUS.filter(function (a) { return a.type !== 'Page'; }).length;

  /* — normalisation : insensible aux accents et à la casse — */
  function norm(s) {
    return (s || '')
      .toString()
      .toLowerCase()
      .normalize('NFD')
      .replace(/[̀-ͯ]/g, '')
      .replace(/[’']/g, ' ')
      .replace(/[^a-z0-9\s%€-]/g, ' ')
      .replace(/\s+/g, ' ')
      .trim();
  }

  function mots(q) {
    return norm(q).split(' ').filter(function (m) { return m.length > 1; });
  }

  /* — score : titre > rubrique > mots-clés — */
  function score(item, termes) {
    var t = norm(item.titre), r = norm(item.rubrique), k = norm((item.cles || []).join(' ')), ty = norm(item.type);
    var total = 0;
    for (var i = 0; i < termes.length; i++) {
      var m = termes[i], trouve = false;
      if (t.indexOf(m) === 0) { total += 60; trouve = true; }
      else if (t.indexOf(' ' + m) > -1) { total += 45; trouve = true; }
      else if (t.indexOf(m) > -1) { total += 30; trouve = true; }
      if (r.indexOf(m) > -1) { total += 18; trouve = true; }
      if (ty.indexOf(m) > -1) { total += 12; trouve = true; }
      if (k.indexOf(m) > -1) { total += 10; trouve = true; }
      if (!trouve) return 0; // tous les termes doivent apparaître
    }
    return total;
  }

  function chercher(q) {
    var termes = mots(q);
    if (!termes.length) return [];
    return CORPUS
      .map(function (a) { return { a: a, s: score(a, termes) }; })
      .filter(function (o) { return o.s > 0; })
      .sort(function (x, y) { return y.s - x.s || x.a.titre.localeCompare(y.a.titre, 'fr'); })
      .map(function (o) { return o.a; });
  }

  /* — surlignage des termes dans le titre — */
  function surligner(titre, q) {
    var termes = mots(q);
    if (!termes.length) return echapper(titre);
    var nt = norm(titre), zones = [];
    termes.forEach(function (m) {
      var d = 0, i;
      while ((i = nt.indexOf(m, d)) > -1) { zones.push([i, i + m.length]); d = i + m.length; }
    });
    if (!zones.length) return echapper(titre);
    zones.sort(function (a, b) { return a[0] - b[0]; });
    var fusion = [zones[0]];
    for (var j = 1; j < zones.length; j++) {
      var last = fusion[fusion.length - 1];
      if (zones[j][0] <= last[1]) { last[1] = Math.max(last[1], zones[j][1]); }
      else { fusion.push(zones[j]); }
    }
    /* norm() conserve la longueur des caractères latins usuels : l'index reste fiable */
    var out = '', pos = 0;
    fusion.forEach(function (z) {
      if (z[0] > titre.length) return;
      out += echapper(titre.slice(pos, z[0])) + '<mark>' + echapper(titre.slice(z[0], z[1])) + '</mark>';
      pos = z[1];
    });
    return out + echapper(titre.slice(pos));
  }

  function echapper(s) {
    return (s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  function ligne(a, q) {
    return '<a href="' + a.url + '">' +
      '<span class="t">' + surligner(a.titre, q) + '</span>' +
      '<span class="rb">' + echapper(a.rubrique) + (a.type ? ' — ' + echapper(a.type) : '') + '</span>' +
      '<span class="mt">' + echapper(a.lecture || '') + '</span>' +
      '</a>';
  }

  /* ————————————————— overlay ————————————————— */
  var boite = document.getElementById('rch');
  if (boite) {
    var champ = boite.querySelector('input'),
        res = boite.querySelector('.rch-res'),
        etat = boite.querySelector('.rch-etat .nb'),
        sel = -1,
        courant = [],
        rendu = '';

    function afficher(q) {
      courant = chercher(q);
      sel = -1;
      if (!q.trim()) {
        var suggestions = CORPUS.filter(function (a) { return a.mis_en_avant; }).slice(0, 6);
        res.innerHTML = suggestions.map(function (a) { return ligne(a, ''); }).join('');
        if (etat) etat.textContent = 'Suggestions';
        return;
      }
      if (!courant.length) {
        res.innerHTML = '<div class="rch-vide"><p>Aucun résultat pour « ' + echapper(q) +' ».</p>' +
          '<p class="s">Essayez « rétinol », « SPF », « INCI », « parfum »…</p></div>';
        if (etat) etat.textContent = '0 résultat';
        return;
      }
      res.innerHTML = courant.slice(0, 24).map(function (a) { return ligne(a, q); }).join('');
      if (etat) etat.textContent = courant.length + (courant.length > 1 ? ' résultats' : ' résultat');
    }

    function ouvrir() {
      boite.classList.add('on');
      document.documentElement.style.overflow = 'hidden';
      afficher(champ.value);
      setTimeout(function () { champ.focus(); champ.select(); }, 20);
    }
    function fermer() {
      boite.classList.remove('on');
      document.documentElement.style.overflow = '';
    }

    document.querySelectorAll('[data-rch-open]').forEach(function (b) {
      b.addEventListener('click', function (e) { e.preventDefault(); ouvrir(); });
    });
    boite.querySelector('.esc').addEventListener('click', fermer);
    boite.addEventListener('click', function (e) { if (e.target === boite) fermer(); });
    champ.addEventListener('input', function () { afficher(champ.value); });

    champ.addEventListener('keydown', function (e) {
      var liens = res.querySelectorAll('a');
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        e.preventDefault();
        if (!liens.length) return;
        if (sel > -1 && liens[sel]) liens[sel].classList.remove('sel');
        sel = e.key === 'ArrowDown'
          ? (sel + 1) % liens.length
          : (sel <= 0 ? liens.length - 1 : sel - 1);
        liens[sel].classList.add('sel');
        liens[sel].scrollIntoView({ block: 'nearest' });
      } else if (e.key === 'Enter') {
        if (sel > -1 && liens[sel]) { e.preventDefault(); window.location.href = liens[sel].getAttribute('href'); }
        else if (champ.value.trim()) { e.preventDefault(); window.location.href = '/recherche/?q=' + encodeURIComponent(champ.value.trim()); }
      }
    });

    document.addEventListener('keydown', function (e) {
      var ouvert = boite.classList.contains('on');
      if (e.key === 'Escape' && ouvert) { fermer(); return; }
      if ((e.key === 'k' || e.key === 'K') && (e.metaKey || e.ctrlKey)) { e.preventDefault(); ouvert ? fermer() : ouvrir(); return; }
      var cible = e.target.tagName;
      if (e.key === '/' && !ouvert && cible !== 'INPUT' && cible !== 'TEXTAREA' && cible !== 'SELECT') {
        e.preventDefault(); ouvrir();
      }
    });
  }

  /* ————————————————— page /recherche/ ————————————————— */
  var page = document.getElementById('rch-page');
  if (page) {
    var pchamp = document.getElementById('rch-page-champ'),
        pres = document.getElementById('rch-page-res'),
        petat = document.getElementById('rch-page-etat'),
        statique = document.getElementById('rch-page-tout');

    function rendrePage(q) {
      var url = new URL(window.location.href);
      if (q.trim()) { url.searchParams.set('q', q.trim()); } else { url.searchParams.delete('q'); }
      window.history.replaceState(null, '', url.pathname + url.search);

      if (!q.trim()) {
        if (statique) statique.hidden = false;
        pres.innerHTML = '';
        petat.textContent = NB_ARTICLES + ' articles au catalogue';
        return;
      }
      if (statique) statique.hidden = true;
      var trouves = chercher(q);
      if (!trouves.length) {
        pres.innerHTML = '<div class="rch-vide"><p>Aucun résultat pour « ' + echapper(q) + ' ».</p>' +
          '<p class="s">Essayez « rétinol », « SPF 50 », « INCI », « parfum »…</p></div>';
        petat.textContent = '0 résultat';
        return;
      }
      pres.innerHTML = trouves.map(function (a) { return ligne(a, q); }).join('');
      petat.textContent = trouves.length + (trouves.length > 1 ? ' résultats' : ' résultat');
    }

    var q0 = new URLSearchParams(window.location.search).get('q') || '';
    if (q0) pchamp.value = q0;
    rendrePage(q0);
    pchamp.addEventListener('input', function () { rendrePage(pchamp.value); });
    pchamp.addEventListener('keydown', function (e) { if (e.key === 'Enter') e.preventDefault(); });
    if (!q0) setTimeout(function () { pchamp.focus(); }, 40);
  }
})();
