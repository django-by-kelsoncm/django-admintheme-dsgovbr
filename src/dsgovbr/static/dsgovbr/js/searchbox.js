document.addEventListener('DOMContentLoaded', function() {
  const searchInput = document.getElementById('searchbox');
  if (!searchInput) return;

  const autocompleteUrl = searchInput.getAttribute('data-autocomplete-url');
  if (!autocompleteUrl) return;

  // Create or select the autocomplete container
  const resultsContainer = document.getElementById('searchbox-autocomplete-results');
  if (!resultsContainer) return;

  let debounceTimer;

  searchInput.addEventListener('input', function() {
    clearTimeout(debounceTimer);
    const query = searchInput.value.trim();

    if (query.length < 2) {
      clearResults();
      return;
    }

    debounceTimer = setTimeout(function() {
      fetchSuggestions(query);
    }, 300);
  });

  // Hide on click outside
  document.addEventListener('click', function(e) {
    if (!searchInput.contains(e.target) && !resultsContainer.contains(e.target)) {
      clearResults();
    }
  });

  // Handle escape key
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      clearResults();
    }
  });

  function fetchSuggestions(query) {
    const url = new URL(autocompleteUrl, window.location.origin);
    url.searchParams.set('q', query);

    fetch(url)
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        // data is expected to be an array of strings or list of objects
        // We will support both: ["opt1", "opt2"] or [{"label": "opt1", "value": "opt1"}]
        displayResults(data);
      })
      .catch(error => {
        console.error('Error fetching autocomplete suggestions:', error);
      });
  }

  function displayResults(items) {
    resultsContainer.innerHTML = '';
    if (!items || items.length === 0) {
      const emptyDiv = document.createElement('div');
      emptyDiv.className = 'list-group-item empty-result';
      emptyDiv.textContent = 'Nenhum resultado encontrado';
      resultsContainer.appendChild(emptyDiv);
      resultsContainer.classList.add('active');
      return;
    }

    items.forEach(function(item) {
      let label = '';
      let value = '';
      if (typeof item === 'object' && item !== null) {
        label = item.label || item.value || '';
        value = item.value || item.label || '';
      } else {
        label = item;
        value = item;
      }

      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'list-group-item list-group-item-action';
      button.textContent = label;
      button.addEventListener('click', function() {
        searchInput.value = value;
        clearResults();
        // Submit the parent form if it exists
        const form = searchInput.closest('form');
        if (form) {
          form.submit();
        }
      });

      resultsContainer.appendChild(button);
    });

    resultsContainer.classList.add('active');
  }

  function clearResults() {
    resultsContainer.innerHTML = '';
    resultsContainer.classList.remove('active');
  }
});
