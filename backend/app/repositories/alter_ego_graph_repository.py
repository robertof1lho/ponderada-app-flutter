class AlterEgoGraphRepository:
    def __init__(self, driver):
        self._driver = driver

    async def save_graph(self, user_id: str, alter_ego_id: str, styles: list[str]) -> None:
        async with self._driver.session() as session:
            await session.run(
                "MERGE (u:User {id: $uid}) "
                "MERGE (a:AlterEgo {id: $aid}) "
                "MERGE (u)-[:CREATED]->(a)",
                uid=user_id, aid=alter_ego_id,
            )
            if styles:
                await session.run(
                    "UNWIND $styles AS styleName "
                    "MERGE (s:Style {name: styleName}) "
                    "MERGE (a:AlterEgo {id: $aid}) "
                    "MERGE (a)-[:HAS_STYLE]->(s)",
                    styles=styles, aid=alter_ego_id,
                )
