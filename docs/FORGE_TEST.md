# DRIFT FORGE — Stress Testing Specification

This document outlines the diagnostic suite used to validate the structural integrity, edge-case handling, and parser compatibility of the `FORGE` module prior to running production workloads in **FARGO3D**.

---

## 1. Test Scenarios Matrix

| Test ID | Scenario | Validation Objective | Potential Failure Mode |
| :--- | :--- | :--- | :--- |
| **TEST-01** | **Dynamic Parameter Injection** | Verify that parameters present in the blueprint matrix but absent in the base `.par` file are cleanly appended at the end of the generated file. | Parser ignores new parameters or appends them with incorrect formatting. |
| **TEST-02** | **Inline Comments & Empty Rows** | Process base template files containing trailing inline comments (e.g., `NX 128 # Grid resolution`) and irregular empty rows. | String splitting errors (`split()[0]`) corrupt parameter keys or delete inline comments. |
| **TEST-03** | **Zero-Padding Scalability** | Evaluate deployment behavior across variable batch sizes (e.g., single-digit `len = 5` vs. large-scale `len = 1050`). | Directory naming misalignment (e.g., generating `run_1` instead of `run_001`). |
| **TEST-04** | **Path Integrity & Trailing Slash** | Audit the explicit override of the `OutputDir` parameter in the generated `.par` files. | Missing trailing slash (`/`) causes FARGO3D to dump output files in the parent directory. |

---

## 2. Mock Setup Preparation (`test_suite.par`)

Create an isolated test setup inside your root directory at `setups/test_suite/test_suite.par`. This file deliberately includes mixed formatting, comments, and spacing to challenge the parser:

```text
### DRIFT FORGE TEST SUITE TEMPLATE ###

NX               	128         # Radial grid resolution
NY               	256
# Standard comment line

Aspectratio      	0.05
Sigma0           	1e-4

OutputDir        	@outputs/test_suite/