class NotFoundError(Exception):
    """Registro inexistente (HTTP 404)."""


class ConflictError(Exception):
    """Conflito de unicidade, capacidade ou vinculo (HTTP 409)."""
