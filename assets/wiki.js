document.querySelectorAll('[data-wiki-search]').forEach(input => {
  const section = input.closest('.wiki-reference-data');
  const rows = [...section.querySelectorAll('tbody tr')];
  const count = document.createElement('p');
  count.className = 'meta';
  count.setAttribute('role', 'status');
  input.closest('label').after(count);
  function filter() {
    const query = input.value.trim().toLocaleLowerCase();
    let visible = 0;
    rows.forEach(row => {
      row.hidden = !row.textContent.toLocaleLowerCase().includes(query);
      if (!row.hidden) visible++;
    });
    count.textContent = `${visible} / ${rows.length}개 항목`;
  }
  input.addEventListener('input', filter);
  filter();
});
