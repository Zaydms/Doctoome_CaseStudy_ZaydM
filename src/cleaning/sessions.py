#script to clean and normalize the sessions data.
def normalize_sessions(df):
    df = df.copy()

    df["acquisition_source"] = (
        df["acquisition_source"]
        .str.strip()
        .str.lower()
        .str.normalize("NFKD")
        .str.encode("ascii", errors="ignore")
        .str.decode("utf-8")
        .str.replace(r"[\s_-]+", "-", regex=True)
        .fillna("unprovided_data")
    )
    return df