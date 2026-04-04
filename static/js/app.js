// ── DARK MODE ────────────────────────────────────────────────
function toggleTheme() {
  const html = document.documentElement;
  const isDark = html.getAttribute('data-theme') === 'dark';
  html.setAttribute('data-theme', isDark ? 'light' : 'dark');
  localStorage.setItem('theme', isDark ? 'light' : 'dark');
  document.getElementById('themeIcon').textContent = isDark ? '◑' : '●';
}

// Apply saved theme on load
(function() {
  const saved = localStorage.getItem('theme') || 'light';
  document.documentElement.setAttribute('data-theme', saved);
  const icon = document.getElementById('themeIcon');
  if (icon) icon.textContent = saved === 'dark' ? '●' : '◑';
})();

// ── SIDEBAR ──────────────────────────────────────────────────
function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
}

// Close sidebar on outside click (mobile)
document.addEventListener('click', function(e) {
  const sidebar = document.getElementById('sidebar');
  if (!sidebar) return;
  if (window.innerWidth <= 768 && sidebar.classList.contains('open')) {
    if (!sidebar.contains(e.target) && !e.target.classList.contains('mobile-menu-btn')) {
      sidebar.classList.remove('open');
    }
  }
});

// ── GLOBAL SEARCH ────────────────────────────────────────────
const searchInput = document.getElementById('globalSearch');
const searchDropdown = document.getElementById('searchResults');

if (searchInput) {
  let debounce;
  searchInput.addEventListener('input', function() {
    clearTimeout(debounce);
    const q = this.value.trim();
    if (!q) { searchDropdown.style.display = 'none'; return; }
    debounce = setTimeout(() => doSearch(q), 250);
  });

  searchInput.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      searchDropdown.style.display = 'none';
      this.value = '';
    }
  });

  document.addEventListener('click', function(e) {
    if (!searchInput.contains(e.target) && !searchDropdown.contains(e.target)) {
      searchDropdown.style.display = 'none';
    }
  });
}

async function doSearch(q) {
  try {
    const res = await fetch(`/search?q=${encodeURIComponent(q)}`);
    const data = await res.json();
    renderSearchResults(data);
  } catch (e) {
    console.error('Search error', e);
  }
}

function renderSearchResults(results) {
  if (!results.length) {
    searchDropdown.innerHTML = '<div class="search-result-item"><span style="color:var(--text-muted)">No cadets found</span></div>';
    searchDropdown.style.display = 'block';
    return;
  }
  searchDropdown.innerHTML = results.map(r => `
    <a href="/cadet/${r.id}" class="search-result-item">
      <span class="sr-rank">${r.rank}</span>
      <div>
        <div class="sr-name">${r.name}</div>
        <div class="sr-flight">${r.flight}</div>
      </div>
    </a>
  `).join('');
  searchDropdown.style.display = 'block';
}
