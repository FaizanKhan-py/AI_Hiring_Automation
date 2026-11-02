
"""Resume Loader - AI Hiring Automation."""

from langchain_community.document_loaders import (
    DirectoryLoader,
    PyPDFLoader,
    Docx2txtLoader
)


# Job positions and their folder names
POSITIONS = {
    "AI Engineer": "AI_Engineer",
    "DevOps": "DevOps",
    "HR": "HR",
    "Business Developer": "Business_Developer",
    "Full Stack Developer": "FullStack_Developer"
}


# Experience levels and their folder names
LEVELS = {
    "Junior": "Junior",
    "Mid-Level": "MidLevel",
    "Senior": "Senior"
}


def load_folder(folder_path):
    """Load PDF and DOCX resumes from a folder."""

    pdf_loader = DirectoryLoader(
        folder_path,
        glob="*.pdf",
        loader_cls=PyPDFLoader
    )

    docx_loader = DirectoryLoader(
        folder_path,
        glob="*.docx",
        loader_cls=Docx2txtLoader
    )

    pdf_documents = pdf_loader.load()
    docx_documents = docx_loader.load()

    return pdf_documents + docx_documents


def load_resumes():
    """Load resumes and organize them into separate collections."""

    resume_collections = {}

    for position, position_folder in POSITIONS.items():

        for level, level_folder in LEVELS.items():

            folder_path = (
                f"resumes/{position_folder}/{level_folder}/"
            )

            collection_name = (
                f"{level.lower().replace('-', '')}_"
                f"{position_folder.lower()}"
            )

            documents = load_folder(folder_path)

            resume_collections[collection_name] = documents

            print(
                f"{collection_name}: "
                f"{len(documents)} documents loaded"
            )

    return resume_collections


if __name__ == "__main__":

    all_resumes = load_resumes()

    total_documents = sum(
        len(documents)
        for documents in all_resumes.values()
    )

    print(f"\nTotal documents loaded: {total_documents}")
