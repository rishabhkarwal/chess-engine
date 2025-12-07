from pathlib import Path

def load_fens(path: str) -> list[str]:
    """return a list of FEN strings"""
    file = Path(path)
    with file.open() as f:
        return [line.strip() for line in f if line.strip()]

start_positions = load_fens("book.txt")