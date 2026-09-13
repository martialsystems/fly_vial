# fly_vial

Does a closed vial of 1,000 diploid flies, paired by genome similarity, raise IBD F faster than random mating at the same N, seed, and load?

Assortative k = 3, seed 1, 80 generations: F = 0.524. Random mating, same N / seed / load: F = 0.034. Wright's random-mating scale at census N = 1,000 is about 80 / 2,000 = 0.04. Census stayed at 1,000 on both arms. Locked logs: `logs/assort_80.json`, `logs/random_80.json`.

Independent fitness numbers, egg-to-adult viability, t = 0 to t = 80:

- Assortative: 0.963 to 0.748
- Random: 0.963 to 0.791

Fertility, t = 0 to t = 80: 0.997 to 0.958 assortative, 0.997 to 0.959 random.

Courtship uses the first generation that pairs (t = 1), then t = 80: 0.934 to 0.595 assortative, 0.930 to 0.599 random. Those two courtship series move together. The courtship drop is not the assortative signature. The eval hook was off (`n_eval_hook` = 0). Scores are closed-form circuit scalars.

Assortative similarity clumps rose then fell (4, 32, 98, 48). Some both-sex clumps lost a sex (`n_extinct_clusters` 1, 4, 4 at t = 1, 8, 20). Random clumps ended at 2.

F in the log is `1 - H_t / H_0` from within-individual founder-allele IBD. H_0 = 1, so H = 1 - F is the same number written twice. The log keeps both conventions. Heterozygosity is IBD on founder IDs, not a floating-point compare of QTL values.

`mean_pairwise_phi` is mean kinship over unordered adult pairs from autosomal QTL founder-allele IBD. It is not F (assortative t = 80: F = 0.524, phi = 0.076). It stays in the JSON. It is not a headline.

Recombination is free: each locus segregates independently. QTLs do not hitchhike. Chromosomal blocks are unbuilt.

Female template: FlyWire 139,255 neurons, whole brain, no VNC (Dorkenwald et al., *Nature* 2024). Male template: MaleCNS 166,691 neurons, brain plus ventral nerve cord (Berg et al., *Cell* 2026). Female locomotion and copulation-motor scores are closed-form overlays on that brain map, not a MaleCNS-symmetric VNC reconstruction. vpoDN and song CPG names in the G2P map are circuit labels for those scalars.

Mating is forced k-nearest-neighbor pairing on morphology plus courtship-circuit QTLs. Hidden recessive load (16 lethals, 48 sublethals, h = 0) is excluded from similarity. Offspring genomes are Mendelian plus per-locus Gaussian mutation. Density cap samples viable adults uniformly down to 1,000.

## Locked metrics

Copied from the JSON. Courtship at t = 0 is omitted: founders have not paired. H is omitted: it is 1 - F.

Assortative, `logs/assort_80.json`:

| t | n | F | egg viability | fertility | courtship | accepted pairs | clusters |
|--:|--:|--:|----------------:|----------:|----------:|---------------:|---------:|
| 0 | 1,000 | 0.000 | 0.963 | 0.997 |  | 0 | 4 |
| 1 | 1,000 | 0.000 | 0.921 | 0.991 | 0.934 | 372 | 32 |
| 8 | 1,000 | 0.131 | 0.817 | 0.966 | 0.820 | 385 | 98 |
| 20 | 1,000 | 0.217 | 0.787 | 0.959 | 0.744 | 374 | 75 |
| 40 | 1,000 | 0.399 | 0.777 | 0.952 | 0.680 | 382 | 61 |
| 80 | 1,000 | 0.524 | 0.748 | 0.958 | 0.595 | 386 | 48 |

Random, `logs/random_80.json`:

| t | n | F | egg viability | fertility | courtship | accepted pairs | clusters |
|--:|--:|--:|----------------:|----------:|----------:|---------------:|---------:|
| 0 | 1,000 | 0.000 | 0.963 | 0.997 |  | 0 | 4 |
| 1 | 1,000 | 0.000 | 0.918 | 0.990 | 0.930 | 493 | 10 |
| 8 | 1,000 | 0.005 | 0.871 | 0.979 | 0.861 | 493 | 77 |
| 20 | 1,000 | 0.008 | 0.832 | 0.969 | 0.772 | 488 | 25 |
| 40 | 1,000 | 0.021 | 0.784 | 0.959 | 0.690 | 481 | 7 |
| 80 | 1,000 | 0.034 | 0.791 | 0.959 | 0.599 | 485 | 2 |

## How to run

```
.venv/bin/python -m pytest
.venv/bin/python -m fly_vial run --arm assortative --mode knn --k 3 --generations 80 --n 1000 --seed 1 --out logs/assort_80.json
.venv/bin/python -m fly_vial run --arm random --mode random --generations 80 --n 1000 --seed 1 --out logs/random_80.json
```

## Files

| Path | Role |
|------|------|
| `src/fly_vial/` | Genome, mating, inheritance, fitness, metrics, CLI |
| `data/templates/` | FlyWire / MaleCNS counts and circuit type names |
| `logs/assort_80.json` | Locked 80-generation k = 3 assortative run |
| `logs/random_80.json` | Locked 80-generation random-mating contrast |
| `vialforge/` | GraphForge pin: five refuse laws |
| `AGENTS.md` | Project rules and VBD |
| `THIRD_PARTY.md` | Connectome attribution |

[Fly research index](https://gist.github.com/martialsystems/12835f747d6360781f3cc7f91f243178)
