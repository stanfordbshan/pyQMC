(function () {
  const apiUrlEl = document.getElementById("api-url");
  const resultEl = document.getElementById("result");
  const runBtn = document.getElementById("run-btn");
  const form = document.getElementById("vmc-form");

  const params = new URLSearchParams(window.location.search);
  const apiBaseUrl = (params.get("api_base_url") || "http://127.0.0.1:8000").replace(/\/$/, "");
  apiUrlEl.textContent = apiBaseUrl;

  function numberValue(id) {
    return Number(document.getElementById(id).value);
  }

  function payloadFromForm() {
    const seedRaw = document.getElementById("seed").value.trim();
    return {
      n_steps: numberValue("n_steps"),
      burn_in: numberValue("burn_in"),
      step_size: numberValue("step_size"),
      alpha: numberValue("alpha"),
      initial_position: numberValue("initial_position"),
      seed: seedRaw === "" ? null : Number(seedRaw),
    };
  }

  function fmt(x, digits) {
    return Number(x).toFixed(digits);
  }

  function renderResult(data) {
    const exact = data.metadata && data.metadata.exact_ground_state_energy;
    const delta = exact !== undefined ? data.mean_energy - exact : null;

    const lines = [
      `Method: ${data.method}`,
      `System: ${data.system}`,
      `Samples: ${data.n_samples}`,
      `Mean energy: ${fmt(data.mean_energy, 8)}`,
      `Standard error: ${fmt(data.standard_error, 8)}`,
      `Acceptance ratio: ${fmt(data.acceptance_ratio, 4)}`,
    ];

    if (exact !== undefined) {
      lines.push(`Exact energy: ${fmt(exact, 8)}`);
    }

    if (delta !== null) {
      lines.push(`Difference (estimate - exact): ${fmt(delta, 8)}`);
    }

    resultEl.textContent = lines.join("\n");
  }

  async function runSimulation(evt) {
    evt.preventDefault();
    runBtn.disabled = true;
    runBtn.textContent = "Running...";
    resultEl.textContent = "Submitting simulation request...";

    try {
      const response = await fetch(`${apiBaseUrl}/simulate/vmc/harmonic-oscillator`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payloadFromForm()),
      });

      if (!response.ok) {
        const detail = await response.text();
        throw new Error(`API ${response.status}: ${detail}`);
      }

      const data = await response.json();
      renderResult(data);
    } catch (error) {
      resultEl.textContent = `Error:\n${String(error)}`;
    } finally {
      runBtn.disabled = false;
      runBtn.textContent = "Run VMC";
    }
  }

  form.addEventListener("submit", runSimulation);
})();
