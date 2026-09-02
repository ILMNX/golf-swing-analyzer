"""Overall score and coaching recommendations."""

from __future__ import annotations


def compute_overall_score(summary: dict[str, int]) -> int:
    weights = {
        "tempo": 0.2,
        "posture": 0.25,
        "rotation": 0.25,
        "balance": 0.2,
        "head_stability": 0.1,
    }
    total = sum(summary.get(k, 0) * w for k, w in weights.items())
    return int(round(max(0, min(100, total))))


def build_recommendation(summary: dict[str, int], club: str, shot_type: str) -> str:
    tips: list[str] = []

    if summary.get("head_stability", 100) < 70:
        tips.append("Kepala terlalu bergerak lateral — fokus menjaga head steady di atas bola.")
    if summary.get("posture", 100) < 70:
        tips.append("Bahu tidak level — perhatikan alignment bahu saat address.")
    if summary.get("rotation", 100) < 70:
        tips.append("Rotasi bahu/hip terbatas — tingkatkan turn pada backswing.")
    if summary.get("balance", 100) < 70:
        tips.append("Keseimbangan kaki tidak stabil — perlebar stance dan distribusikan berat merata.")
    if summary.get("tempo", 100) < 70:
        tips.append("Tempo swing tidak konsisten — latih ritme 3:1 backswing ke downswing.")

    if not tips:
        return (
            f"Swing {shot_type.replace('_', ' ')} dengan {club.replace('_', ' ')} terlihat solid. "
            "Pertahankan konsistensi dan fokus pada repeatability."
        )

    return " ".join(tips[:3])
