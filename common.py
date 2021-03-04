DEFAULT_START_DATE = "1999-03-10"
DEFAULT_END_DATE = "2021-02-26"


def get_start_row(dataframe, start_date) -> int:
    for i in range(dataframe.Date.size):
        if dataframe.Date[i] == start_date:
            return i
    raise Exception(f"Configured start date {start_date} not found in data.")


def output(line: str, file_path: str) -> None:
    print(line)
    with open(file_path, 'a+') as _file:
        _file.write(line + '\n')


def get_pct_change_str(start: int, end: int) -> str:
    return str(((end - start) / start) * 100).split('.')[0] + "%"
