# fly_vial

Does a closed vial of 1,000 diploid flies, paired by genome similarity, lose diversity and show inbreeding depression?

Yes. Under k=3 assortative pairing, seed 1, 80 discrete generations, inbreeding coefficient F = 0.524 and mean kinship φ = 0.0756. Autosomal QTL heterozygosity fell from 1.000 to 0.476. Mean egg-to-adult viability fell from 0.963 to 0.748. Adult fertility fell from 0.997 to 0.958. Pair courtship (first mating to generation 80) fell from 0.934 to 0.595. Population size stayed at 1,000; the vial did not go extinct. Locked log: `logs/assort_80.json`.

Female template: FlyWire 139,255 neurons, whole brain (Dorkenwald et al., *Nature* 2024). Male template: MaleCNS 166,691 neurons, brain plus ventral nerve cord (Berg et al., *Cell* 2026). Each agent loads the matching template identifier. The default engine maps a diploid genome onto circuit scalars (song, LC10 tracking, pC1/vpoDN receptivity, locomotion). A reduced-circuit audit hook exists for at most eight accepted-pair individuals; this run did not call it.

Mating is forced k-nearest-neighbor pairing on morphology plus courtship-circuit QTLs. Hidden recessive load (16 lethals, 48 sublethals, h = 0) is excluded from similarity. Offspring genomes are Mendelian plus per-locus Gaussian mutation. Density cap samples viable adults uniformly down to 1,000.

## Locked metrics

Copied from `logs/assort_80.json`.

| t | n | F | φ | H | egg viability | fertility | courtship | accepted pairs | clusters |
|--:|--:|--:|--:|--:|----------------:|----------:|----------:|---------------:|---------:|
| 0 | 1,000 | 0.000 | 0.000 | 1.000 | 0.963 | 0.997 | 0.000 | 0 | 4 |
| 1 | 1,000 | 0.000 | 0.001 | 1.000 | 0.921 | 0.991 | 0.934 | 372 | 32 |
| 8 | 1,000 | 0.131 | 0.006 | 0.869 | 0.817 | 0.966 | 0.820 | 385 | 98 |
| 20 | 1,000 | 0.217 | 0.014 | 0.783 | 0.787 | 0.959 | 0.744 | 374 | 75 |
| 40 | 1,000 | 0.399 | 0.035 | 0.601 | 0.777 | 0.952 | 0.680 | 382 | 61 |
| 80 | 1,000 | 0.524 | 0.076 | 0.476 | 0.748 | 0.958 | 0.595 | 386 | 48 |

Courtship at t = 0 is 0 because founders have not yet paired. Cluster count rose then fell. Some both-sex similarity clumps lost a sex (`n_extinct_clusters` is 1, 4, and 4 at t = 1, 8, and 20).

## How to run

```
.venv/bin/python -m pytest
.venv/bin/python -m fly_vial run --arm assortative --mode knn --k 3 --generations 80 --n 1000 --seed 1 --out logs/assort_80.json
```

Random mating is implemented (`--arm random`) and unit-tested. It is not the locked arm.

## Files

| Path | Role |
|------|------|
| `src/fly_vial/` | Genome, mating, inheritance, fitness, metrics, CLI |
| `data/templates/` | FlyWire / MaleCNS counts and circuit type names |
| `logs/assort_80.json` | Locked 80-generation assortative run |
| `vialforge/` | GraphForge pin: five refuse laws |
| `AGENTS.md` | Project rules and VBD |
| `THIRD_PARTY.md` | Connectome attribution |

[Fly research index](https://gist.github.com/martialsystems/12835f747d6360781f3cc7f91f243178)
