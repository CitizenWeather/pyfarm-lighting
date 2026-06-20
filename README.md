# pyfarm-lighting

Photoperiod and DLI management for pyfarm.

## Purpose

Light control for photoperiod-sensitive crops.

## Phase 1 Scope

- **DLI Calculations** — Convert target DLI (mol/m²/day) to runtime hours based on fixture specs
- **Photoperiod Control** — Schedule lights on/off with configurable onset/offset times
- **Safety Interlocks** — Respect thermal constraints (light → heat)
- **Dimming Curves** — Support flat, linear, or sinusoidal intensity curves

## Integration

- Called by pyfarm-control to compute setpoints
- Loads cultivar defaults from pyfarm-crops
- GrowSpec can override via `<lighting>` block

## Development

```bash
pip install -e ".[dev]"
pytest tests/
```
