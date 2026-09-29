// Research page: show only the chosen research area's card. No dependencies.
// The pure function is exported for the Node-based tests in tests/test_site.py.
var LabResearch = {
  shows: function (topic, cardTopic) {
    return topic === 'all' || topic === cardTopic;
  }
};

if (typeof module !== 'undefined' && module.exports) {
  module.exports = LabResearch;
}

if (typeof document !== 'undefined') {
  document.addEventListener('DOMContentLoaded', function () {
    var chips = Array.prototype.slice.call(document.querySelectorAll('.research-filter .pub-filter-chip'));
    var cards = Array.prototype.slice.call(document.querySelectorAll('.research-card'));
    chips.forEach(function (chip) {
      chip.addEventListener('click', function () {
        var topic = chip.dataset.filter;
        chips.forEach(function (c) {
          c.classList.toggle('is-active', c === chip);
          c.setAttribute('aria-pressed', c === chip ? 'true' : 'false');
        });
        cards.forEach(function (card) {
          card.hidden = !LabResearch.shows(topic, card.dataset.topic);
        });
      });
    });
  });
}
