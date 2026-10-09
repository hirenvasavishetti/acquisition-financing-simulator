from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class Shock:
    name: str = "Base"
    revenue: float = 0.0
    margin: float = 0.0
    inventory_days: float = 0.0
    benchmark: float = 0.0
    spread: float = 0.0
    synergy_factor: float = 1.0
    synergy_delay: int = 0

    def to_dict(self):
        return asdict(self)


def scenarios():
    rows = [Shock()]
    for severity, scale in (("Moderate", 1), ("Severe", 2)):
        rows.extend(
            [
                Shock(f"{severity} revenue", revenue=-0.05 * scale),
                Shock(f"{severity} margin", margin=-0.01 * scale),
                Shock(f"{severity} inventory", inventory_days=10 * scale),
                Shock(f"{severity} benchmark", benchmark=0.01 * scale),
                Shock(f"{severity} spread", spread=0.01 * scale),
            ]
        )
        factor, delay = (0.5, 1) if scale == 1 else (0.0, 0)
        rows.append(
            Shock(f"{severity} synergies", synergy_factor=factor, synergy_delay=delay)
        )
        rows.append(
            Shock(
                f"{severity} combined",
                -0.05 * scale,
                -0.01 * scale,
                10 * scale,
                0.01 * scale,
                0.01 * scale,
                factor,
                delay,
            )
        )
    return rows
