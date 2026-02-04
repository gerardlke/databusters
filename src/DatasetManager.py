import io
import zipfile
import pandas as pd
from pathlib import Path


class DatasetManager:
    """
    Manages datasets and all data parsing functions
    """

    def __init__(self):
        self.datasets = []
        self.filemap = {}


    def add_dataset(self, dataset):
        """Adds a dataset to the dataset object
        
        :param self: Description
        :param dataset: Description
        """
        self.datasets.append(Path(dataset))
        self.extract_files(Path(dataset))


    def extract_files(self, root_path):
        """Creating a dict mapping of files in zipped dataset to workaround nested zips
        
        Returns:
            Mapping of {filename : parent}
        """
        if not root_path.exists():
            print(f"Warning: {root_path} not found.")
            return

        with zipfile.ZipFile(root_path, 'r') as z:
            for name in z.namelist():
                self.filemap[name] = (root_path, None)
                
                # Index nested contents too
                if name.endswith('.zip'):
                    with z.open(name) as nested_zip_data:
                        with zipfile.ZipFile(io.BytesIO(nested_zip_data.read())) as nz:
                            for nested_name in nz.namelist():
                                # Store the nested name and its parent zip
                                self.filemap[nested_name] = (root_path, name)


    def get_df(self, filename):
        """Retrieves dataframe for a file using mapping
        
        Args:
            filename: str
        
        Returns:
            df: pd.dataframe
        """
        key = next((k for k in self.filemap if filename in k), None)
        
        if not key:
            raise FileNotFoundError(f"'{filename}' not found in datasets")

        root_path, nested_name = self.filemap[key]

        with zipfile.ZipFile(root_path, 'r') as root_z:
            if nested_name is None:
                with root_z.open(key) as f:
                    return pd.read_csv(f)
            else:
                with root_z.open(nested_name) as nested_z_bytes:
                    with zipfile.ZipFile(io.BytesIO(nested_z_bytes.read())) as nested_z:
                        with nested_z.open(key) as f:
                            return pd.read_csv(f)


    def unix_to_datetime(self, unix_time):
        """Helper function to convert unix time to datetime object
        
        Args:
            unix_time: Unix time to convert
        """
        return pd.to_datetime(unix_time, unit="s", utc=True).dt.tz_localize(None)


    def string_to_datetime(self, string):
        """Helper function to convert unix time to datetime object
        
        Args:
            unix_time: Unix time to convert
        """
        return pd.to_datetime(string, format='%m/%d/%Y')
    

    def combine_dfs(self, dfs, on, how):
        """Helper function to combine multiple 

        Args:
            dfs: List of Dataframes to combine together
        """
        if len(dfs) == 0: return 

        final_df = dfs[0]
        for df in dfs[1:]:
            final_df = final_df.merge(df, on=on, how=how)

        return final_df

    def clean_fred(self, df, value_col):
        """Cleaning data comes from Federal Reserve data (FRED): observation_date + value_col
        
        Args:
            df: Dataframe to clean
            value_col: 
        """
        out = df.copy()
        out["Date"] = self.unix_to_datetime(out["observation_date"])
        out[value_col] = pd.to_numeric(out[value_col], errors="coerce")
        out = out[["Date", value_col]].dropna().sort_values("Date")
        return out


    def clean_yahoo(self, df_raw):
        """Cleaning data from Yahoo! finance
            Yahoo-style exports in this dataset often have 2 metadata rows at the top.
            We detect the first row whose 'Price' field looks like a Date, then parse.

        Args:
            df_raw: 
        """
        df = df_raw.copy()

        # Find actual header if first row is metadata
        if "Price" not in df.columns:
            df.columns = df.iloc[0].tolist()
            df = df.iloc[1:].copy()

        # Find first row where "Price" can be parsed as a Date
        start_idx = None
        for i in range(min(len(df), 50)):
            try:
                pd.to_datetime(df.loc[df.index[i], "Price"])
                start_idx = i
                break
            except Exception:
                pass

        if start_idx is None:
            raise ValueError("Couldn't detect where OHLCV data starts in the ^VIX file.")

        df = df.iloc[start_idx:].copy()
        df = df.rename(columns={"Price": "Date"})
        df["Date"] = self.unix_to_datetime(df["Date"])

        for col in ["Close", "High", "Low", "Open", "Volume"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        df = df.dropna(subset=["Date", "Close"]).sort_values("Date")
        return df[["Date", "Open", "High", "Low", "Close", "Volume"]].copy()


    def clean_price(self, df, rename=""):
        """Cleaning price data

        Args: 
            df: Dataframe to clean
        """
        # Convert timestamp
        if "timestamp" in df.columns:
            df["Date"] = self.unix_to_datetime(df["timestamp"])

        # Ensure price columns are numeric
        price_cols = [col for col in df.columns if col != "Date"]
        df[price_cols] = df[price_cols].apply(pd.to_numeric, errors="coerce")
        
        # Remove missing values
        df.dropna(subset=price_cols)

        # Rename columns if need be
        df.rename(columns={col: f"{rename}_{col}" for col in price_cols}, inplace=True)

        return df[["Date"] + [f"{rename}_{col}" for col in price_cols]].sort_values("Date")
