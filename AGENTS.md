# Agent notes: fly_vial

MIT for original code. FlyWire and MaleCNS remain under their published licenses (typically CC BY 4.0).

Connectomes are templates. Each sex loads one published map (FlyWire 139,255 female brain; MaleCNS 166,691 male CNS). The vial does not instantiate a live 139k or 167k LIF.

Default engine is the genome-to-circuit-scalar map. `--eval-connectome` is a cap-8 audit hook on accepted pairs.

Closed vial: no immigration.

Inbreeding depression is the measurement. If it does not appear, the load is too weak.

Deformed means trait extremes, collapsed circuit scores, sterility, or death.

No renderer, animation, narration, or product UI in this tree.

Do not restamp FlyWire 139,255 or MaleCNS 166,691 from a different paper.

Female template is brain-only; do not silently add FANC.

Mating is the forced similarity rule. Do not replace it with an emergent free-choice model unless the operator turns `receptivity_filter` on, and then only as a filter after legality.

Pin is `vialforge/`. Five laws: claim bans, engine order, closed vial, load required, template identity. Engine checkout `~/graphforge`. No catalog/`surfaces.json` unless the operator asks. Verify-before-done is the finish gate.

## Verify

`python3 ~/agent_laws_verify_before_done/vbd_gate.py check --app-root . --claim-done`

`vbd.runtime.json` runs pytest, an 8-generation N=40 fixture, and `vialforge/scripts/sanity_vialforge.py`. Do not use stock `/usr/bin/python3 -m pytest`.
