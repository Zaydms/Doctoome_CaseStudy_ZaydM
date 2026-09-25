#script to clean and normalize the visitors data.
def normalize_visitors(df):
    df = df.copy() 

    df["gender"] = (
        df["gender"]
        .str.strip()
        .str.lower()
        .replace({
            "m": "male",
            "f": "female"
        })
        .fillna("not provided")
    )

    df["region"] = (
        df["region"]
        .str.strip()
        .str.lower()
        .str.normalize("NFKD")
        .str.encode("ascii", errors="ignore")
        .str.decode("utf-8")
        .str.replace(r"[\s_-]+", "-", regex=True)
        .fillna("not provided")
    )

    return df

