#!/usr/bin/env python3
"""
Interactive Seinfeld Character Dialogue Explorer
Visualize character dialogue patterns across seasons and topics using Bokeh
"""

import pandas as pd
from bokeh.plotting import figure, output_file, save
from bokeh.layouts import column
from bokeh.models import (
    ColumnDataSource,
    HoverTool,
    Tabs,
    TabPanel,
    Div,
    Button,
    CustomJS,
)
from bokeh.palettes import Category10_8
from bokeh.io.export import export_png

from comp370.constants import DIR_DATA


def load_data(filepath):
    """Load the CSV data"""
    df = pd.read_csv(filepath)
    return df


def create_download_buttons():
    button_a = Button(label="Download comp370.db", button_type="default", width=200)
    button_a.js_on_click(
        CustomJS(
            code="""
        const link = document.createElement('a');
        link.href = '/download/db';
        link.click();
    """
        )
    )

    button_b = Button(
        label="Download comp370.tf-idf.csv", button_type="default", width=200
    )
    button_b.js_on_click(
        CustomJS(
            code="""
        const link = document.createElement('a');
        link.href = '/download/tf-idf';
        link.click();
    """
        )
    )

    button_c = Button(
        label="Download comp370.topics.csv", button_type="default", width=200
    )
    button_c.js_on_click(
        CustomJS(
            code="""
        const link = document.createElement('a');
        link.href = '/download/topics';
        link.click();
    """
        )
    )

    button_d = Button(
        label="Download comp370.annotations.csv", button_type="default", width=200
    )
    button_d.js_on_click(
        CustomJS(
            code="""
        const link = document.createElement('a');
        link.href = '/download/annotations';
        link.click();
    """
        )
    )

    return column(button_a, button_b, button_c, button_d, sizing_mode="fixed")


def create_stacked_bar_chart(df, title="Character Dialogue by Topic"):
    """Create stacked bar chart for overall topic distribution"""
    overall_data = df[df["scope"] == "overall"].copy()

    characters = list(overall_data["character"].unique())
    topics = list(overall_data["topic"].unique())

    # Prepare data for stacking
    data = {"characters": characters}
    colors = Category10_8[: len(topics)]

    for topic in topics:
        data[topic] = []
        for char in characters:
            mask = (overall_data["character"] == char) & (
                overall_data["topic"] == topic
            )
            ratio = overall_data[mask]["ratio"].values
            data[topic].append(ratio[0] if len(ratio) > 0 else 0)

    width = 900
    height = int(width * 3 / 4)
    p = figure(
        x_range=characters,  # type: ignore
        width=width,
        height=height,
        title=title,
        toolbar_location="above",
        tools="pan,wheel_zoom,box_zoom,reset,save",
        background_fill_color="white",
        border_fill_color="white",
    )

    # Create stacked bars using vbar_stack
    source = ColumnDataSource(data=data)

    p.vbar_stack(
        topics,
        x="characters",
        width=0.8,
        color=colors,
        legend_label=topics,
        source=source,
    )

    p.y_range.start = 0  # type: ignore
    p.x_range.range_padding = 0.1  # type: ignore
    p.xaxis.major_label_orientation = 45
    p.xgrid.grid_line_color = None
    p.legend.location = "top_right"
    p.legend.click_policy = "hide"
    p.yaxis.axis_label = "Proportion of Lines"

    hover = HoverTool(
        tooltips=[
            ("Character", "@characters"),
            ("Topic", "$name"),
            ("Value", "@$name{0.0%}"),
        ]
    )
    p.add_tools(hover)

    return p


def create_season_line_chart(df, character_name):
    """Create line chart showing topic evolution across seasons for a character"""
    char_data = df[
        (df["character"] == character_name) & (df["scope"] == "season")
    ].copy()

    if char_data.empty:
        return None

    width = 900
    height = int(width * 3 / 4)
    p = figure(
        width=width,
        height=height,
        title=f"{character_name}: Topic Distribution Across Seasons",
        toolbar_location="above",
        tools="pan,wheel_zoom,box_zoom,reset,save",
        background_fill_color="white",
        border_fill_color="white",
    )

    topics = char_data["topic"].unique()
    colors = Category10_8[: len(topics)]

    for i, topic in enumerate(topics):
        topic_data = char_data[char_data["topic"] == topic].sort_values("season")

        source = ColumnDataSource(
            data=dict(
                season=topic_data["season"].astype(str),
                ratio=topic_data["ratio"],
                lines=topic_data["topic_lines"],
                total=topic_data["total_lines"],
            )
        )

        p.line(
            "season",
            "ratio",
            source=source,
            legend_label=topic,
            color=colors[i],
            line_width=2,
        )
        p.scatter("season", "ratio", source=source, color=colors[i], size=8)

    p.legend.location = "top_right"
    p.legend.click_policy = "hide"
    p.xaxis.axis_label = "Season"
    p.yaxis.axis_label = "Proportion of Lines"

    hover = HoverTool(
        tooltips=[
            ("Season", "@season"),
            ("Ratio", "@ratio{0.0%}"),
            ("Topic Lines", "@lines"),
            ("Total Lines", "@total"),
        ]
    )
    p.add_tools(hover)

    return p


def create_topic_comparison(df):
    """Create grouped bar chart comparing characters on a specific topic"""
    overall_data = df[df["scope"] == "overall"].copy()

    # Get all unique topics and characters
    topics = sorted(overall_data["topic"].unique())
    characters = sorted(overall_data["character"].unique())

    # Start with first topic
    topic = topics[0]
    topic_data = overall_data[overall_data["topic"] == topic]

    source = ColumnDataSource(
        data=dict(
            characters=topic_data["character"].tolist(),
            ratios=topic_data["ratio"].tolist(),
            lines=topic_data["topic_lines"].tolist(),
            total=topic_data["total_lines"].tolist(),
        )
    )

    width = 900
    height = int(width * 3 / 4)
    p = figure(
        x_range=characters,  # type:  ignore
        width=width,
        height=height,
        title=f"Character Comparison: {topic}",
        toolbar_location="above",
        tools="pan,wheel_zoom,box_zoom,reset,save",
        background_fill_color="white",
        border_fill_color="white",
    )

    p.vbar(
        x="characters", top="ratios", width=0.7, source=source, color="navy", alpha=0.8
    )

    p.xaxis.major_label_orientation = 45
    p.yaxis.axis_label = "Proportion of Lines"

    hover = HoverTool(
        tooltips=[
            ("Character", "@characters"),
            ("Ratio", "@ratios{0.0%}"),
            ("Topic Lines", "@lines"),
            ("Total Lines", "@total"),
        ]
    )
    p.add_tools(hover)

    return p


def create_character_heatmap(df):
    """Create a heatmap showing all characters and topics"""
    overall_data = df[df["scope"] == "overall"].copy()

    # Pivot the data
    pivot_data = overall_data.pivot(index="character", columns="topic", values="ratio")

    characters = list(pivot_data.index)
    topics = list(pivot_data.columns)

    # Prepare data for heatmap
    char_list = []
    topic_list = []
    ratio_list = []

    for char in characters:
        for topic in topics:
            char_list.append(char)
            topic_list.append(topic)
            ratio_list.append(pivot_data.loc[char, topic])

    source = ColumnDataSource(
        data=dict(character=char_list, topic=topic_list, ratio=ratio_list)
    )

    from bokeh.models import LinearColorMapper
    from bokeh.palettes import RdYlBu11

    mapper = LinearColorMapper(
        palette=RdYlBu11[::-1], low=min(ratio_list), high=max(ratio_list)
    )

    width = 900
    height = int(width * 3 / 4)
    p = figure(
        x_range=topics,  # type:  ignore
        y_range=characters,  # type:  ignore
        width=width,
        height=height,
        title="Character-Topic Heatmap (Overall)",
        toolbar_location="above",
        tools="pan,wheel_zoom,box_zoom,reset,save,hover",
        background_fill_color="white",
        border_fill_color="white",
    )

    p.rect(
        x="topic",
        y="character",
        width=1,
        height=1,
        source=source,
        fill_color={"field": "ratio", "transform": mapper},
        line_color=None,
    )

    p.xaxis.major_label_orientation = 45

    hover = HoverTool(
        tooltips=[
            ("Character", "@character"),
            ("Topic", "@topic"),
            ("Ratio", "@ratio{0.0%}"),
        ]
    )
    p.tools = [hover, p.tools[0], p.tools[1], p.tools[2], p.tools[3], p.tools[4]]

    return p


def create_dashboard(df):
    """Create the main interactive dashboard"""

    # Title
    title_div = Div(
        text="""
    <h1 style="color: #333; margin-bottom: 0px;">Seinfeld Side Characters</h1>
    <p style="font-size: 14px; color: #666;">
        Explore dialogue patterns across characters, seasons, and topics
    </p>
    """,
        width=900,
    )

    # Create download buttons
    download_buttons = create_download_buttons()

    # Create visualizations
    stacked_bars = create_stacked_bar_chart(df)
    heatmap = create_character_heatmap(df)

    # Create season evolution charts for each character
    characters = df["character"].unique()
    season_charts = []

    for char in characters:
        chart = create_season_line_chart(df, char)
        if chart:
            tab = TabPanel(child=chart, title=char)  # type: ignore
            season_charts.append(tab)

    season_tabs = Tabs(tabs=season_charts)

    button_gql = Button(label="GraphQL Playground", button_type="primary", width=200)
    button_gql.js_on_click(
        CustomJS(
            code="""
        const link = document.createElement('a');
        link.href = '/gql';
        link.click();
    """
        )
    )

    # Layout
    dashboard_layout = column(
        button_gql,
        title_div,
        Div(text="<h3>Character Dialogue By Topic</h3>", width=900),
        stacked_bars,
        Div(text="<h3>Character-Topic Heatmap</h3>", width=900),
        heatmap,
        Div(text="<h3>Season Evolution by Character</h3>", width=900),
        season_tabs,
        Div(text="<h3>Downloads</h3>", width=900),
        download_buttons,
        sizing_mode="scale_width",
    )

    return dashboard_layout


def main():
    # Load data
    df = load_data(DIR_DATA / "statistics" / "statistics.topics.csv")

    print(f"Loaded {len(df)} records")
    print(f"Characters: {', '.join(df['character'].unique())}")
    print(f"Topics: {', '.join(df['topic'].unique())}")
    print(f"Seasons: {sorted(df[df['scope'] == 'season']['season'].unique())}")

    # Create dashboard
    dashboard = create_dashboard(df)

    # Output to HTML file
    output_file(DIR_DATA / "statistics" / "statistics.topics.html")
    save(dashboard)


if __name__ == "__main__":
    main()
