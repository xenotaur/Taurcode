from .prompt_model import Prompt

REQUIRED_FIELDS = ["id", "name", "description", "keyword", "body"]


def validate_prompt(prompt: Prompt) -> None:
    prompt_ref = prompt.source or (prompt.id or "<unknown>")
    for field_name in REQUIRED_FIELDS:
        value = getattr(prompt, field_name, "")
        if not isinstance(value, str) or not value:
            raise ValueError(f"Missing required field '{field_name}' in {prompt_ref}")
    if not prompt.body.strip():
        raise ValueError(f"Prompt body must not be blank in {prompt_ref}")

    if not isinstance(prompt.keyword, str):
        raise ValueError(f"Invalid keyword in {prompt_ref}: must be a string")
    if not prompt.keyword.startswith(":") or prompt.keyword == ":":
        raise ValueError(
            f"Invalid keyword '{prompt.keyword}' in {prompt_ref}: must start with ':' and not be empty"
        )


def validate_prompts(prompts: list[Prompt]) -> None:
    if not prompts:
        raise ValueError("No prompt markdown files found")

    id_sources: dict[str, str] = {}
    keyword_sources: dict[str, str] = {}

    for prompt in prompts:
        validate_prompt(prompt)

        prompt_ref = prompt.source or (prompt.id or "<unknown>")

        existing_id_source = id_sources.get(prompt.id)
        if existing_id_source:
            raise ValueError(
                f"Duplicate id '{prompt.id}' found in {existing_id_source} and {prompt_ref}"
            )
        id_sources[prompt.id] = prompt_ref

        existing_keyword_source = keyword_sources.get(prompt.keyword)
        if existing_keyword_source:
            raise ValueError(
                f"Duplicate keyword '{prompt.keyword}' found in {existing_keyword_source} and {prompt_ref}"
            )
        keyword_sources[prompt.keyword] = prompt_ref
