(function () {
  const computeModeEl = document.getElementById("compute-mode");
  const transportModeEl = document.getElementById("transport-mode");
  const apiUrlEl = document.getElementById("api-url");
  const resultEl = document.getElementById("result");
  const runBtn = document.getElementById("run-btn");
  const form = document.getElementById("vmc-form");

  const params = new URLSearchParams(window.location.search);
  const requestedComputeMode = (params.get("compute_mode") || "auto").toLowerCase();
  const computeMode = ["auto", "direct", "api"].includes(requestedComputeMode)
    ? requestedComputeMode
    : "auto";

  const rawApiBaseUrl = (params.get("api_base_url") || "").trim();
  const apiBaseUrl = rawApiBaseUrl ? rawApiBaseUrl.replace(/\/$/, "") : null;

  computeModeEl.textContent = computeMode;
  apiUrlEl.textContent = apiBaseUrl || "(none)";

  function setTransportMode(value) {
    transportModeEl.textContent = value;
  }

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
    const alpha = data.parameters && typeof data.parameters.alpha === "number"
      ? data.parameters.alpha
      : null;

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

    if (
      alpha !== null &&
      Math.abs(alpha - 1.0) < 1e-12 &&
      Math.abs(data.standard_error) < 1e-12 &&
      delta !== null &&
      Math.abs(delta) < 1e-12
    ) {
      lines.push(
        "Note: alpha=1.0 is exact for this system, so local energy is constant E=0.5."
      );
      lines.push(
        "Try alpha=0.95 or 0.90 to observe sampling fluctuations with small N."
      );
    }

    resultEl.textContent = lines.join("\n");
  }

  function hasLocalBridge() {
    return Boolean(
      window.pywebview &&
        window.pywebview.api &&
        typeof window.pywebview.api.run_vmc_harmonic_oscillator === "function"
    );
  }

  function waitForLocalBridge(timeoutMs = 2000) {
    if (hasLocalBridge()) {
      return Promise.resolve(window.pywebview.api);
    }

    return new Promise((resolve, reject) => {
      const onReady = () => {
        if (hasLocalBridge()) {
          cleanup();
          resolve(window.pywebview.api);
        }
      };

      const timer = window.setTimeout(() => {
        cleanup();
        reject(new Error("Local compute bridge is not available"));
      }, timeoutMs);

      function cleanup() {
        window.clearTimeout(timer);
        window.removeEventListener("pywebviewready", onReady);
      }

      window.addEventListener("pywebviewready", onReady);
    });
  }

  async function runViaLocalBridge(payload) {
    const bridge = await waitForLocalBridge();
    setTransportMode("direct-local");
    return bridge.run_vmc_harmonic_oscillator(payload);
  }

  async function runViaApi(payload, transportLabel = "http-api") {
    if (!apiBaseUrl) {
      throw new Error("API URL is not configured for this GUI session");
    }

    setTransportMode(transportLabel);
    const response = await fetch(`${apiBaseUrl}/simulate/vmc/harmonic-oscillator`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const detail = await response.text();
      throw new Error(`API ${response.status}: ${detail}`);
    }

    return response.json();
  }

  async function runWithConfiguredMode(payload) {
    if (computeMode === "direct") {
      return runViaLocalBridge(payload);
    }

    if (computeMode === "api") {
      return runViaApi(payload, "http-api");
    }

    try {
      return await runViaLocalBridge(payload);
    } catch (directError) {
      if (!apiBaseUrl) {
        throw directError;
      }
      return runViaApi(payload, "http-api (fallback)");
    }
  }

  async function runSimulation(evt) {
    evt.preventDefault();
    runBtn.disabled = true;
    runBtn.textContent = "Running...";
    resultEl.textContent = "Submitting simulation request...";
    setTransportMode("running...");

    try {
      const data = await runWithConfiguredMode(payloadFromForm());
      renderResult(data);
    } catch (error) {
      setTransportMode("error");
      resultEl.textContent = `Error:\n${String(error)}`;
    } finally {
      runBtn.disabled = false;
      runBtn.textContent = "Run VMC";
    }
  }

  form.addEventListener("submit", runSimulation);
})();
