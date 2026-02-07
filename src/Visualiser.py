import plotly.graph_objects as go
from plotly.subplots import make_subplots

class Visualiser:
    """
    Compiles tools to visualise dataframes
    """

    def __init__(self, df):
        self.df = df

    def focus(self, start=None, end=None):
        """Focuses the dataframe on a specified period
        
        Args:
            df: Dataframe
            start: Start date for window
            end: End date for window
        """
        return self.df[
            (self.df["Date"] >= ("1970-01-01" if not start else start)) 
            & (self.df["Date"] <= ("2050-01-01" if not end else end))
        ].copy()
    
    def plot_indicators(self, title="No title", graphs=[]):
        """Generates plotlines for indicators
        
        Args:
            title: 
            indicators: 
        """
        # Create subplot based on number of graphs to plot
        fig = make_subplots(
            rows=len(graphs), cols=1, 
            shared_xaxes=True, 
            vertical_spacing=0.1,
            subplot_titles=[graph["Title"] for graph in graphs]
        )

        # For each graph
        for i, graph in enumerate(graphs):
            # Plot each trace
            for trace in graph["Traces"]:
                fig.add_trace(
                    go.Scatter(x=self.df[trace["x"]], y=self.df[trace["y"]], name=trace["Name"], line=dict(color=trace["Color"])),
                    row=i+1, col=1
                )

        # Update layout for a professional look
        fig.update_layout(
            title_text=title,
            height=800,
            xaxis_title="Date",
            hovermode="x unified", # Shows all values in one tooltip when hovering
            template="plotly_dark"  # Dark mode is standard for financial dashboards
        )

        # Save to HTML file instead of showing
        fig.write_html("indicators_plot.html")
        


