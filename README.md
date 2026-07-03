# DRIFT v1.0 — Dynamic Runtime Infrastructure for FARGO3D Tracking

## Architecture Specification & Execution Pipeline

**DRIFT** is a CLI orchestrator. It is engineered to automate large-scale parametric sweeps and magnetohydrodynamic (MHD) simulations in **FARGO3D** strictly under the principles of **immutability**, **asynchrony**, and **zero side effects**.

The execution workflow follows a sequential and asynchronous pipeline powered by 5 core modules:

[ FORGE ] ➔ [ LAUNCH ] ⇆ [ SENTINEL ] ⇆ [ UNIFY ] | [ VOID ]

| Module | CLI Command | Core Mission |
| :---: | :---: | :--- |
| **FORGE** | `./drift forge -b / -c` | Parametric forging and deployment tree construction. |
| **LAUNCH** | `./drift launch` | Non-invasive, asynchronous batch execution deployment. |
| **SENTINEL** | `./drift sentinel` | Real-time telemetry, CFL monitoring, and numerical crash mitigation. |
| **UNIFY** | `./drift unify` | Background tensor consolidation and HDF5 data compression. |
| **VOID** | `./drift void -c / -o / -a` | Surgical sanitization and environment resetting. |

---

## Step-by-Step Architecture Breakdown

### PHASE 0: Forging & Infrastructure (`FORGE`)

The **FORGE** engine translates a conceptual parameter design space into a physical directory tree ready for the underlying C numerical solver.

1. **Scan & Blueprint (`forge -b`):**
   * Reads user configurations (`variables.py` or a `blueprint.json` file) defining static variables and hyperparameter ranges to explore (e.g., $\text{ASPECTRATIO}$, $\text{SIGMA0}$, plasma $\beta$).
   * Generates a comprehensive parameter matrix using Cartesian product algorithms (`itertools.product`).

2. **Deployment Tree Construction (`forge -c`):**
   * Edifies an isolated runtime directory for each individual simulation within the output tree: `outputs/run_001/`, `outputs/run_002/`, ..., `outputs/run_N/` (applying automatic zero-padding for alphabetical sorting).
   * Generates the specific setup parameter file `outputs/run_XXX/setup.par` by cloning the base setup and injecting the customized blueprint parameters.
   * **Direct Redirection Injection:** Explicitly overrides the target output path to eliminate redundant disk I/O operations:
     $$\text{OutputDirectory} = \text{/absolute/path/to/outputs/run\_XXX/}$$

---

### PHASE 1: Asynchronous & Shielded Execution Loop (`LAUNCH` & `SENTINEL`)

The **LAUNCH** engine manages the execution queue, maximizing CPU/GPU utilization without altering or contaminating the base FARGO3D source repository.

3. **Zero-Touch Execution:**
   * **LAUNCH** never edits, moves, or overwrites the original `.par` file located inside `setups/[setup_name]/`.
   * Invokes the native compiled binary by passing the forged parameter file directly as a terminal argument:
     ```bash
     ./fargo3d outputs/run_XXX/setup.par
     ```
   * *(HPC Support):* If parallel computing is required, the command dynamically scales via MPI to `mpirun -np [cores] ./fargo3d outputs/run_XXX/setup.par`.

4. **Native Output Redirection:**
   * During execution, FARGO3D reads the injected `OutputDirectory` and outputs raw numerical data binaries (`gasdens*.dat`, `gasvrad*.dat`) directly into `outputs/run_XXX/`.
   * **Immutability Guarantee:** The FARGO3D setup root directory remains 100% pristine throughout the entire computational cycle.

5. **Real-Time Continuous Monitoring (`SENTINEL`):**
   * While FARGO3D computes, the **SENTINEL** engine performs non-intrusive background inspection of the execution log file `outputs/run_XXX/fargo3d.log`.
   * Monitors timestep evolution ($\Delta t$), Courant–Friedrichs–Lewy (CFL) stability conditions, and physical conservation laws.
   * **Active Mitigation:** If a numerical divergence (*NaN*, CFL violation, or segmentation fault) is detected, it sends a surgical kill signal to the current subprocess and flags the directory with a `.FAILED` state, shielding the rest of the batch queue.

---

### PHASE 2: Asynchronous Processing (`UNIFY`)

The **UNIFY** engine removes storage I/O bottlenecks by decoupling heavy data compression from core numerical computation.

6. **Asynchronous HDF5 Packaging:**
   * Immediately after **LAUNCH** captures a successful exit code (`exit code 0`) from `run_XXX`, it immediately launches the next simulation (`run_XXX+1`) on the CPU/GPU with zero idle time.
   * Simultaneously, a background **UNIFY** subprocess forks over the `outputs/run_XXX/` directory.
   * Reads the raw binary output matrices (`.dat`), structures them across the spatial-temporal mesh $(r, \theta, z, t)$, and packs them into a single, highly structured tensor container `data.h5`.

---

### PHASE 3: Preservation & Sanitization (`VOID`)

The **VOID** engine handles storage management in HPC environments where high-speed scratch disk allocations are restricted or costly.

7. **Selective Environment Purging:**
   * Once **UNIFY** verifies the integrity checksum of the compiled `data.h5` container, **VOID** can safely purge hundreds of gigabytes of redundant raw `.dat` files, retaining only the consolidated tensors and telemetry records (`setup.par`, `fargo3d.log`, `data.h5`).
   * Provides granular command-line flags to execute clean environment resets:
     * `./drift void --config` (`-c`): Purges forged configuration directories in `configs/`.
     * `./drift void --outputs` (`-o`): Purges computational results and logs in `outputs/`.
     * `./drift void --all` (`-a`): Executes a complete factory reset of the DRIFT workspace.

---

## Supercomputing Performance Advantages

* **Zero Redundant I/O Overhead:** Directing `OutputDirectory` straight to the final destination eliminates unnecessary copying of massive datasets across storage partitions.
* **100% Compute Continuity:** CPUs and GPUs experience zero idle wait times while storage nodes compress raw outputs into HDF5 formats.
* **Pristine Isolation:** Original FARGO3D setups and source files remain strictly untouched, eliminating the risk of workspace corruption due to execution crashes or power interruptions.