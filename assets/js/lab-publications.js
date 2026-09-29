// Publications page: search and research-area filter, abstract toggles. No dependencies.
// The pure functions are exported for the Node-based tests in tests/test_site.py.
var LabPublications = {
  // Lower-case search terms from the query box.
  terms: function (query) {
    return query.toLowerCase().split(/\s+/).filter(Boolean);
  },
  // entry: {topic, search, abstract} (lower-cased data attributes of a .pub-entry)
  matches: function (entry, topic, terms, includeAbstract) {
    if (topic !== 'all' && entry.topic !== topic) return false;
    var text = entry.search + (includeAbstract ? ' ' + entry.abstract : '');
    return terms.every(function (term) { return text.indexOf(term) !== -1; });
  },
  statusText: function (shown, scope, query) {
    var text = 'Showing ' + shown + ' publication' + (shown === 1 ? '' : 's') + ' for ' + scope;
    if (query) text += ' matching “' + query + '”';
    return text + '.';
  }
};

if (typeof module !== 'undefined' && module.exports) {
  module.exports = LabPublications;
}

if (typeof document !== 'undefined') {
  document.addEventListener('DOMContentLoaded', function () {
    var search = document.getElementById('pub-search');
    var withAbstract = document.getElementById('pub-search-abstract');
    var status = document.getElementById('pub-filter-status');
    var empty = document.querySelector('.pub-empty');
    var chips = Array.prototype.slice.call(document.querySelectorAll('.pub-filter-chip'));
    var entries = Array.prototype.slice.call(document.querySelectorAll('.pub-entry'));
    var groups = Array.prototype.slice.call(document.querySelectorAll('.pub-year-group'));
    if (!search || !status || !entries.length) return;
    var topic = 'all';

    function apply() {
      var terms = LabPublications.terms(search.value);
      var shown = 0;
      entries.forEach(function (entry) {
        var ok = LabPublications.matches(entry.dataset, topic, terms, withAbstract.checked);
        entry.parentElement.hidden = !ok;
        if (ok) shown += 1;
      });
      groups.forEach(function (group) {
        group.hidden = !group.querySelector('li:not([hidden])');
      });
      var chip = chips.filter(function (c) { return c.dataset.filter === topic; })[0];
      var scope = topic === 'all' ? 'all topics' : chip.textContent.trim();
      status.textContent = LabPublications.statusText(shown, scope, search.value.trim());
      if (empty) empty.hidden = shown !== 0;
    }

    chips.forEach(function (chip) {
      chip.addEventListener('click', function () {
        topic = chip.dataset.filter;
        chips.forEach(function (c) {
          c.classList.toggle('is-active', c === chip);
          c.setAttribute('aria-pressed', c === chip ? 'true' : 'false');
        });
        apply();
      });
    });
    search.addEventListener('input', apply);
    withAbstract.addEventListener('change', apply);

    Array.prototype.forEach.call(document.querySelectorAll('.pub-abstract-toggle'), function (button) {
      button.addEventListener('click', function () {
        var box = document.getElementById(button.getAttribute('aria-controls'));
        var open = button.getAttribute('aria-expanded') === 'true';
        button.setAttribute('aria-expanded', open ? 'false' : 'true');
        box.hidden = open;
      });
    });
  });
}
