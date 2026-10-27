"use strict";
document.querySelectorAll("[data-filter-group]").forEach(group => {
  const search = group.querySelector("[data-search]");
  const category = group.querySelector("[data-category-filter]");
  const rows = [...group.querySelectorAll("[data-record]")];
  const corpus = rows.map(row => row.textContent.toLocaleLowerCase());
  const update = () => {
    const terms = search.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    let visible = 0;
    rows.forEach((row, index) => {
      const matches = terms.every(term => corpus[index].includes(term)) && (!category || !category.value || category.value === row.dataset.category);
      row.hidden = !matches;
      visible += Number(matches);
    });
    group.querySelector("[data-count]").textContent = `${visible} of ${rows.length} shown`;
    group.querySelector("[data-empty]").hidden = visible !== 0;
  };
  search.addEventListener("input", update);
  category?.addEventListener("change", update);
  group.querySelector("[data-reset]").addEventListener("click", () => {
    search.value = "";
    if (category) category.value = "";
    update();
    search.focus();
  });
  update();
});
const timezone = document.querySelector("#timezone");
if (timezone) {
  const updateTimes = () => {
    const options = {dateStyle: "medium", timeStyle: "short"};
    if (timezone.value === "UTC") options.timeZone = "UTC";
    const zone = timezone.value === "UTC" ? "UTC" : Intl.DateTimeFormat().resolvedOptions().timeZone;
    document.querySelectorAll("time[datetime]").forEach(time => {
      time.textContent = `${new Intl.DateTimeFormat(undefined, options).format(new Date(time.dateTime))} ${zone}`;
    });
  };
  timezone.addEventListener("change", updateTimes);
  updateTimes();
}
document.querySelectorAll("[data-enhancement]").forEach(node => { node.hidden = false; });
function revealAnchor() {
  const target = document.getElementById(location.hash.slice(1));
  if (target?.matches("[data-record]")) {
    if (target.hidden) {
      const group = target.closest("[data-filter-group]");
      const search = group?.querySelector("[data-search]");
      const category = group?.querySelector("[data-category-filter]");
      if (search) {
        search.value = "";
        if (category) category.value = "";
        search.dispatchEvent(new Event("input", {bubbles: true}));
      }
    }
    if (target.tagName === "DETAILS") target.open = true;
    (target.querySelector("summary") || target).focus({preventScroll: true});
    target.scrollIntoView({block: "start"});
  }
}
document.addEventListener("click", event => {
  const link = event.target instanceof Element ? event.target.closest('a[href^="#"]') : null;
  if (link?.hash && link.hash === location.hash) revealAnchor();
});
window.addEventListener("hashchange", revealAnchor);
revealAnchor();
