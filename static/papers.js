// Toggle BibTeX entries via the inline [bibtex] link and copy to clipboard.
//
// Progressive enhancement: the BibTeX lives in a native <details> element, so
// if this script never runs the <summary> still reveals the entry. When JS is
// on, the inline [bibtex] link toggles the <details> and the copy button works.
document.addEventListener('DOMContentLoaded', function () {
  // Reveal/hide a paper's BibTeX via its inline [bibtex] link.
  document.querySelectorAll('.bibtex-toggle').forEach(function (toggle) {
    toggle.addEventListener('click', function (e) {
      e.preventDefault();
      var id = toggle.getAttribute('href').slice(1);
      var details = document.getElementById(id);
      if (details) {
        details.open = !details.open;
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
