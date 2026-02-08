import plotly.graph_objects as go
from plotly.subplots import make_subplots

class Visualiser:
    """
    Compiles tools to visualise dataframes
    """

    def __init__(self, original_df):
        self.original_df = original_df
        self.df = original_df


    def focus(self, start=None, end=None):
        """Focuses the dataframe on a specified period
        
        Args:
            df: Dataframe
            start: Start date for window
            end: End date for window

        Returns: pd.Dataframe of focused data
        """
        self.df = self.original_df[
            (self.df["Date"] >= ("1970-01-01" if not start else start)) 
            & (self.df["Date"] <= ("2050-01-01" if not end else end))
        ].copy()
        return self.df
    

    def plot_indicators(self, title="No title", graphs=[], h_lines=[], v_lines=[], graph_height=450, vert_spacing=0.05):
        """Generates plotlines for indicators
        
        Args:
            title (str): Title for all plots 
            graphs (list[dict]): List of graphs to plot
            h_lines (list[dict]): List of horizontal lines to plot on all graphs
            v_lines (list[dict]): List of vertical lines to plot on all graphs

        Returns: None
        """
        # Create subplot based on number of graphs to plot
        fig = make_subplots(
            rows=len(graphs), cols=1, 
            shared_xaxes=False, 
            vertical_spacing=vert_spacing,
            subplot_titles=[graph["Title"] for graph in graphs]
        )

        # Plot each trace for each graph
        for i, graph in enumerate(graphs):
            row_idx = i + 1
            for trace in graph["Traces"]:
                fig.add_trace(
                    go.Scatter(
                        x=self.df[trace["x"]],
                        y=self.df[trace["y"]],
                        name=trace["Name"],
                        line=dict(color=trace["Color"]),
                        legendgroup=f"group{row_idx}",
                        legendgrouptitle_text=f"{graph["Title"]} Legend" if trace == graph["Traces"][0] else None,
                        connectgaps=True
                    ),
                    row=row_idx, col=1
                )
            fig.update_xaxes(title_text="Date", row=row_idx, col=1)

        # Plot each horizontal lines across all graphs
        for h_line in h_lines:
            fig.add_hline(
                y=h_line["y"],
                line_width=2,
                line_color=h_line.get("color", "white"),
                opacity=1.0,
                annotation_text=h_line.get("label", ""),
                annotation_position="right",
                row="all",
                col=1
            )

        # Plot each vertical lines across all graphs
        for v_line in v_lines:
            fig.add_vline(
                x=v_line["x"], 
                line_width=2, 
                line_color=v_line.get("color", "white"),
                opacity=1.0,
                annotation_text=v_line.get("Label", ""),
                annotation_position="top",
                row="all",
                col=1
            )

        # Update layout design
        fig.update_layout(
            title_text=title,
            height=max(1080, graph_height * len(graphs) + vert_spacing * graph_height * (len(graphs) - 1)),
            hovermode="x unified",
            template="plotly_dark",
            legend=dict(
                groupclick="toggleitem",
                tracegroupgap=0.74*graph_height  # Space between legend groups (cannot be dynamic)
            )
        )

        fig.show()
    