from pathlib import Path
import os

api_file = Path(os.path.abspath("backend/app/api/evaluation.py"))
print("api_file:", api_file)
root_dir = api_file.resolve().parent.parent.parent.parent.parent
print("root_dir:", root_dir)
eval_dir = root_dir / 'backend' / 'evaluation' / 'final'
print("eval_dir:", eval_dir)
