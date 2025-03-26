from pandas import DataFrame

from app.config import table_dir
from app.metadata.utils import get_meta, process_long


def main():
    meta_list = get_meta()
    meta_long = process_long(meta_list)
    file_path = table_dir / "metadata.csv"
    DataFrame(meta_long).to_csv(file_path, encoding="utf-8-sig", index=False)


if __name__ == "__main__":
    main()
