// Toggle + copy BibTeX entries on the papers page.
document.addEventListener('DOMContentLoaded', function () {
  // Reveal/hide a paper's BibTeX block.
  document.querySelectorAll('.pub a[href$="-bibtex"]').forEach(function (toggle) {
    toggle.addEventListener('click', function (e) {
      e.preventDefault();
      var id = toggle.getAttribute('href').slice(1);
      var target = document.getElementById(id);
      if (target) {
        target.hidden = !target.hidden;
      }
    });
  });

  // Copy the BibTeX text to the clipboard.
  document.querySelectorAll('.bibtex-copy').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var wrap = btn.closest('.bibtex-wrap');
      var code = wrap && wrap.querySelector('pre code');
      if (!code) return;
      var text = code.textContent;
      function done() {
        var old = btn.textContent;
        btn.textContent = 'copied!';
        setTimeout(function () { btn.textContent = old; }, 1200);
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, function () { fallbackCopy(text, done); });
      } else {
        fallbackCopy(text, done);
      }
    });
  });

  function fallbackCopy(text, done) {
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand('copy'); } catch (e) {}
    document.body.removeChild(ta);
    done();
  }
});
