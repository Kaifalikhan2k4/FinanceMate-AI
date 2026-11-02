from src.assistant.query_handler import handle_question


def main():

    questions = [
        "What is our total revenue and profit?",
        "Which department spends the most?",
        "Show me the top expenses",
        "Show reconciliation summary",
        "Find bank discrepancies",
        "Show monthly financial summary",
        "Show category-wise expenses",
        "Tell me a joke",
    ]

    for question in questions:

        print("\n====================================")
        print("QUESTION:", question)

        result = handle_question(question)

        print("RESULT TYPE:", result["type"])
        print("RESULT:", result)


if __name__ == "__main__":
    main()