"""
Terra-Luna Crisis Analysis
"""

import pandas as pd
import numpy as np
import zipfile
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Import your visualization tools
from src.DatasetManager import DatasetManager
from src.Visualiser import Visualiser

if __name__ == "__main__":
    # ============================================================================
    # CONFIGURATION
    # ============================================================================

    # File paths
    ZIP_PATH = "datasets/ERC20-stablecoins.zip"
    CSV_FILE = "token_transfers_V3.0.0.csv"

    # USDT contract address (to filter if needed)
    USDT_CONTRACT = "0xa47c8bf37f92abed4a126bda807a7b7498661acd"

    # USDT has 6 decimal places
    USDT_DECIMALS = 1e6

    # Analysis period
    ANALYSIS_START = '2022-04-20'
    ANALYSIS_END = '2022-05-30'
    CRISIS_START = '2022-05-03'
    CRISIS_END = '2022-05-20'

    # Analysis parameters
    LARGE_TX_PERCENTILE = 95
    STRESS_VOLUME_PERCENTILE = 90
    # ============================================================================
    # LOAD DATA
    # ============================================================================

    print("Loading data from ZIP file...")
    print(f"ZIP: {ZIP_PATH}")
    print(f"CSV: {CSV_FILE}")

    # Load data using your method
    # NOTE: Remove 'nrows=5' for full analysis - that's just for testing!
    with zipfile.ZipFile(ZIP_PATH) as z:
        with z.open(CSV_FILE) as f:
            # For full analysis, remove nrows parameter:
            # token_df = pd.read_csv(f, encoding='latin-1')
            
            # For testing with sample:
            token_df = pd.read_csv(f, encoding='latin-1')  # Adjust as needed


    print(f"✓ Loaded {len(token_df):,} transactions")
    print(f"\nColumns: {list(token_df.columns)}")
    print(f"\nFirst few rows:")
    print(token_df.head())
    # Check data structure
    print(f"\nData types:")
    print(token_df.dtypes)
    # ============================================================================
    # DATA PREPROCESSING
    # ============================================================================

    print("\n" + "="*80)
    print("PREPROCESSING DATA")
    print("="*80)

    # 1. Convert value to number of coins 
    token_df['amount'] = token_df['value'] 
    print(f"✓ Converted value to USD (divided by {USDT_DECIMALS:,.0f})")

    # Sanity check
    print(f"  Sample values:")
    print(f"  - Raw value: {token_df['value'].iloc[0]:,.0f} → Tokens:{token_df['amount'].iloc[0]:,.6f}")
    print(f"  - Median raw: {token_df['value'].median():,.0f} → Tokens:{token_df['amount'].median():,.2f}")
    print(f"  - Max raw: {token_df['value'].max():,.0f} → Tokens:{token_df['amount'].max():,.2f}")

    # 2. Convert timestamp to datetime
    token_df['Date'] = pd.to_datetime(token_df['time_stamp'], unit='s')
    print(f"✓ Converted timestamps to datetime")
    print(f"  Date range: {token_df['Date'].min()} to {token_df['Date'].max()}")

    # 3. Create time-based features
    token_df['Hour'] = token_df['Date'].dt.floor('h')
    token_df['Day'] = token_df['Date'].dt.date
    token_df['DayOfWeek'] = token_df['Date'].dt.day_name()
    print(f"✓ Created time features (Hour, Day, DayOfWeek)")

    # 4. Sort by timestamp (CRITICAL for rolling calculations)
    token_df = token_df.sort_values('Date').reset_index(drop=True)
    print(f"✓ Sorted by date")

    # 5. Filter to analysis period
    mask = (token_df['Date'] >= ANALYSIS_START) & (token_df['Date'] <= ANALYSIS_END)
    token_df_filtered = token_df[mask].copy()
    print(f"✓ Filtered to analysis period: {ANALYSIS_START} to {ANALYSIS_END}")
    print(f"  Transactions in period: {len(token_df_filtered):,}")

    # Check if we have data in the crisis period
    crisis_mask = (token_df_filtered['Date'] >= CRISIS_START) & (token_df_filtered['Date'] <= CRISIS_END)
    crisis_txs = crisis_mask.sum()
    print(f"  Transactions during crisis ({CRISIS_START} to {CRISIS_END}): {crisis_txs:,}")

    if crisis_txs == 0:
        print("\n⚠️  WARNING: No transactions found in crisis period!")
        print("    This might mean:")
        print("    1. You're using nrows limit that's too small")
        print("    2. Dataset doesn't cover May 2022")
        print("    3. Need to filter by contract_address for USDT only")
        print("\n    Continuing with available data...\n")

    # Use filtered data for analysis
    token_df = token_df_filtered # Analysis Start - End Timeframe
    # ============================================================================
    # EXPLORATORY DATA ANALYSIS
    # ============================================================================

    print("\n" + "="*80)
    print("EXPLORATORY DATA ANALYSIS")
    print("="*80)

    # Basic statistics
    print(f"\nToken Transaction Amount Statistics:")
    print(token_df['amount'].describe())

    print(f"\nDate Distribution:")
    print(token_df['Date'].dt.date.value_counts().sort_index().head(5))

    print(f"\nUnique Participants:")
    print(f"  Unique senders: {token_df['from_address'].nunique():,}")
    print(f"  Unique receivers: {token_df['to_address'].nunique():,}")

    # Check for contract filtering
    if 'contract_address' in token_df.columns:
        print(f"\nContract Addresses in Data:")
        print(token_df['contract_address'].value_counts())
        
        # Filter to USDT only if multiple contracts present
        if token_df['contract_address'].nunique() > 1:
            print(f"\n⚠️  Multiple contracts detected! Filtering to USDT only...")
            token_df = token_df[token_df['contract_address'].str.lower() == USDT_CONTRACT.lower()].copy()
            print(f"  USDT transactions: {len(token_df):,}")
    # ============================================================================
    # CALCULATE ROLLING METRICS (24-HOUR WINDOWS)
    # ============================================================================

    print("\n" + "="*80)
    print("CALCULATING ROLLING METRICS (24H WINDOWS)")
    print("="*80)

    # Set Date as index for rolling operations
    df_indexed = token_df.set_index('Date').sort_index()
    df_indexed.index = pd.DatetimeIndex(df_indexed.index)
    print("Calculating volume metrics...")
    # 1. Total volume (24h rolling sum)
    df_indexed['Volume_24h'] = df_indexed['amount'].rolling(
        window='24h', min_periods=1
    ).sum()

    print("Calculating transaction count...")
    # 2. Transaction count (24h rolling count)
    df_indexed['TxCount_24h'] = df_indexed['amount'].rolling(
        window='24h', min_periods=1
    ).count()

    print("Calculating average transaction size...")
    # 3. Average transaction size (whale indicator)
    df_indexed['AvgTxSize_24h'] = df_indexed['amount'].rolling(
        window='24h', min_periods=1
    ).mean()

    # 4. Median transaction size (robust to outliers)
    df_indexed['MedianTxSize_24h'] = df_indexed['amount'].rolling(
        window='24h', min_periods=1
    ).median()

    print("Calculating volatility metrics...")
    # 5. Transaction volatility (market stress indicator)
    df_indexed['TxVolatility_24h'] = df_indexed['amount'].rolling(
        window='24h', min_periods=1
    ).std()

    print("Identifying large transactions...")
    # 6. Large transaction indicator
    large_tx_threshold = df_indexed['amount'].quantile(LARGE_TX_PERCENTILE / 100)
    df_indexed['is_large_tx'] = (df_indexed['amount'] >= large_tx_threshold).astype(int)
    df_indexed['LargeTxCount_24h'] = df_indexed['is_large_tx'].rolling(
        window='24h', min_periods=1
    ).sum()

    print(f"✓ Large transaction threshold (95th percentile): ${large_tx_threshold:,.2f}")
    print(f"✓ Number of large transactions: {df_indexed['is_large_tx'].sum():,}")

    # Reset index
    token_df = df_indexed.reset_index()

    print("✓ Rolling metrics calculated")
    # ============================================================================
    # CALCULATE HOURLY AGGREGATES
    # ============================================================================

    print("\n" + "="*80)
    print("CALCULATING HOURLY AGGREGATES")
    print("="*80)

    hourly = token_df.groupby('Hour').agg({
        'amount': ['sum', 'mean', 'median', 'std', 'count'],
        'from_address': 'nunique',
        'to_address': 'nunique',
        'is_large_tx': 'sum'
    }).reset_index()

    # Flatten multi-index columns
    hourly.columns = ['Hour', 'Total_Volume', 'Avg_Tx', 'Median_Tx', 'Tx_Std', 
                    'Tx_Count', 'Unique_Senders', 'Unique_Receivers', 'Large_Tx_Count']

    # Calculate derived metrics
    hourly['Volume_Per_Sender'] = hourly['Total_Volume'] / hourly['Unique_Senders']
    hourly['Tx_Per_Sender'] = hourly['Tx_Count'] / hourly['Unique_Senders']

    # Hour-over-hour changes
    hourly['Volume_Change_Pct'] = hourly['Total_Volume'].pct_change() * 100
    hourly['TxCount_Change_Pct'] = hourly['Tx_Count'].pct_change() * 100

    # Identify stress periods
    volume_threshold = hourly['Total_Volume'].quantile(STRESS_VOLUME_PERCENTILE / 100)
    count_threshold = hourly['Tx_Count'].quantile(STRESS_VOLUME_PERCENTILE / 100)
    hourly['is_stress_period'] = (
        (hourly['Total_Volume'] >= volume_threshold) & 
        (hourly['Tx_Count'] >= count_threshold)
    )

    stress_hours = hourly['is_stress_period'].sum()
    print(f"✓ Hourly aggregates calculated: {len(hourly)} hours")
    print(f"✓ Stress periods identified: {stress_hours} hours ({stress_hours/len(hourly)*100:.1f}%)")
    # recompute daily from current token_df in memory
    daily = token_df.groupby('Day').agg(
        Daily_Volume=('amount', 'sum'),
        Unique_Senders=('from_address', 'nunique'),
        Unique_Receivers=('to_address', 'nunique'),
        Tx_Count=('amount', 'count')
    ).reset_index()
    daily.columns = ['Day', 'Daily_Volume', 'Unique_Senders', 'Unique_Receivers','Tx_Count']

    # recompute HHI
    hhi_data = []
    for day in token_df['Day'].unique():
        day_txs = token_df[token_df['Day'] == day]
        sender_volumes = day_txs.groupby('from_address')['amount'].sum()
        total_volume = sender_volumes.sum()
        hhi = (sender_volumes / total_volume).pow(2).sum() if total_volume > 0 else float('nan')
        hhi_data.append({'Day': day, 'HHI_Senders': hhi})

    daily = daily.merge(pd.DataFrame(hhi_data), on='Day', how='left')
    daily['Day'] = pd.to_datetime(daily['Day'])

    # ============================================================================
    # EXPORT DATA FOR VISUALIZATION
    # ============================================================================

    print("\n" + "="*80)
    print("EXPORTING PROCESSED DATA")
    print("="*80)

    # Export to CSV for use in visualizations
    hourly.to_csv('hourly_metrics.csv', index=False)
    daily.to_csv('daily_metrics.csv', index=False)

    # Export key events
    key_events = pd.DataFrame([
        {'Date': pd.to_datetime(CRISIS_START), 'Event': 'UST Depeg Begins (May 7)'},
        {'Date': pd.to_datetime('2022-05-08'), 'Event': 'Confidence Collapses (May 8)'},
        {'Date': pd.to_datetime('2022-05-09'), 'Event': 'LUNA Death Spiral (May 9)'},
        {'Date': pd.to_datetime('2022-05-10'), 'Event': 'Near-Total Collapse (May 10)'},
        {'Date': pd.to_datetime(CRISIS_END), 'Event': 'Crisis Containment (May 12+)'}
    ])
    if 'first_spike' in locals():
        key_events = pd.concat([
            pd.DataFrame([{'Date': first_spike, 'Event': 'First Warning Signal'}]),
            key_events
        ]).sort_values('Date').reset_index(drop=True)

    key_events.to_csv('key_crisis_events.csv', index=False)

    print("✓ Exported: hourly_metrics.csv")
    print("✓ Exported: daily_metrics.csv")
    print("✓ Exported: key_crisis_events.csv")

    print("\n✅ ANALYSIS COMPLETE!")
    print("\nProcessed data is ready for visualization.")
    print("Load 'hourly_metrics.csv' into Visualiser class.")

    import importlib
    import src.Visualiser as V
    importlib.reload(V)
    from src.Visualiser import Visualiser

    # Load processed data
    daily_df = pd.read_csv('daily_metrics.csv')
    daily_df['Day'] = pd.to_datetime(daily_df['Day'])
    daily_df['Date'] = daily_df['Day']

    # PRE-CALCULATE transformed columns (don't use lambdas)
    daily_df['Total_Volume_M'] = daily_df['Daily_Volume'] / 100000000
    daily_df['Tx_Count_K'] = daily_df['Tx_Count'] /1000

    # Initialize visualiser
    vis = Visualiser(daily_df)
    vis.focus(CRISIS_START,CRISIS_END)

    # Use the pre-calculated columns directly (no lambdas)
    graphs = [
        {
            "Title": "Crisis Onset: Volume and Transaction Surge",
            "Traces": [
                {
                    "Name": "Total Volume of Tokens / 100M",
                    "x": "Date",
                    "y": "Total_Volume_M",  # Direct column name
                    "Color": "crimson"
                },
                {
                    "Name": "Transaction Count / Thousands",
                    "x": "Date",
                    "y": "Tx_Count_K",  # Direct column name
                    "Color": "steelblue"
                }            
            ]
        }
    ]

    vis.plot_indicators(
        title="Terra-Luna Crisis: Confidence Breakdown Analysis",
        graphs=graphs
    )