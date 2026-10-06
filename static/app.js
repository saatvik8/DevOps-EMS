// Theme toggle (remembered in the browser)
(function () {
  var saved = localStorage.getItem("theme");
  if (saved) document.documentElement.setAttribute("data-theme", saved);
})();

function toggleTheme() {
  var cur = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", cur);
  localStorage.setItem("theme", cur);
  var b = document.getElementById("themeBtn");
  if (b) b.textContent = cur === "dark" ? "☀️" : "🌙";
}

document.addEventListener("DOMContentLoaded", function () {
  var b = document.getElementById("themeBtn");
  if (b) b.textContent = document.documentElement.getAttribute("data-theme") === "dark" ? "☀️" : "🌙";

  // Toasts auto-dismiss
  document.querySelectorAll(".toast").forEach(function (t) {
    t.addEventListener("click", function () { t.remove(); });
    setTimeout(function () { t.remove(); }, 4000);
  });

  // Live search filter
  var search = document.getElementById("search");
  if (search) {
    search.addEventListener("input", function () {
      var q = search.value.toLowerCase();
      var shown = 0;
      document.querySelectorAll("#empTable tbody tr[data-row]").forEach(function (tr) {
        var text = tr.getAttribute("data-search");
        var match = text.indexOf(q) !== -1;
        tr.style.display = match ? "" : "none";
        if (match) shown++;
      });
      var none = document.getElementById("noMatch");
      if (none) none.style.display = shown ? "none" : "";
    });
  }
});

function toggleAdd() {
  document.getElementById("addForm").classList.toggle("open");
}

function togglePw() {
  var p = document.getElementById("pw");
  var btn = document.getElementById("pwBtn");
  p.type = p.type === "password" ? "text" : "password";
  btn.textContent = p.type === "password" ? "Show" : "Hide";
}
