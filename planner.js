"use strict";

function safeGigabytes(value) {
  const number = Number(value);
  return Number.isFinite(number) && number > 0 ? number : 0;
}

function roundGigabytes(value) {
  return Math.round((value + Number.EPSILON) * 100) / 100;
}

function calculatePlan(input = {}) {
  const currentFree = safeGigabytes(input.currentFree);
  const goalFree = safeGigabytes(input.goalFree);
  const candidates = Array.isArray(input.candidates) ? input.candidates : [];
  const selectedCandidates = candidates
    .filter((candidate) => Boolean(candidate && candidate.selected))
    .map((candidate) => ({
      id: String(candidate.id || "candidate"),
      label: String(candidate.label || "Cleanup candidate"),
      risk: candidate.risk === "low" ? "low" : "review",
      gb: safeGigabytes(candidate.gb),
    }));
  const selectedTotal = roundGigabytes(
    selectedCandidates.reduce((total, candidate) => total + candidate.gb, 0),
  );
  const projectedFree = roundGigabytes(currentFree + selectedTotal);
  const remainingGap = roundGigabytes(Math.max(0, goalFree - projectedFree));

  return {
    currentFree: roundGigabytes(currentFree),
    goalFree: roundGigabytes(goalFree),
    selectedTotal,
    projectedFree,
    remainingGap,
    goalMet: projectedFree >= goalFree,
    selectedCandidates,
  };
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { calculatePlan };
}

if (typeof document !== "undefined") {
  const form = document.querySelector("#cleanup-planner");

  if (form) {
    const format = (value) => `${value.toLocaleString(undefined, { maximumFractionDigits: 2 })} GB`;
    const currentOutput = document.querySelector("#current-output");
    const reclaimOutput = document.querySelector("#reclaim-output");
    const projectedOutput = document.querySelector("#projected-output");
    const verdict = document.querySelector("#plan-verdict");
    const checklist = document.querySelector("#plan-checklist");

    const readPlan = () => calculatePlan({
      currentFree: form.elements.currentFree.value,
      goalFree: form.elements.goalFree.value,
      candidates: [...form.querySelectorAll("[data-candidate]")].map((row) => ({
        id: row.dataset.id,
        label: row.dataset.label,
        risk: row.dataset.risk,
        selected: row.querySelector("[data-select]").checked,
        gb: row.querySelector("[data-size]").value,
      })),
    });

    const render = () => {
      const plan = readPlan();
      currentOutput.textContent = format(plan.currentFree);
      reclaimOutput.textContent = format(plan.selectedTotal);
      projectedOutput.textContent = format(plan.projectedFree);

      if (plan.goalMet) {
        verdict.className = "verdict success";
        verdict.textContent = `Your selected actions meet the ${format(plan.goalFree)} goal, based on your estimates.`;
      } else {
        verdict.className = "verdict pending";
        verdict.textContent = `${format(plan.remainingGap)} remains between the estimate and your goal.`;
      }

      checklist.replaceChildren();
      if (plan.selectedCandidates.length === 0) {
        const item = document.createElement("li");
        item.textContent = "Select at least one area to build a review checklist.";
        checklist.append(item);
        return;
      }

      plan.selectedCandidates.forEach((candidate) => {
        const item = document.createElement("li");
        const badge = candidate.risk === "low" ? "Lower risk" : "Review first";
        item.textContent = `${badge} · ${candidate.label} · up to ${format(candidate.gb)}`;
        checklist.append(item);
      });
    };

    form.addEventListener("input", render);
    form.addEventListener("change", render);
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      render();
      document.querySelector("#plan-results").focus();
    });
    form.addEventListener("reset", () => window.setTimeout(render, 0));
    render();
  }
}
