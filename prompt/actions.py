import json


def convert_signatures(action_list):
    return "\n".join([json.dumps(tool) for tool in action_list])


def get_action_prompts(action_list):
    action_list = [action for action in action_list if "available" not in action or action["available"]]
    available_list = []
    for action in action_list:
        entry = {}
        for k, v in action.items():
            if "available" not in k:
                entry[k] = v
        available_list.append(entry)
    prompt = f"""
Duration descriptor is -1 means that the
The set of actions available to you are: 
{convert_signatures(available_list)}
""".strip()

    return prompt


# test_signatures = [
#     {
#         "name": "message",
#         "description": "message with someone",
#         "parameters": [
#             {
#                 "name": "to",
#                 "type": "string",
#                 "description": "The name of person to be messaged",
#             },
#             {
#                 "name": "content",
#                 "type": "string",
#                 "description": "The content of the message. It should be as daily communication",
#             },
#         ],
#     },
#     {
#         "name": "trade",
#         "description": "perform a trade with another agent",
#         "parameters": [
#             {
#                 "name": "with",
#                 "type": "string",
#                 "description": "The name of person to trade",
#             },
#             {
#                 "name": "item",
#                 "type": "string",
#                 "description": "The name of the item to be traded",
#             },
#             {
#                 "name": "amount",
#                 "type": "int",
#                 "description": "the amount of item to be trade",
#             },
#             {
#                 "name": "price",
#                 "type": "float",
#                 "description": "the single price of an item",
#             },
#         ],
#     }
# ]
