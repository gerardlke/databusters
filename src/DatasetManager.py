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


    def convert_to_datetime(self, unix_time):
        """Helper function to convert unix time to datetime object
        
        Args:
            unix_time: Unix time to convert
        """
        return pd.to_datetime(unix_time, unit="s", utc=True).dt.tz_localize(None)
    

    def clean_fred(self, df, value_col):
        """FRED-style: observation_date + value_col"""
        out = df.copy()
        out["Date"] = self.convert_to_datetime(out["observation_date"])
        out[value_col] = pd.to_numeric(out[value_col], errors="coerce")
        out = out[["Date", value_col]].dropna().sort_values("Date")
        return out


    def clean_yahoo(self, df_raw: pd.DataFrame) -> pd.DataFrame:
        """
        Yahoo-style exports in this dataset often have 2 metadata rows at the top.
        We detect the first row whose 'Price' field looks like a Date, then parse.
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
        df["Date"] = self.convert_to_datetime(df["Date"])

        for col in ["Close", "High", "Low", "Open", "Volume"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        df = df.dropna(subset=["Date", "Close"]).sort_values("Date")
        return df[["Date", "Open", "High", "Low", "Close", "Volume"]].copy()
    

    def string_to_unix(self, string):
        """Helper function to convert string time to unix object
        
        Args:
            unix_time: Unix time to convert
        """
        return pd.to_datetime(string).timestamp() * 1000
