from app.services.vision_service import VisionService
from app.services.prompt_service import PromptService
from app.services.generation_service import GenerationService


class GenerateAlterEgoUseCase:
    def __init__(
        self,
        alter_ego_repository,
        vision_service: VisionService,
        prompt_service: PromptService,
        generation_service: GenerationService,
    ):
        self._repo = alter_ego_repository
        self._vision = vision_service
        self._prompt = prompt_service
        self._generation = generation_service

    async def execute(self, user_id: str, selfie_url: str, universe: str) -> dict:
        traits = await self._vision.extract_traits(selfie_url)
        prompt = self._prompt.build_prompt(traits, universe)
        negative_prompt = self._prompt.build_negative_prompt()
        image_url = await self._generation.generate(prompt, negative_prompt=negative_prompt, selfie_url=selfie_url)
        style_tags = self._prompt.extract_style_tags(traits, universe)
        saved = await self._repo.save(
            user_id=user_id,
            image_url=image_url,
            selfie_url=selfie_url,
            universe=universe,
            traits=traits,
            style_tags=style_tags,
        )
        return {"id": saved["id"], "image_url": image_url, "style_tags": style_tags}
