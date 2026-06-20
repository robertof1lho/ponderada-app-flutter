from app.domain.repositories.alter_ego_repository import AlterEgoRepository
from app.services.vision_service import VisionService
from app.services.prompt_service import PromptService
from app.services.generation_service import GenerationService


class GenerateAlterEgoUseCase:
    def __init__(
        self,
        alter_ego_pg_repository,   # AlterEgoPgRepository
        alter_ego_graph_repository,  # AlterEgoGraphRepository
        vision_service: VisionService,
        prompt_service: PromptService,
        generation_service: GenerationService,
    ):
        self._pg_repo = alter_ego_pg_repository
        self._graph_repo = alter_ego_graph_repository
        self._vision = vision_service
        self._prompt = prompt_service
        self._generation = generation_service

    async def execute(self, user_id: str, selfie_url: str, universe: str) -> dict:
        traits = await self._vision.extract_traits(selfie_url)
        prompt = self._prompt.build_prompt(traits, universe)
        image_url = await self._generation.generate(prompt)
        style_tags = self._prompt.extract_style_tags(traits, universe)
        saved = await self._pg_repo.save(
            user_id=user_id,
            image_url=image_url,
            selfie_url=selfie_url,
            universe=universe,
            traits=traits,
        )
        await self._graph_repo.save_graph(
            user_id=user_id,
            alter_ego_id=saved["id"],
            styles=style_tags,
        )
        return {"id": saved["id"], "image_url": image_url, "style_tags": style_tags}
