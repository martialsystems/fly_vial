# Independent replica

Hash-check the locked logs, or rebuild them in a temp path and diff F, n, and courtship. Never overwrite `logs/assort_80.json` or `logs/random_80.json`.

## Machine used for the lock

- Python 3.12.14
- numpy 2.5.3 (`numpy.random.default_rng`)
- pytest 9.1.1
- macOS arm64

Install from the pin:

```
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock.txt
.venv/bin/python -m pip install -e ".[dev]"
```

## Commands

```
.venv/bin/python scripts/reproduce_lock.py
.venv/bin/python scripts/reproduce_lock.py --rerun
```

`--rerun` writes two temp JSON files for seed 1, 80 generations, N=1,000, then diffs t in {0, 1, 8, 20, 40, 80}. It does not write under `logs/`. Runtime on the lock machine is on the order of a few minutes for both arms.

## Expected sha256

| File | sha256 |
|------|--------|
| `logs/assort_80.json` | `92a328278e62c4c607749c9358cdc733e1f06424a4b7f13c97c352ce4f4f759b` |
| `logs/random_80.json` | `3c4606204cdf5516ddf7bbf371a59111473c944510fff4f87f8599b1171e8e61` |
| `logs/assort_80_s2.json` | `f4b699dd1197ecc2ff98510073b568092dd3963ecabd19277770065e45a4d752` |
| `logs/random_80_s2.json` | `ffcb77d6efb24c6cfbd4b2c94c9782c4dd751f24195720ad16a79327f629648f` |
| `logs/assort_80_s3.json` | `fd8df4bb9fcf906ae349175728658e7f6f9019efe7354bda2cc32038f4b1e7a0` |
| `logs/random_80_s3.json` | `5ca067a39917b150bb3056f632f10f89753bb2094c171323f35c9fbf4e5e05fd` |

Seed 1 RNG is `numpy.random.default_rng(1)`. The eval-connectome hook is off on the seed-1 lock.
