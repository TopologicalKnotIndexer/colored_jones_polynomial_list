# colored-jones-polynomial-list

Checkpointed color-2 and color-3 Jones polynomials for the organization's
catalog of 1,783 knots with at most 11 crossings.

## Repository contents

- `data/com_pd_code_list.txt` maps canonical knot names to PD codes.
- `data/sub_data/n2_*.txt` and `n3_*.txt` are per-knot checkpoints.
- `data/get_colored_jones_2_and_3.py` computes or resumes one checkpoint.
- `data/run_all.py` runs the complete bounded parallel workload and writes
  one JSON execution log per task under `data/log/`.

Checkpoint records use the format `[POLYNOMIAL|KNOT_NAME]`.

## Requirements

- Python 3.10 or newer.
- SageMath with `sage.all.Knot` available in the selected Python runtime.

No PyPI upload is required or performed by these scripts.

## Usage

Run one knot/color pair:

```bash
sage -python data/get_colored_jones_2_and_3.py 2 0
```

Run the full table with ten workers:

```bash
sage -python data/run_all.py 10
```

Each subprocess has a 60-second limit. The batch exits after every task has
completed or timed out; it does not remain in an infinite status loop.

## Algorithm

Prime-knot values are computed by SageMath's normalized
`Knot.colored_jones_polynomial()`. The normalization assigns value `1` to the
unknot. Composite-knot values are obtained by multiplying the values of their
prime summands, using multiplicativity under connected sum for this normalized
invariant. Textual PD codes are parsed with `ast.literal_eval`.

Existing non-empty checkpoint files are retained. Empty files are deleted and
recomputed, which makes interrupted runs resumable.

## Development

Parser, checkpoint, subprocess, and scheduler behavior can be tested without
SageMath:

```bash
python -m unittest discover -s tests -v
```

The computed dataset is released under the repository's MIT license.

## Citation

If you use this repository in academic work, please cite it as:

```bibtex
@software{topologicalknotindexer_colored_jones_polynomial_list,
  author = {{GGN\_2015}},
  title = {{colored\_jones\_polynomial\_list}},
  year = {2026},
  url = {https://github.com/TopologicalKnotIndexer/colored_jones_polynomial_list}
}
```
