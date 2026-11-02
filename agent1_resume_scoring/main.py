
"""AI Hiring Automation - Resume Scoring Agent."""

import re

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from resume_loader import load_resumes

from promptsfolder import (
    ai_engineer,
    business_dev,
    devops,
    fullstack_dev,
    hr
)


# Load environment variables
load_dotenv()


# Initialize Azure OpenAI
llm = ChatOpenAI(
    model="gpt-4.1-mini",
    base_url="https://mychatbot2.openai.azure.com/openai/v1",
    temperature=0
)


# Job positions and their prompt files
POSITION_PROMPTS = {
    "AI Engineer": ai_engineer,
    "DevOps": devops,
    "HR": hr,
    "Business Developer": business_dev,
    "Full Stack Developer": fullstack_dev
}


# Position names matching resume_loader.py collection names
POSITION_KEYS = {
    "AI Engineer": "ai_engineer",
    "DevOps": "devops",
    "HR": "hr",
    "Business Developer": "business_developer",
    "Full Stack Developer": "fullstack_developer"
}


# Experience levels
LEVELS = {
    "Junior": "junior",
    "Mid-Level": "midlevel",
    "Senior": "senior"
}


def show_menu(options, title):
    """Display a numbered menu and return the selected option."""

    print(f"\n===== {title} =====")

    for index, option in enumerate(options, start=1):
        print(f"{index}. {option}")

    choice = input("\nEnter your choice: ").strip()

    if not choice.isdigit():
        print("Invalid choice!")
        return None

    choice = int(choice)

    if not 1 <= choice <= len(options):
        print("Invalid choice!")
        return None

    return options[choice - 1]


def select_resumes(documents):
    """Allow HR to select which resumes to score."""

    print("\n===== SELECT RESUMES =====")
    print("1. Score all resumes")
    print("2. Score a specific resume")
    print("3. Back")

    choice = input("\nEnter your choice: ").strip()

    if choice == "1":
        return documents

    elif choice == "2":

        # Get unique resume filenames
        sources = list(dict.fromkeys(
            document.metadata.get("source", "Unknown")
            for document in documents
        ))

        print("\nAvailable Resumes:")

        for index, source in enumerate(sources, start=1):
            print(f"{index}. {source}")

        resume_choice = input(
            "\nSelect resume number: "
        ).strip()

        if not resume_choice.isdigit():
            print("Invalid choice!")
            return None

        resume_choice = int(resume_choice)

        if not 1 <= resume_choice <= len(sources):
            print("Invalid choice!")
            return None

        selected_source = sources[resume_choice - 1]

        return [
            document for document in documents
            if document.metadata.get("source") == selected_source
        ]

    elif choice == "3":
        return None

    else:
        print("Invalid choice!")
        return None


def score_resumes(documents, position, level):
    """Evaluate selected resumes and display only their scores."""

    prompt_module = POSITION_PROMPTS[position]
    prompt_key = LEVELS[level]

    # Check whether the required prompt exists
    if not hasattr(prompt_module, "prompts"):
        print(f"Error: No prompts dictionary found for {position}.")
        return

    if prompt_key not in prompt_module.prompts:
        print(f"Error: {prompt_key} prompt not found for {position}.")
        return

    selected_prompt = prompt_module.prompts[prompt_key]

    # Create LangChain chain
    chain = selected_prompt | llm

    # Group pages belonging to the same resume
    grouped_resumes = {}

    for document in documents:

        source = document.metadata.get("source", "Unknown")

        if source not in grouped_resumes:
            grouped_resumes[source] = []

        grouped_resumes[source].append(document.page_content)

    print("\n===== RESUME SCORING STARTED =====")

    # Evaluate each resume
    for index, (source, pages) in enumerate(
        grouped_resumes.items(), start=1
    ):

        resume_text = "\n".join(pages)

        try:

            result = chain.invoke({
                "resume": resume_text,
                "level": level
            })

            # Extract numerical score from AI response
            score_match = re.search(
                r"SCORE:\s*(\d+)\s*/\s*100",
                result.content,
                re.IGNORECASE
            )

            print("\n" + "=" * 50)
            print(f"Candidate: {index}")
            print(f"Resume: {source}")
            print(f"Position: {position}")
            print(f"Experience Level: {level}")

            if score_match:
                score = int(score_match.group(1))
                print(f"Score: {score}/100")
            else:
                print("Score: Could not extract score")

            print("=" * 50)

        except Exception as error:
            print(f"\nError scoring {source}: {error}")

    print("\n===== SCORING COMPLETED =====")


def main():
    """Run the AI Resume Scoring System."""

    print("\n===================================")
    print("      AI RESUME SCORING SYSTEM")
    print("===================================")

    # Load all resumes
    print("\nLoading resumes...")

    try:
        all_resumes = load_resumes()

    except Exception as error:
        print(f"\nError loading resumes: {error}")
        return

    print("\nResume loading completed!")

    while True:

        # Step 1: Select job position
        position = show_menu(
            list(POSITION_PROMPTS.keys()),
            "SELECT JOB POSITION"
        )

        if position is None:
            continue

        # Step 2: Select experience level
        level = show_menu(
            list(LEVELS.keys()),
            "SELECT EXPERIENCE LEVEL"
        )

        if level is None:
            continue

        # Step 3: Find the corresponding resume collection
        collection_key = (
            f"{LEVELS[level]}_{POSITION_KEYS[position]}"
        )

        documents = all_resumes.get(collection_key, [])

        if not documents:
            print(
                f"\nNo resumes found for "
                f"{position} - {level}."
            )
            continue

        print(f"\nFound {len(documents)} documents.")

        # Step 4: Select resumes
        selected_documents = select_resumes(documents)

        if not selected_documents:
            continue

        # Step 5: Score selected resumes
        score_resumes(
            selected_documents,
            position,
            level
        )

        # Step 6: Continue or exit
        again = input(
            "\nDo you want to score more resumes? (y/n): "
        ).strip().lower()

        if again != "y":
            print(
                "\nThank you for using AI Resume Scoring System!"
            )
            break


if __name__ == "__main__":
    main()
