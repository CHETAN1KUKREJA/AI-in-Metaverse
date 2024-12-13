def get_system_prompt_entry(idx, system_entry):
    ret = str(idx + 1) + ". "
    match system_entry["type"]:
        case "conflict":
            assert system_entry["during"] == "talk"
            other_agent = system_entry["details"]["other"]
            talked_content = system_entry["details"]["talked_content"]
            ret += f'Another agent "{other_agent}" was talking, and what you just said "{talked_content}" is covered. You may need to repeat it.'
            return ret
        case "invalid-parameter-name":
            ret += f"You must be aware that during your last action \"{system_entry['during']}\", some parameters are invalid. Consider whether to extract the valid parameters for \"{system_entry['during']}\" and repeat it."
            return ret
        case "parameter-not-permitted":
            ret += f"You must be aware that during your last action \"{system_entry['during']}\", some parameters are not permitted. Consider whether to extract the permitted parameters for \"{system_entry['during']}\" and repeat it."
            return ret
        case "invalid-action-name":
            ret += f"You must be aware that the last action you generated \"{system_entry['during']}\" is invaild. You are not allowed to perform it."
            return ret
        case "action-not-permitted":
            ret += f"You must be aware that the last action you generated \"{system_entry['during']}\" is invaild. You are not allowed to perform it."
            return ret


def get_system_prompt(system_list):
    system_prompt_list = [get_system_prompt_entry(idx, system_entry) for idx, system_entry in enumerate(system_list)]
    system_prompt = "\n".join(system_prompt_list)
    return system_prompt
