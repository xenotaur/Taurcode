from .prompt_model import Prompt


REQUIRED_FIELDS = ["id", "name", "description", "keyword"]


def validate_prompt(prompt: Prompt) -> None:
    for field_name in REQUIRED_FIELDS:
        if not getattr(prompt, field_name, ""):
            raise ValueError(f"Prompt missing required field: {field_name}")
    if not prompt.body.strip():
        raise ValueError(f"Prompt '{prompt.id or '<unknown>'}' has an empty body")


def validate_prompts(prompts: list[Prompt]) -> None:
    if not prompts:
        raise ValueError("No prompt markdown files found")
    for prompt in prompts:
        validate_prompt(prompt)
