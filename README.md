# Databusters - Eumasek

### This is a quantitative framework built to analyse systemic financial financial failures.

## Project Structure

```Plaintext
├───archives/               # Contains old code for reference
├───datasets/               # Contains ERC20 and GFC datasets
├───src                     # Contains main python scripts used for running data analysis
│   ├───DatasetManager.py
│   └───Visualiser.py
├───plot_erc20_price_data.py    # Plots price data from erc20 purely
├───plot_erc20.py               # Plots Terra USTC Crisis Analysis
├───plot_gfc.py                 # Plots Global Financial Crisis (01/01/2008 - 31/10/2008)
├───plot_token_transfer.py      # Plots Terra-Luna Crisis: Confidence Breakdown Analysis
├───README.md
└───requirements.txt
```

## Code Engine

### How does the code work?

1. **DatasetManager**: Handles all functionality related to data and manipulation

- Handles multi-level ZIP archives (eg, opening files inside nested zips)

- Data cleaning between Yahoo Finance (OHLCV), FRED (Macroeconomic) data formats, and various price data

- Automatically fixes timezone mismatches (stripping UTC) and "dirty" data like FRED’s placeholder periods, '.'

2. **Visualiser**: Plots an interactive graph 

- Interactive UI using Plotly; hover over any data point to see unified stats across all indicators

- Dynamic crisis markers: Automatically renders vertical lines for historical events (e.g. Lehman Brothers' Collapse)

### To run code:

1. **Install dependencies**

    Set up your environment and install the required processing libraries:
    ```cmd
    python -m venv venv
    venv\scripts\activate
    pip install -r requirements.txt
    ```

2. **Download datasets**

    Download the zip archives provided and put them in the datasets folder. We should have 2 datasets;
    ```
    /datasets/ERC20-stablecoins.zip
    /datasets/gfc.zip
    ```

3. **Run code**

    Execute the main logic to process the datasets and calculate indicators (e.g. VIX Volatility, TED Spread):
    ```cmd
    python plot_gfc.py
    python plot_erc20.py
    python plot_erc20_price_data.py
    python plot_token_transfers.py
    ```

4. **View graph in browser**

    Once the script finishes, an interactive dashboard will automatically open in your default web browser. You can zoom, pan, and export the charts directly from the interface.