from loader import load_all_files

data = load_all_files()

print(data["companies"].columns.tolist())
