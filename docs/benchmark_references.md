# Benchmark References

This document records the reference values used in the current benchmark suite.

## Units and conventions
All harmonic-oscillator benchmarks use reduced units:
- `hbar = 1`
- `m = 1`
- `omega = 1`

## Reference 1: Exact ground-state energy
For the 1D harmonic oscillator,
- `E_n = n + 1/2`
- ground state (`n = 0`) is `E0 = 0.5`

This is the reference used for benchmark case `ho_exact_alpha_1.0`.

## Reference 2: Variational energy for Gaussian trial wavefunction
For trial wavefunction
- `psi_T(x; alpha) = exp(-alpha x^2 / 2)` with `alpha > 0`

the analytic variational energy is
- `E(alpha) = 1/4 * (alpha + 1/alpha)`

This is used for benchmark cases:
- `ho_variational_alpha_0.8`
- `ho_variational_alpha_1.2`

## Literature context
These formulas are standard quantum-mechanics results and are commonly used in introductory VMC teaching examples.

Suggested background references:
1. D. J. Griffiths and D. F. Schroeter, *Introduction to Quantum Mechanics* (Cambridge University Press), harmonic oscillator chapter.
2. W. M. C. Foulkes, L. Mitas, R. J. Needs, and G. Rajagopal, "Quantum Monte Carlo simulations of solids," *Rev. Mod. Phys.* 73, 33 (2001), doi:10.1103/RevModPhys.73.33.
