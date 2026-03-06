(function (global) {
  function setupAjaxTable(config) {
    const tbody = document.querySelector(config.tbodySelector);
    const renderRow = config.rowRenderer || (item => `<tr><td>${JSON.stringify(item)}</td></tr>`);
    const emptyRow = config.emptyRow || `<tr><td colspan="${config.emptyColspan || 1}"></td></tr>`;
    return function Search(page = 1) {
      const payload = (config.buildPayload && config.buildPayload(page)) || { page };
      $.ajax({
        type: config.method || "POST",
        url: config.url,
        data: JSON.stringify(payload),
        contentType: "application/json; charset=utf-8",
        success: function (response, textStatus) {
          const rows = (config.extractRows && config.extractRows(response)) || response[config.rowsKey || 'data'] || [];
          tbody.innerHTML = (rows && rows.length) ? rows.map(renderRow).join('') : emptyRow;
          const pagination = (response && response[config.paginationKey || 'pagination']) || null;
          if (config.pagination && pagination) {
            config.pagination(pagination);
          }
        }
      });
    };
  }

  function renderPagination(ids) {
    return function (pagination) {
      if (!pagination) return;
      ids.forEach(id => pagination2(pagination.page, pagination.total_pages, id));
    };
  }

  function confirmDeleteWithPrecheck(opts) {
    $.ajax({
      type: opts.method || "POST",
      url: opts.precheckUrl,
      data: JSON.stringify(opts.payload || {}),
      contentType: "application/json; charset=utf-8",
      success: function (response) {
        const message = opts.messageParser ? opts.messageParser(response) : response;
        if (!confirm(message)) return;
        $.post(opts.deleteUrl, opts.payload || {}).done(() => {
          if (opts.redirect) {
            window.location.href = opts.redirect;
          } else {
            window.location.reload();
          }
        });
      }
    });
  }

  function redirectWithParams(baseUrl, params) {
    const search = new URLSearchParams();
    Object.entries(params || {}).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== '') search.append(k, v);
    });
    const qs = search.toString();
    window.location.href = qs ? `${baseUrl}?${qs}` : baseUrl;
  }

  global.ListPage = {
    setupAjaxTable,
    renderPagination,
    confirmDeleteWithPrecheck,
    redirectWithParams,
  };
})(window);
