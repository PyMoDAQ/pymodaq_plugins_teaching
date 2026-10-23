"""Run the code cells of the corrected notebooks of the module C against the data files of the `data` folder.

The notebooks are executed in a temporary copy of the repository folders, without display: the cells that need
a Qt viewer (magics and `.plot('qt')`) are skipped.
"""
import json
import shutil
from pathlib import Path

import matplotlib
import pytest

matplotlib.use('Agg')

ROOT = Path(__file__).parent.parent
NOTEBOOKS = sorted((ROOT / 'notebooks').glob('0*.ipynb'))


def code_cells(notebook: Path) -> list[str]:
    cells = json.loads(notebook.read_text(encoding='utf-8'))['cells']
    return [''.join(cell['source']) for cell in cells if cell['cell_type'] == 'code']


def needs_display(source: str) -> bool:
    return source.lstrip().startswith('%') or ".plot('qt')" in source


@pytest.mark.parametrize('notebook', NOTEBOOKS, ids=lambda path: path.stem)
def test_notebook_runs(notebook, tmp_path, monkeypatch):
    shutil.copytree(ROOT / 'notebooks', tmp_path / 'notebooks')
    shutil.copytree(ROOT / 'data', tmp_path / 'data')
    monkeypatch.chdir(tmp_path / 'notebooks')
    namespace = {'__name__': '__main__'}
    for source in code_cells(tmp_path / 'notebooks' / notebook.name):
        if needs_display(source):
            continue
        exec(compile(source, notebook.name, 'exec'), namespace)
