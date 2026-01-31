# Databusters

### How does the code work?

1. **DatasetManager**

- Handles multi-level ZIP archives (eg, opening files inside nested zips)

- Data cleaning between Yahoo Finance (OHLCV) and FRED (Macroeconomic) data formats

- Automatically fixes timezone mismatches (stripping UTC) and "dirty" data like FRED’s placeholder periods, '.'

2. **Visualiser**

- Interactive UI using Plotly; hover over any data point to see unified stats across all indicators

### To run code:

1. **Install dependencies**

    Set up your environment and install the required processing libraries (Pandas, Plotly):
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

    Execute the main logic to process the datasets and calculate indicators (VIX Volatility, TED Spread, etc.):
    ```cmd
    python main.py
    ```

4. **View graph in browser**

    Once the script finishes, an interactive dashboard will automatically open in your default web browser. You can zoom, pan, and export the charts directly from the interface.