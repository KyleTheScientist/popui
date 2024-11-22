pip install --upgrade build && rm dist/*; python -m build
pip install --upgrade twine && twine upload dist/*
