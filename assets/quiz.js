/* ————————————————————————————————————————————————
   Quiz d'article — Le Journal de la Cosmétique
   Correction immédiate, explication par question, score.
   Les bonnes réponses sont portées par data-juste dans le HTML :
   la page reste correcte et lisible sans JavaScript.
   ———————————————————————————————————————————————— */
(function () {
  'use strict';

  document.querySelectorAll('[data-quiz]').forEach(function (quiz) {
    var items = [].slice.call(quiz.querySelectorAll('.qz-item'));
    var total = items.length;
    var scoreEl = quiz.querySelector('[data-score]');
    var rejouer = quiz.querySelector('.rejouer');
    var repondus = {};

    function majScore() {
      var justes = 0, faits = 0;
      Object.keys(repondus).forEach(function (k) {
        faits++;
        if (repondus[k]) justes++;
      });
      if (!scoreEl) return;
      scoreEl.innerHTML = faits
        ? '<b>' + justes + '</b> / ' + total + (faits < total ? ' — ' + (total - faits) + ' restante' + (total - faits > 1 ? 's' : '') : ' — terminé')
        : '<b>0</b> / ' + total;
    }

    items.forEach(function (item, i) {
      var labels = [].slice.call(item.querySelectorAll('.qz-opts label'));
      labels.forEach(function (label) {
        var input = label.querySelector('input');
        if (!input) return;
        input.addEventListener('change', function () {
          if (item.classList.contains('repondu')) return;
          var juste = label.hasAttribute('data-juste');
          repondus[i] = juste;
          item.classList.add('repondu');
          labels.forEach(function (l) {
            var inp = l.querySelector('input');
            if (inp) inp.disabled = true;
            if (l.hasAttribute('data-juste')) l.classList.add('juste');
            else if (l === label) l.classList.add('faux');
          });
          majScore();
        });
      });
    });

    if (rejouer) {
      rejouer.addEventListener('click', function () {
        repondus = {};
        items.forEach(function (item) {
          item.classList.remove('repondu');
          item.querySelectorAll('.qz-opts label').forEach(function (l) {
            l.classList.remove('juste', 'faux');
            var inp = l.querySelector('input');
            if (inp) { inp.disabled = false; inp.checked = false; }
          });
        });
        majScore();
        quiz.scrollIntoView({ block: 'start', behavior: 'smooth' });
      });
    }

    majScore();
  });
})();
