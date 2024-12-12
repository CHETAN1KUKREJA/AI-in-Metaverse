def get_contracts_prompt(contracts):
    # Generate a detailed description for the contracts.
    
    if not contracts:
        return "You are not engaged in any contracts."

    contract_descriptions = ["\nYou are engaged in the following contracts:"]
    for contract in contracts:
        contract_desc = (
            f"With agent {contract['other']}, valid until {contract['expires']}, you have agreed that:\n"
            f"{contract['content']}"
        )
        contract_descriptions.append(contract_desc)
    return "\n".join(contract_descriptions)
