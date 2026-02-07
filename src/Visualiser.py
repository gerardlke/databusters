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
    
    def plot_indicators(self, title="No title", graphs=[], v_graphs=[]):
        """Generates plotlines for indicators
        
        Args:
            title: 
            indicators: 
        """
        # Create subplot based on number of graphs to plot
        fig = make_subplots(
            rows=len(graphs), cols=1, 
            shared_xaxes=False, 
            vertical_spacing=0.05,
            subplot_titles=[graph["Title"] for graph in graphs]
        )

        # For each graph
        for i, graph in enumerate(graphs):
            # Plot each trace
            row_idx = i + 1
            for trace in graph["Traces"]:
                fig.add_trace(
                    go.Scatter(
                        x=self.df[trace["x"]],
                        y=self.df[trace["y"]],
                        name=trace["Name"],
                        line=dict(color=trace["Color"]),
                        legendgroup=f"group{row_idx}",
                        legendgrouptitle_text=f"({row_idx}) {graph["Title"]} Legend" if trace == graph["Traces"][0] else None,
                        connectgaps=True
                    ),
                    row=row_idx, col=1
                )
            # Label each individual X-axis
            fig.update_xaxes(title_text="Date", row=row_idx, col=1)

        for v_line in v_graphs:
            fig.add_hline(
                y=v_line["Price"], 
                line_width=2, 
                line_color="white",
                opacity=1.0,
                annotation_text=v_line["Event"],
                annotation_position="top",
                row="all", # Set to "all" to span all subplots, or a specific row_idx
                col=1
            )

        # Update layout for a professional look
        fig.update_layout(
            title_text=title,
            height=450*len(graphs),
            hovermode="x unified", # Shows all values in one tooltip when hovering
            template="plotly_dark",  # Dark mode is standard for financial dashboards
            legend=dict(
                groupclick="toggleitem",
                tracegroupgap=330  # Increases vertical gap between legend groups
            )
        )

        fig.show()