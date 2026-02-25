(function () {
  function getCellValue(row, colIdx) {
    const cell = row.children[colIdx];
    if (!cell) return '';
    return (cell.innerText || cell.textContent || '').trim();
  }

  function isNumeric(value) {
    if (value === '' || value === null || value === undefined) return false;
    const n = Number(value);
    return !Number.isNaN(n);
  }

  function renumberFirstColumn(tbody) {
    const rows = tbody.querySelectorAll('tr');
    rows.forEach((tr, idx) => {
      const first = tr.children[0];
      if (first) first.textContent = idx + 1;
    });
  }

  function sortTable(table, colIdx, dir) {
    const tbody = table.querySelector('tbody');
    if (!tbody) return;

    const rows = Array.from(tbody.querySelectorAll('tr'));
    const multiplier = dir === 'desc' ? -1 : 1;
    rows.sort((a, b) => {
      const va = getCellValue(a, colIdx);
      const vb = getCellValue(b, colIdx);
      const bothNumeric = isNumeric(va) && isNumeric(vb);
      if (bothNumeric) return (Number(va) - Number(vb)) * multiplier;
      return va.localeCompare(vb, undefined, { numeric: true, sensitivity: 'base' }) * multiplier;
    });

    rows.forEach(row => tbody.appendChild(row));

    // If the first column is a sequence number (common in these tables), refresh it.
    if (colIdx !== 0 && table.dataset.renumber !== 'false') {
      renumberFirstColumn(tbody);
    }
  }

  function setup(table) {
    const headers = table.querySelectorAll('thead th');
    headers.forEach((th, idx) => {
      if (!th.textContent.trim() || th.classList.contains('no-sort')) return;
      th.classList.add('sortable__heading');
      th.addEventListener('click', () => {
        const current = th.getAttribute('data-sort-dir');
        const nextDir = current === 'asc' ? 'desc' : 'asc';
        table.querySelectorAll('thead th').forEach(h => h.removeAttribute('data-sort-dir'));
        th.setAttribute('data-sort-dir', nextDir);
        sortTable(table, idx, nextDir);
      });
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('table.sortable').forEach(setup);
  });
})();
