"""Pile undo/redo pour la session CLI."""


def create_undo_stack() -> dict:
    """Crée une pile undo/redo vide."""
    return {"undo": [], "redo": [], "max_size": 50}


def push_state(stack: dict, state: dict) -> dict:
    """Empile un état (immutable). Vide la pile redo."""
    undo = [*stack["undo"], state]
    if len(undo) > stack["max_size"]:
        undo = undo[-stack["max_size"]:]
    return {**stack, "undo": undo, "redo": []}


def undo(stack: dict) -> tuple[dict, dict | None]:
    """Dépile un état. Retourne (nouveau_stack, état_restauré)."""
    if not stack["undo"]:
        return stack, None
    restored = stack["undo"][-1]
    return {
        **stack,
        "undo": stack["undo"][:-1],
        "redo": [*stack["redo"], restored],
    }, restored


def redo(stack: dict) -> tuple[dict, dict | None]:
    """Rétablit un état. Retourne (nouveau_stack, état_rétabli)."""
    if not stack["redo"]:
        return stack, None
    restored = stack["redo"][-1]
    return {
        **stack,
        "redo": stack["redo"][:-1],
        "undo": [*stack["undo"], restored],
    }, restored


def can_undo(stack: dict) -> bool:
    return len(stack["undo"]) > 0


def can_redo(stack: dict) -> bool:
    return len(stack["redo"]) > 0
