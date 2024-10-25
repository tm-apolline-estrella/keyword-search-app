# Import local modules
from src.components.coach_ai.modules.librarian.constants import LibrarianRewriteInstruction


def expand_rewrite_instruction(rewrite_instruction: LibrarianRewriteInstruction):
    expanded_instruction = rewrite_instruction.value

    if rewrite_instruction in [
        LibrarianRewriteInstruction.TAGLISH,
        LibrarianRewriteInstruction.CEBUANO,
    ]:
        expanded_instruction = f"Rewrite the message in {rewrite_instruction.value}."

    return expanded_instruction
