_IDENTITY_LOCK = (
    "IMPORTANT: preserve this exact person's physical characteristics — "
    "same face structure, jawline, nose shape, eye shape and color, skin tone, "
    "hair color and texture, age appearance. Only the art style and clothing change. "
    "The output must be unmistakably the same individual."
)

UNIVERSE_DESCRIPTORS = {
    "anime": (
        "Redraw this exact person as a polished anime character portrait. "
        "Translate their real face into anime art style: cel-shaded skin, clean line art, "
        "expressive anime eyes reflecting their actual eye color, vibrant colors, Studio Ghibli quality rendering. "
        "Change only the art style — every facial feature stays true to the original photo"
    ),
    "medieval": (
        "Redraw this exact person as a medieval fantasy portrait. "
        "Dress them as a noble knight or warrior with detailed plate armor and fur-lined cloak. "
        "Dramatic torch lighting, stone castle background, oil painting style. "
        "Keep all their real facial features — only the clothing, setting and art style change"
    ),
    "sci-fi": (
        "Redraw this exact person as a cinematic cyberpunk character. "
        "Add subtle cybernetic implants near one eye and futuristic clothing. "
        "Neon city lights reflecting on their face, holographic HUD elements in background, Blade Runner aesthetic. "
        "Keep all their real facial features — only the clothing, setting and art style change"
    ),
    "político br": (
        "Redraw this exact person as a Brazilian political leader in an official portrait. "
        "Dress them in a formal suit with a Brazilian flag pin, Brazilian congress building in background, "
        "dramatic editorial photography lighting, confident expression. "
        "Keep all their real facial features — only the clothing and setting change"
    ),
}

QUALITY_PREFIX = ""
QUALITY_SUFFIX = f". {_IDENTITY_LOCK} High quality, detailed."
NEGATIVE_PROMPT = (
    "blurry, low quality, deformed, bad anatomy, cropped, worst quality, watermark, text, "
    "different person, changed face, different nose, different eyes, different skin tone, "
    "different hair color, younger, older, different gender"
)

class PromptService:
    def build_prompt(self, traits: dict, universe: str) -> str:
        base = UNIVERSE_DESCRIPTORS.get(universe.lower(),
            f"Transform this person into a {universe} style character, exaggerated and satirical")

        extra = []
        if traits.get("expression"):
            extra.append(f"with a {traits['expression']} expression")
        if traits.get("hair_color"):
            extra.append(f"keeping hints of their {traits['hair_color']} hair color")

        suffix = (", " + ", ".join(extra)) if extra else ""
        return base + suffix + QUALITY_SUFFIX

    def build_negative_prompt(self) -> str:
        return NEGATIVE_PROMPT

    def extract_style_tags(self, traits: dict, universe: str) -> list[str]:
        tags = [universe.lower()]
        if traits.get("expression"):
            tags.append(traits["expression"])
        if traits.get("hair_color"):
            tags.append(traits["hair_color"] + "_hair")
        return tags
