# Agent notes: fly_vial

MIT for original code. FlyWire and MaleCNS remain under their published licenses (typically CC BY 4.0).

Connectomes are templates. Each sex loads one published map (FlyWire 139,255 female brain; MaleCNS 166,691 male CNS). The vial does not instantiate a live 139k or 167k LIF.

Default engine is the genome-to-circuit-scalar map. `--eval-connectome` is a cap-8 audit hook on accepted pairs. It uses a separate RNG so it does not step the vial. Seed-1 locked logs are hook-off. Seeds 2 and 3 may turn the hook on as an audit, not as a rewrite of `logs/assort_80.json` or `logs/random_80.json`.

Closed vial: no immigration.

Inbreeding depression is the measurement. If it does not appear, the load is too weak.

Deformed means trait extremes, collapsed circuit scores, sterility, or death.

No renderer, animation, narration, or product UI in this tree. Animation waits.

Do not restamp FlyWire 139,255 or MaleCNS 166,691 from a different paper.

Female template is brain-only. Do not silently add FANC. Female locomotion and copulation-motor scores are closed-form overlays, not a MaleCNS-symmetric VNC map.

Mating is the forced similarity rule. Do not replace it with an emergent free-choice model unless the operator turns `receptivity_filter` on, and then only as a filter after legality.

Recombination is free (independent loci). Do not add chromosomal blocks unless the operator asks.

Locked seed-1 logs: `logs/assort_80.json`, `logs/random_80.json`. Do not restamp F = 0.524 or F = 0.034. Seeds 2 and 3 write `logs/assort_80_s2.json` and friends. Never overwrite the seed-1 files. Public sentence is the description.txt block. Do not quote H as a second diversity finding: H = 1 - F when H_0 = 1. `mean_pairwise_phi` is pairwise kinship, not F; keep it in JSON, not as a headline. Courtship baseline is t = 1. Parallel courtship drop stays; a morphology-only assortative arm is a new experiment.

Heterozygosity is IBD on founder-allele IDs, not QTL value inequality.

Pin is `vialforge/`. Five laws: claim bans, engine order, closed vial, load required, template identity. Engine checkout `~/graphforge`. No catalog/`surfaces.json` unless the operator asks. Verify-before-done is the finish gate.

## Verify

`python3 ~/agent_laws_verify_before_done/vbd_gate.py check --app-root . --claim-done`

`vbd.runtime.json` runs pytest, an 8-generation N=40 fixture, and `vialforge/scripts/sanity_vialforge.py`. Do not use stock `/usr/bin/python3 -m pytest`.
