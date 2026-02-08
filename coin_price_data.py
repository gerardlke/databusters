from src.DatasetManager import DatasetManager
from src.Visualiser import Visualiser
from datetime import datetime
import pandas as pd
import numpy as np


if __name__ == "__main__":
    dm = DatasetManager()
    dm.add_dataset(r"./datasets/ERC20-stablecoins.zip")

    # Retrieve dataframes
    dai = dm.get_df("dai_price_data")
    pax = dm.get_df("pax_price_data")
    usdc = dm.get_df("usdc_price_data")
    usdt = dm.get_df("usdt_price_data")
    ustc = dm.get_df("ustc_price_data")
    wluna = dm.get_df("wluna_price_data")
    
    # Convert timestamp 
    if ustc['timestamp'].dtype != 'datetime64[ns]':
        # Try converting from milliseconds
        ustc['Date'] = pd.to_datetime(ustc['timestamp'], unit='s')
    else:
        ustc['Date'] = ustc['timestamp']
    
    ustc = ustc.sort_values('Date').reset_index(drop=True)
    
    print(f"\nConverted dates - first few:")
    print(ustc[['Date', 'close']].head())
    print(f"\nDate range: {ustc['Date'].min()} to {ustc['Date'].max()}")
    
    # Calculate peg deviation and volatility
    ustc['peg_deviation'] = abs(ustc['close'] - 1)
    ustc['volatility'] = (ustc['high'] - ustc['low']) / ustc['close']
    
    # Define pre-crisis window
    crisis_date = pd.Timestamp('2022-05-07')
    pre_crisis_start = crisis_date - pd.Timedelta(weeks=2)
    pre_crisis_end = crisis_date - pd.Timedelta(days=1)
    
    print(f"\nPre-crisis window: {pre_crisis_start} to {pre_crisis_end}")
    
    # Get pre-crisis data
    pre_crisis_mask = (ustc['Date'] >= pre_crisis_start) & (ustc['Date'] <= pre_crisis_end)
    pre_crisis_data = ustc[pre_crisis_mask]
    
    print(f"Pre-crisis data points: {len(pre_crisis_data)}")
    
    # Calculate baseline statistics
    baseline_mean = pre_crisis_data['peg_deviation'].mean()
    baseline_std = pre_crisis_data['peg_deviation'].std()
    threshold = baseline_mean + (3 * baseline_std)
    ustc["threshold"] = threshold
    
    print(f"\nBaseline mean: {baseline_mean:.6f}")
    print(f"Baseline std: {baseline_std:.6f}")
    print(f"Threshold (mean + 3*std): {threshold:.6f}")
    
    # Find first meaningful deviation
    post_crisis_mask = ustc['Date'] >= pre_crisis_end
    first_deviation_idx = ustc[post_crisis_mask & (ustc['peg_deviation'] > threshold)].index
    
    if len(first_deviation_idx) > 0:
        first_deviation_time = ustc.loc[first_deviation_idx[0], 'Date']
        first_deviation_value = ustc.loc[first_deviation_idx[0], 'peg_deviation']
        print(f"\nFirst meaningful deviation: {first_deviation_time}")
        print(f"Peg deviation: {first_deviation_value:.6f}")
    else:
        first_deviation_time = None
        print("\nNo significant deviation detected")
    # Find minimum price (peak crisis)
    min_price_idx = ustc['close'].idxmin()
    peak_crisis_time = ustc.loc[min_price_idx, 'Date']
    min_price = ustc.loc[min_price_idx, 'close']
    
    print(f"\nPeak crisis (min price): {peak_crisis_time}")
    print(f"Minimum price: ${min_price:.6f}")
    
    # Compare with other stablecoins
    print("\n=== Stablecoin Comparison ===")
    for name, coin in [('DAI', dai), ('PAX', pax), ('USDC', usdc), ('USDT', usdt)]:
        if coin['timestamp'].dtype != 'datetime64[ns]':
            coin['Date'] = pd.to_datetime(coin['timestamp'], unit='s')
        else:
            coin['Date'] = coin['timestamp']
        coin['peg_deviation'] = abs(coin['close'] - 1)
        coin['volatility'] = (coin['high'] - coin['low']) / coin['close']
        
        print(f"\n{name}:")
        print(f"  Avg peg deviation: {coin['peg_deviation'].mean():.6f}")
        print(f"  Max peg deviation: {coin['peg_deviation'].max():.6f}")
        print(f"  Avg volatility: {coin['volatility'].mean():.6f}")
    
    print(f"\nUSTC:")
    print(f"  Avg peg deviation: {ustc['peg_deviation'].mean():.6f}")
    print(f"  Max peg deviation: {ustc['peg_deviation'].max():.6f}")
    print(f"  Avg volatility: {ustc['volatility'].mean():.6f}")
    
    # Create graphs with vertical lines for crisis markers
    graphs = [
        {
            "Title": "USTC Peg Deviation",
            "Traces": [
                {
                    "Name": "Peg Deviation",
                    "x": "Date",
                    "y": "peg_deviation",
                    "Color": "red"
                },
                {
                    "Name": "Peg Deviation Threshold",
                    "x": "Date",
                    "y": "threshold",
                    "Color": "white"
                }
            ]
        },
        {
            "Title": "USTC Volatility",
            "Traces": [
                {
                    "Name": "Volatility",
                    "x": "Date",
                    "y": "volatility",
                    "Color": "orange"
                }
            ]
        }
    ]

    h_graphs = [
        {
            "y": first_deviation_value,
            "label":f"{threshold:.3g} (Pre-Crisis Threshold)"
        }
    ]

    vis = Visualiser(ustc)
    focused_df = vis.focus("2022-05-02", "2022-05-25")
    focused_vis = Visualiser(focused_df)
    focused_vis.plot_indicators(title="Terra USTC Crisis Analysis", graphs=graphs, h_graphs=h_graphs)