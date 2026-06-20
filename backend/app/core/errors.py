class AlterMeError(Exception):
    pass


class VisionError(AlterMeError):
    pass


class GenerationError(AlterMeError):
    pass


class Neo4jError(AlterMeError):
    pass


class NotFoundError(AlterMeError):
    pass
