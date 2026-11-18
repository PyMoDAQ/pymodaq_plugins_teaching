"""Check the exercise notebooks of the module C (the notebooks with holes `...` of the `notebooks` folder).

Each code cell with a hole is tagged `exercise`. The cells before the first exercise (imports, paths, objects given
to the trainees) must run against the data files of the `data` folder, without display: the cells that need a Qt
viewer (magics and `.plot('qt')`) are skipped. The corrected notebooks are in the branch `correction-module-c`.
"""
import ast
import json
import shutil
from pathlib import Path

import matplotlib
import pytest

matplotlib.use('Agg')

ROOT = Path(__file__).parent.parent
NOTEBOOKS = sorted((ROOT / 'notebooks').glob('0*.ipynb'))
DATA_FILES = ('scan_photodiode.h5', 'spectrum_naverage200.h5', 'continuous_spectra.h5')


def code_cells(notebook: Path) -> list[dict]:
    cells = json.loads(notebook.read_text(encoding='utf-8'))['cells']
    return [cell for cell in cells if cell['cell_type'] == 'code']


def source(cell: dict) -> str:
    return ''.join(cell['source'])


def is_exercise(cell: dict) -> bool:
    return 'exercise' in cell['metadata'].get('tags', [])


def needs_display(text: str) -> bool:
    return text.lstrip().startswith('%') or ".plot('qt')" in text


def without_magics(text: str) -> str:
    return '\n'.join(line for line in text.split('\n') if not line.lstrip().startswith('%'))


def test_there_are_notebooks():
    assert len(NOTEBOOKS) > 0


@pytest.mark.parametrize('name', DATA_FILES)
def test_data_file_exists(name):
    assert (ROOT / 'data' / name).is_file()


@pytest.mark.parametrize('notebook', NOTEBOOKS, ids=lambda path: path.stem)
def test_holes_are_tagged_and_cells_are_valid_python(notebook):
    for cell in code_cells(notebook):
        text = source(cell)
        if '...' in text:
            assert is_exercise(cell), f'untagged cell with a hole in {notebook.name}:\n{text}'
        ast.parse(without_magics(text))  # a hole must not be a syntax error


@pytest.mark.parametrize('notebook', NOTEBOOKS, ids=lambda path: path.stem)
def test_given_cells_run(notebook, tmp_path, monkeypatch):
    shutil.copytree(ROOT / 'notebooks', tmp_path / 'notebooks')
    shutil.copytree(ROOT / 'data', tmp_path / 'data')
    monkeypatch.chdir(tmp_path / 'notebooks')
    namespace = {'__name__': '__main__'}
    for cell in code_cells(tmp_path / 'notebooks' / notebook.name):
        if is_exercise(cell):
            break
        text = source(cell)
        if needs_display(text):
            continue
        exec(compile(text, notebook.name, 'exec'), namespace)
