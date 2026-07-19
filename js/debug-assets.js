(function () {
  // #region agent log
  var sessionId = 'c03df7';
  var endpoint = 'http://127.0.0.1:7826/ingest/e06b2f14-f33e-4bc6-935b-85443f1daeb1';
  function logAssetIssue(hypothesisId, message, data) {
    fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Debug-Session-Id': sessionId },
      body: JSON.stringify({
        sessionId: sessionId,
        runId: 'asset-check',
        hypothesisId: hypothesisId,
        location: 'js/debug-assets.js',
        message: message,
        data: data,
        timestamp: Date.now()
      })
    }).catch(function () {});
  }

  window.addEventListener('error', function (event) {
    if (event.target && (event.target.tagName === 'IMG' || event.target.tagName === 'LINK' || event.target.tagName === 'SCRIPT')) {
      logAssetIssue('C', 'resource-load-error', {
        tag: event.target.tagName,
        src: event.target.src || event.target.href || ''
      });
    }
  }, true);

  window.addEventListener('load', function () {
    var localResources = performance.getEntriesByType('resource').filter(function (entry) {
      return entry.name.indexOf(window.location.origin) === 0;
    });
    localResources.forEach(function (entry) {
      if (entry.transferSize === 0 && entry.decodedBodySize === 0 && entry.duration > 0) {
        logAssetIssue('A', 'possible-missing-resource', { url: entry.name, duration: entry.duration });
      }
    });
    logAssetIssue('B', 'page-load-summary', {
      page: window.location.pathname,
      resourceCount: localResources.length
    });
  });
  // #endregion
})();
