from smolagents import CodeAgent, tool, InferenceClientModel

# Tool to suggest a menu based on the occasion
@tool
def suggest_menu(occasion: str) -> str:
    """
    Suggests a menu based on the occasion.
    Args:
        occasion (str): The type of occasion for the party. Allowed values are:
                        - "casual": Menu for casual party.
                        - "formal": Menu for formal party.
                        - "superhero": Menu for superhero party.
                        - "custom": Custom menu.
    """
    if occasion == "casual":
        return "Rice,sabhji, Dal,Roti,Salad,Sweets"
    elif occasion == "formal":
        return "3-course dinner with Juice and Icecreams"
    elif occasion == "superhero":
        return "Buffet with high-energy and healthy food."
    else:
        return "Custom menu for the butler."

agent = CodeAgent(tools=[suggest_menu], model=InferenceClientModel())

agent.run("Prepare a formal menu for the party.")