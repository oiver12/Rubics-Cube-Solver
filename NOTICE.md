# Attribution and license scope

The GNU General Public License version 2 in `LICENSE` (GPL-2.0-only) is the license selected for this project's original software contributions, including its original firmware, hardware integration changes, and new rendering script. Existing third-party material is excluded from any grant the project contributors cannot make.

## Python foundation

`main.py` credits Kenneth Hung. A matching upstream project is:

https://github.com/kennethhung863/Rubiks-Cube-Solver

That repository contains the Pygame GUI primitives and several solver variants. The source header and matching GUI code establish the relationship, but the precise provenance of every line in this checkout has not been reconstructed. The existing author attribution has been preserved. No explicit upstream license file was present when reviewed on 2026-10-19; the project's GPL choice does not establish permission to relicense Kenneth Hung's original code.

The `kociemba` package is a separately installed dependency, not vendored in this repository. It implements Herbert Kociemba's two-phase algorithm and declares GPLv2:

https://github.com/muodov/kociemba

Other installed dependencies retain their own licenses.

## Mechanical assets and renders

`STL_files/` contains a third-party mechanical design found by the builder's brother. These files are retained at the repository owner's request. Their original source and redistribution terms have not been verified. The embedded 3MF designer, copyright, and license fields are blank.

The part names match the following likely source, credited to `aaedmusa` by its published metadata:

https://www.instructables.com/Rubiks-Cube-Solver-2/

This match is a source lead, not confirmation of an identical licensed file set. GPL-2.0-only does not apply to the mechanical models or grant additional rights in them. The CAD renders in `docs/images/` are derived from these models and do not establish additional rights in the underlying design. Generic motor bodies and assembly placement in the concept render are illustrative. No tutorial photographs are redistributed.
