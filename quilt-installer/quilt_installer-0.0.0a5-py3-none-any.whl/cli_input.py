import click


def wait_for_cli_input(prompt, default_val, is_password=False, is_required=True, show_default=True):
    # Special handling when default_value=None because click will keep prompting until user_input is not None
    if default_val is None and is_required:
        prompt += " [required]"
        tmp_default_val = None  # Force click to keep prompting until input is given
    elif default_val is None and not is_required:
        if show_default:
            prompt += " [default=None]"
        tmp_default_val = "__None"  # Trick click into accepting the default value as None
    else:
        if show_default:
            prompt += f" [default={default_val}]"
        tmp_default_val = default_val

    user_input = click.prompt(prompt,
                              default=tmp_default_val,
                              hide_input=is_password,
                              confirmation_prompt=is_password,
                              show_default=False)

    if user_input == "__None" or user_input.strip() == "":
        return default_val

    return user_input.strip()
