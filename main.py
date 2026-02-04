from src.DatasetManager import DatasetManager
from src.Visualiser import Visualiser

if __name__ == "__main__":
    dm = DatasetManager()
    dm.add_dataset(r"./datasets/gfc.zip")

    # Retrieve dataframes
    vix = dm.clean_yahoo(dm.get_df("VIX.csv"))
    ted = dm.clean_fred(dm.get_df("TEDRATE.csv"), "TEDRATE")
    t3m = dm.clean_fred(dm.get_df("WGS3MO.csv"), "WGS3MO")

    aig = dm.clean_yahoo(dm.get_df("AIG"))
    citi = dm.clean_yahoo(dm.get_df("C.csv"))
    jpm = dm.clean_yahoo(dm.get_df("JPM"))
    
    dji = dm.clean_yahoo(dm.get_df("DJI"))
    gspc = dm.clean_yahoo(dm.get_df("GSPC"))

    # Build indicators
    ted_threshold = 0.593827727 + 3 * 0.560750914  # Using mean and stdev of ted in jan 2007
    ted["Panic_Signal"] = ted["TEDRATE"].where(ted["TEDRATE"] > ted_threshold, ted_threshold)

    for df in [vix, dji, gspc, aig, citi, jpm]:
        df['Volatility'] = (df["High"] - df["Low"]) / df["Close"]
        df['Rolling_Volatility'] = df['Close'].pct_change().rolling(window=21).std()
        df['Selling_Pressure'] = df['Volume'] * (df['Open'] - df['Close'])
        
        df["Normalized_Close"] = df["Close"] / df["Close"].loc[
            (dm.string_to_datetime("01/01/2008") <= df["Date"]) & (df["Date"] <= dm.string_to_datetime("01/31/2008"))
        ].iloc[0]

        peak = df.loc[df["Date"].between("2008-01-01", "2008-12-31"), "Close"].max()
        df["Drawdown"] = (peak - df["Close"]) / peak * 100

    # Rename frames
    vix = dm.clean_price(vix, "vix")
    aig = dm.clean_price(aig, "aig")
    citi = dm.clean_price(citi, "citi")
    jpm = dm.clean_price(jpm, "jpm")
    dji = dm.clean_price(dji, "dji")
    gspc = dm.clean_price(gspc, "gspc")

    # Combine all dataframes into 1 and Visualise
    vis = Visualiser(dm.combine_dfs(
        [vix, ted, t3m, aig, citi, jpm, dji, gspc],
        on="Date",
        how="outer"
    ).sort_values("Date"))
    

    graphs = [
        {
            "Title": "Market Volatility",
            "Traces": [
                {
                    "Name": "VIX",
                    "x": "Date",
                    "y": "vix_Volatility",
                    "Color": "red"
                },
                {
                    "Name": "AIG",
                    "x": "Date",
                    "y": "aig_Volatility",
                    "Color": "orange"
                },
                {
                    "Name": "CITI",
                    "x": "Date",
                    "y": "citi_Volatility",
                    "Color": "yellow"
                },
                {
                    "Name": "JPM",
                    "x": "Date",
                    "y": "jpm_Volatility",
                    "Color": "yellowgreen"
                },
                {
                    "Name": "DJI",
                    "x": "Date",
                    "y": "dji_Volatility",
                    "Color": "green"
                },
                {
                    "Name": "GSPC",
                    "x": "Date",
                    "y": "gspc_Volatility",
                    "Color": "aqua"
                }
            ]
        },
        {
            "Title": "Market Rolling Volatility",
            "Traces": [
                {
                    "Name": "VIX",
                    "x": "Date",
                    "y": "vix_Rolling_Volatility",
                    "Color": "red"
                },
                {
                    "Name": "AIG",
                    "x": "Date",
                    "y": "aig_Rolling_Volatility",
                    "Color": "orange"
                },
                {
                    "Name": "CITI",
                    "x": "Date",
                    "y": "citi_Rolling_Volatility",
                    "Color": "yellow"
                },
                {
                    "Name": "JPM",
                    "x": "Date",
                    "y": "jpm_Rolling_Volatility",
                    "Color": "yellowgreen"
                },
                {
                    "Name": "DJI",
                    "x": "Date",
                    "y": "dji_Rolling_Volatility",
                    "Color": "green"
                },
                {
                    "Name": "GSPC",
                    "x": "Date",
                    "y": "gspc_Rolling_Volatility",
                    "Color": "aqua"
                }
            ]
        },
        {
            "Title": "Market Normalized Close",
            "Traces": [
                {
                    "Name": "VIX",
                    "x": "Date",
                    "y": "vix_Normalized_Close",
                    "Color": "red"
                },
                {
                    "Name": "AIG",
                    "x": "Date",
                    "y": "aig_Normalized_Close",
                    "Color": "orange"
                },
                {
                    "Name": "CITI",
                    "x": "Date",
                    "y": "citi_Normalized_Close",
                    "Color": "yellow"
                },
                {
                    "Name": "JPM",
                    "x": "Date",
                    "y": "jpm_Normalized_Close",
                    "Color": "yellowgreen"
                },
                {
                    "Name": "DJI",
                    "x": "Date",
                    "y": "dji_Normalized_Close",
                    "Color": "green"
                },
                {
                    "Name": "GSPC",
                    "x": "Date",
                    "y": "gspc_Normalized_Close",
                    "Color": "aqua"
                }
            ]
        },
        {
            "Title": "Market Drawdown",
            "Traces": [
                {
                    "Name": "VIX",
                    "x": "Date",
                    "y": "vix_Drawdown",
                    "Color": "red"
                },
                {
                    "Name": "AIG",
                    "x": "Date",
                    "y": "aig_Drawdown",
                    "Color": "orange"
                },
                {
                    "Name": "CITI",
                    "x": "Date",
                    "y": "citi_Drawdown",
                    "Color": "yellow"
                },
                {
                    "Name": "JPM",
                    "x": "Date",
                    "y": "jpm_Drawdown",
                    "Color": "yellowgreen"
                },
                {
                    "Name": "DJI",
                    "x": "Date",
                    "y": "dji_Drawdown",
                    "Color": "green"
                },
                {
                    "Name": "GSPC",
                    "x": "Date",
                    "y": "gspc_Drawdown",
                    "Color": "aqua"
                }
            ]
        },
        {
            "Title": "Financial Sector Volume",
            "Traces": [
                {
                    "Name": "AIG",
                    "x": "Date",
                    "y": "aig_Volume",
                    "Color": "blue"
                },
                {
                    "Name": "Citigroup",
                    "x": "Date",
                    "y": "citi_Volume",
                    "Color": "green"
                },
                {
                    "Name": "JPMorgan",
                    "x": "Date",
                    "y": "jpm_Volume",
                    "Color": "white"
                }
            ]
        },
        {
            "Title": "Financial Sector Selling Pressure",
            "Traces": [
                {
                    "Name": "AIG",
                    "x": "Date",
                    "y": "aig_Selling_Pressure",
                    "Color": "blue"
                },
                {
                    "Name": "Citigroup",
                    "x": "Date",
                    "y": "citi_Selling_Pressure",
                    "Color": "green"
                },
                {
                    "Name": "JPMorgan",
                    "x": "Date",
                    "y": "jpm_Selling_Pressure",
                    "Color": "white"
                }
            ]
        },
        {
            "Title": "Systemic Stress",
            "Traces": [
                {
                    "Name": "TED Spread",
                    "x": "Date",
                    "y": "TEDRATE",
                    "Color": "orange"
                },
                {
                    "Name": "TED Threshold exceeded",
                    "x": "Date",
                    "y": "Panic_Signal",
                    "Color": "aqua"
                },
                {
                    "Name": "Secondary Market Rate",
                    "x": "Date",
                    "y": "WGS3MO",
                    "Color": "green"
                }
            ]
        }
    ]
    vis.plot_indicators(title="Global Financial Crisis", graphs=graphs)