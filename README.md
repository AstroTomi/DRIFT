# DRIFT v1.0 — Dynamic Runtime Infrastructure for FARGO3D Tracking

**DRIFT** is a CLI orchestration software designed to automate parametric sweeps for HD/MHD simulations in **FARGO3D**. It is built strictly under the principles of *immutability* and *zero side effects*; meaning that the original **FARGO3D** workspace remains completely unaltered before, during, and after the execution of this program.

[//]: # (TODO: [x] Modified introduction and fisrt phase.)

## Architecture Specification & Execution Pipeline

The execution workflow follows a sequential and asynchronous pipeline powered by 5 modules:

| Module | CLI Command | Core Mission |
| :---: | :---: | :--- | 
| **FORGE** | `./drift forge -b, -d` | Parameter definition and directory tree deployment. |
| **LAUNCH** | `./drift launch` | Batch process management and simulation execution. |
| **SENTINEL** | `./drift sentinel` | Real-time monitoring and crash mitigation. |
| **UNIFY** | `./drift unify` | HDF5 data compression and background tensor consolidation. |
| **VOID** | `./drift void -a, -c, -l, -o` | Modular cleanup and environment resetting. |

This will be a diagram.

[ FORGE ] ➔ [ LAUNCH ] ⇆ [ SENTINEL ] ⇆ [ UNIFY ] | [ VOID ]

### PHASE 0: Forging & Infrastructure (`FORGE`)

The **FORGE** engine translates a parameter design space into a directory tree ready for the underlying C numerical solver.

1. **Scan & Blueprint Creation:**

   * Executing `./drift forge -b` scans the `setups/` directory located inside the **FARGO3D** root folder and presents an interactive setup selection menu. This generates a `blueprint.json` file containing all the original parameters extracted from the `.par` file of the selected setup.
   
   * The user modifies this blueprint file to define static variables and parameter ranges to explore. For example: `"NZ": "30"` for static values and `"NX": [128, 256]` for parameter sweeps.
   
     * Note that standard JSON typing applies: integers can be written with quotation marks, but arrays **MUST** be written without quotation marks. For example, `"NZ": 30` is the same to `"NZ": "30"` and a list needs to be written like `"PlanetConfig": ["planets/MobileJupiter.cfg", "planets/neptune.cfg"]`, whereas strings and boolean-like definitions must remain quoted (e.g., `"Setup": "p3diso"` or `"Disk": "YES"`).
   
   * Next, running `./drift forge -d` prompts the user to select the target blueprint. **FORGE** then processes the non-static parameters using a Cartesian product algorithm (`itertools.product`), generating a parameter matrix that maps every possible configuration for the upcoming simulation batch.

2. **Deployment Tree Construction:**

   * The final step, **isolated via a prompt ater the last command** as a safety measure against accidental overwrites, creates an independent execution directory for each simulation inside the `outputs/` tree: `outputs/run_001/`, `outputs/run_002/`, ..., `outputs/run_N/`. Automatic zero-padding is applied to ensure strict alphabetical sorting.

   * Additionally, it generates a dedicated `outputs/run_XXX/setup.par` file for each run by cloning the base setup and injecting the specific parameter combination assigned by the matrix.

   * Finally, it explicitly overrides the target output directory to eliminate redundant disk I/O operations, modifying the `"OutputDir"` parameter from `"@outputs/[setup name]/"` directly to `[DRIFT absolute path]/outputs/run_XXX/`.


# AFTER THIS, NOTHING ELSE MATTERS...


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

### PHASE 2: Asynchronous Processing (`UNIFY`)

The **UNIFY** engine removes storage I/O bottlenecks by decoupling heavy data compression from core numerical computation.

6. **Asynchronous HDF5 Packaging:**
   * Immediately after **LAUNCH** captures a successful exit code (`exit code 0`) from `run_XXX`, it immediately launches the next simulation (`run_XXX+1`) on the CPU/GPU with zero idle time.
   * Simultaneously, a background **UNIFY** subprocess forks over the `outputs/run_XXX/` directory.
   * Reads the raw binary output matrices (`.dat`), structures them across the spatial-temporal mesh $(r, \theta, z, t)$, and packs them into a single, highly structured tensor container `data.h5`.

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