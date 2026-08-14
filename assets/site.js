/* ————————————————————————————————————————————————
   Comportements communs à toutes les pages.
   Sans JS, les valeurs de repli du HTML restent justes.
   ———————————————————————————————————————————————— */
(function () {
  'use strict';

  /* Date du jour — remplace le contenu de [data-date-jour].
     Repli HTML : « Édition du jour ». */
  var cibles = document.querySelectorAll('[data-date-jour]');
  if (cibles.length) {
    var d = new Date();
    var txt;
    try {
      txt = d.toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
      txt = txt.charAt(0).toUpperCase() + txt.slice(1);
    } catch (e) {
      txt = null;
    }
    if (txt) {
      cibles.forEach(function (el) { el.textContent = txt; });
    }
  }
})();
