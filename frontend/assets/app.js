/**
 * Frontend scaffold (vanilla JS).
 *
 * TODO: Implement:
 * - fetch `/api/districts` and render the ranking table (#rows)
 * - when a row is clicked, fetch `/api/districts/{id}/package` and render the detail panel (#detail)
 * - optional filters:
 *   - search (#q)
 *   - risk filter (#risk)
 */

async function boot() {
  // Placeholder so the page loads even before the API is implemented.
  const detail = document.getElementById("detail");
  if (detail) {
    detail.innerHTML =
      '<div class="muted">Frontend scaffold ready. Next: implement API + wire up table/detail rendering.</div>';
  }
}

boot();
