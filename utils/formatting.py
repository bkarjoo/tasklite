def wrap_code_in_fence(code: str, language: str = "c") -> str:
    """
    Wraps the given code in a markdown code fence for display.
    """
    return f"```{language}\n{code}\n```"


def format_tasks_as_list(tasks):
    """Formats a list of tasks as a numbered list."""
    return "\n".join(f"{i + 1}. {task.taskname}" for i, task in enumerate(tasks))

def format_tasks_as_list_with_id(tasks):
    """Formats a list of tasks as a numbered list."""
    return "\n".join(f"{i + 1}. {task.taskname} ({task.taskid})" for i, task in enumerate(tasks))


def format_future_tasks_as_list(tasks):
    """Formats a list of tasks as a numbered list."""
    return "\n".join(f"{i + 1}. {task.taskname} ({task.earlieststarttime})" for i, task in enumerate(tasks))


def format_artifacts_as_list(artifacts):
    """
    Format a list of artifacts into a numbered string.
    Each artifact is expected to be either a dict with a 'url'
    or an object with a corresponding attribute.
    Only the index and the URL are shown.
    """
    if not artifacts:
        return "No artifacts found."

    lines = []
    for idx, artifact in enumerate(artifacts, 1):
        if isinstance(artifact, dict):
            url = artifact.get("url", "No URL")
        else:
            url = getattr(artifact, "url", "No URL")
        lines.append(f"{idx}. {url}")
    return "\n".join(lines)



def format_box_list(box_list : list[str]) -> str:
    """
    Converts a list of boxes into a presentable ordered string list.

    Returns:
        A string with each box name on a new line, prefixed with its order number.
    """
    return "\n".join(f"{i + 1}. {box}" for i, box in enumerate(box_list))


def format_ai_model_list(models_by_provider: dict) -> str:
    lines = []
    for provider, model_ids in models_by_provider.items():
        lines.append(f"{provider}:")
        for i, model_id in enumerate(model_ids, 1):
            lines.append(f"  {i}. {model_id}")
    return "\n".join(lines)


def format_ai_model_grouped_list(models_by_provider: dict) -> str:
    lines = []
    for i, (provider, model_ids) in enumerate(models_by_provider.items(), 1):
        lines.append(f"{i}. {provider}:")
        for j, model_id in enumerate(model_ids, 1):
            lines.append(f"  {j}. {model_id}")
    return "\n".join(lines)



def format_ai_model_flat_list(models_by_provider: dict) -> str:
    lines = []
    index = 1
    for provider, models in models_by_provider.items():
        for model in models:
            lines.append(f"{index}. {provider}: {model['model_id']} ({model['description']})")
            index += 1
    return "\n".join(lines)

