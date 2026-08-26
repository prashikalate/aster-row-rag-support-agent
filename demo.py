from src.agent.agent import SupportAgent


def main():
    agent = SupportAgent()

    print("=" * 60)
    print("Aster & Row Support Agent")
    print("Type 'exit' to quit.")
    print("=" * 60)

    while True:
        query = input("\nYou: ").strip()

        if query.lower() == "exit":
            break

        if not query:
            continue

        result = agent.handle(query)

        print(f"\nAgent: {result.answer}")

        if result.sources:
            print("\nSources:")
            for source in result.sources:
                print(f"  - {source}")

        print(f"\nAction: {result.action}")
        print(f"Human handoff/input required: {result.requires_input}")


if __name__ == "__main__":
    main()