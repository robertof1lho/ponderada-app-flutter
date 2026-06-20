UNIVERSE_DESCRIPTORS = {
    "anime": "anime art style, vibrant colors, large expressive eyes, Studio Ghibli quality",
    "medieval": "medieval fantasy portrait, oil painting, armor, castle background",
    "sci-fi": "futuristic cyberpunk portrait, neon lights, chrome, holographic elements",
    "político br": "brazilian political caricature, editorial cartoon style, exaggerated features",
}

QUALITY_SUFFIX = ", highly detailed, 8k, professional illustration"

class PromptService:
    def build_prompt(self, traits: dict, universe: str) -> str:
        base = UNIVERSE_DESCRIPTORS.get(universe.lower(), f"{universe} art style")
        parts = [f"portrait of a person in {base}"]

        if traits.get("expression"):
            parts.append(f"with a {traits['expression']} expression")

        if traits.get("hair_color"):
            parts.append(f"{traits['hair_color']} hair")

        return ", ".join(parts) + QUALITY_SUFFIX

    def extract_style_tags(self, traits: dict, universe: str) -> list[str]:
        tags = [universe.lower()]
        if traits.get("expression"):
            tags.append(traits["expression"])
        if traits.get("hair_color"):
            tags.append(traits["hair_color"] + "_hair")
        return tags
