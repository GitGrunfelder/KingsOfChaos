import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from datetime import datetime, timedelta

# SPM data
spm_levels = list(range(1, 51))

spm_exp_costs = [
    0,
    150,
    275,
    300,
    325,
    350,
    375,
    400,
    450,
    500,
    650,
    700,
    750,
    800,
    850,
    900,
    950,
    1000,
    1050,
    1200,
    1250,
    1300,
    1350,
    1400,
    1500,
    1700,
    1800,
    1900,
    2000,
    2100,
    2300,
    2400,
    2500,
    2600,
    2700,
    2800,
    2900,
    3000,
    3100,
    3400,
    3600,
    3700,
    3800,
    3900,
    4000,
    4100,
    4200,
    4300,
    4400,
    4500,
]


# Economy data
econ_levels = [
    0,
    200,
    500,
    1300,
    3100,
    7800,
    19500,
    48800,
    122100,
    305200,
    762900,
    1907300,
    4768400,
]

econ_exp_costs = [
    0,
    75,
    150,
    300,
    600,
    1200,
    2400,
    4800,
    9600,
    19200,
    38400,
    76800,
    153600,
]
xp_per_minute_costs = [0, 200000000, 550000000, 800000000, 1000000000, 2000000000]


# Starting Upgrade Path Section (Race to 6XP/Min)
def time_to_next_upgrade(current_xp, xp_rate, upgrade_cost):
    """Calculate the time required to afford the next upgrade in XP."""
    return (upgrade_cost - current_xp) / xp_rate


def time_to_xp_upgrade(current_gold, gold_rate, upgrade_cost):
    """Calculate the time required to reach the next XP/minute upgrade in gold."""
    return (upgrade_cost - current_gold) / gold_rate


def perform_upgrade(
    current_level, upgrade_costs, current_xp, current_gold, xp_rate, gold_rate
):
    """Helper function to perform an upgrade if possible."""
    if (
        current_level - 1 < len(upgrade_costs)
        and current_xp >= upgrade_costs[current_level - 1]
    ):
        time_to_upgrade = (upgrade_costs[current_level - 1] - current_xp) / xp_rate
        current_gold += gold_rate * time_to_upgrade
        current_xp = 0
        current_level += 1
    return current_level, current_xp, current_gold


def optimal_upgrade_path():
    # Starting conditions
    current_spm = 1
    current_econ = 0
    current_gold = 50000
    current_xp = 0
    current_xp_rate = 1
    gold_rate = current_spm * 2.6 + current_econ

    steps = []

    while current_xp_rate < 6:
        gold_rate = current_spm * 2.6 + current_econ  # Update gold rate

        # Store the current state to check if any upgrades were made
        prev_spm, prev_econ, prev_gold = current_spm, current_econ, current_gold

        # Use the helper function to check and perform SPM upgrade
        current_spm, current_xp, current_gold = perform_upgrade(
            current_spm,
            spm_exp_costs,
            current_xp,
            current_gold,
            current_xp_rate,
            gold_rate,
        )

        # Use the helper function to check and perform Economy upgrade
        current_econ, current_xp, current_gold = perform_upgrade(
            current_econ,
            econ_exp_costs,
            current_xp,
            current_gold,
            current_xp_rate,
            gold_rate,
        )

        # Check if we can afford the next XP/minute upgrade in gold
        if current_gold >= xp_per_minute_costs[current_xp_rate]:
            steps.append(
                f"Get XP/minute upgrade {current_xp_rate + 1} (Cost: {xp_per_minute_costs[current_xp_rate + 1]} Gold)"
            )
            current_xp_rate += 1
            current_gold -= xp_per_minute_costs[current_xp_rate]

        # If no upgrades were made, break out of the loop
        if (
            prev_spm == current_spm
            and prev_econ == current_econ
            and prev_gold == current_gold
        ):
            break

    return steps


app = dash.Dash(__name__)

app.layout = html.Div(
    [
        # Input Fields Section
        html.Div(
            [
                # SPM and Economy Inputs in two columns
                html.Div(
                    [
                        # Current SPM
                        html.Div(
                            [
                                html.Label("Current SPM:"),
                                dcc.Input(
                                    id="current-spm-input",
                                    type="number",
                                    value=1,
                                    min=1,
                                    max=50,
                                ),
                            ],
                            style={"width": "100%", "padding": "10px"},
                        ),
                        # Goal SPM
                        html.Div(
                            [
                                html.Label("Goal SPM:"),
                                dcc.Input(
                                    id="goal-spm-input",
                                    type="number",
                                    value=50,
                                    min=1,
                                    max=50,
                                ),
                            ],
                            style={"width": "100%", "padding": "10px"},
                        ),
                    ],
                    style={"width": "50%", "display": "inline-block"},
                ),
                html.Div(
                    [
                        # Current Economy
                        html.Div(
                            [
                                html.Label("Current Economy:"),
                                dcc.Dropdown(
                                    id="current-economy-dropdown",
                                    options=[
                                        {"label": str(val), "value": val}
                                        for val in econ_levels
                                    ],
                                    value=0,
                                ),
                            ],
                            style={"width": "100%", "padding": "10px"},
                        ),
                        # Goal Economy
                        html.Div(
                            [
                                html.Label("Goal Economy:"),
                                dcc.Dropdown(
                                    id="goal-economy-dropdown",
                                    options=[
                                        {"label": str(val), "value": val}
                                        for val in econ_levels
                                    ],
                                    value=4768400,
                                ),
                            ],
                            style={"width": "100%", "padding": "10px"},
                        ),
                    ],
                    style={"width": "50%", "display": "inline-block"},
                ),
                # Other input fields
                html.Div(
                    [
                        html.Label("Current Income:"),
                        dcc.Input(id="income-input", type="number", value=100),
                        html.Label("Current XP/minute:"),
                        dcc.Input(
                            id="xp-per-minute-input",
                            type="number",
                            value=1,
                            min=1,
                            max=6,
                        ),
                        html.Label("End Condition:"),
                        dcc.Dropdown(
                            id="end-condition-dropdown",
                            options=[
                                {"label": "End Date", "value": "end_date"},
                                {"label": "Target Gold", "value": "target_gold"},
                            ],
                            value="end_date",
                        ),
                        html.Div(
                            [
                                dcc.DatePickerSingle(
                                    id="end-date-picker",
                                    date=(datetime.today() + timedelta(days=30)).date(),
                                )
                            ],
                            id="end-date-container",
                            style={"display": "none"},
                        ),
                        html.Div(
                            [
                                dcc.Input(
                                    id="target-gold-input",
                                    type="number",
                                    value=2000000000,
                                )
                            ],
                            id="target-gold-container",
                            style={"display": "none"},
                        ),
                    ]
                ),
            ],
            style={
                "backgroundColor": "#f5f5f5",
                "padding": "20px",
                "borderRadius": "5px",
            },
        ),
        # SPM Graph
        dcc.Graph(id="spm-gold-graph", style={"margin-bottom": "20px"}),
        # Economy Graph
        dcc.Graph(id="econ-gold-graph"),
        # Results Section
        html.Div(
            [
                html.Div(id="spm-result", className="result-panel"),
                html.Div(id="econ-result", className="result-panel"),
                html.Div(id="comparison-result", className="result-panel"),
                # New section for steps
                html.Div(
                    [
                        html.H3("Early Game"),
                        html.Div(id="steps-result", className="result-panel"),
                    ],
                    className="results-section",
                    style={
                        "backgroundColor": "#f5f5f5",
                        "padding": "20px",
                        "borderRadius": "5px",
                        "marginTop": "20px",
                    },
                ),
            ]
        ),
    ]
)


@app.callback(
    [Output("end-date-container", "style"), Output("target-gold-container", "style")],
    [Input("end-condition-dropdown", "value")],
)
def toggle_end_condition_input(selected_value):
    if selected_value == "end_date":
        return {"display": "block"}, {"display": "none"}
    else:
        return {"display": "none"}, {"display": "block"}


@app.callback(
    [
        Output("spm-gold-graph", "figure"),
        Output("econ-gold-graph", "figure"),
        Output("spm-result", "children"),
        Output("econ-result", "children"),
        Output("comparison-result", "children"),
        Output("steps-result", "children"),
    ],
    [
        Input("income-input", "value"),
        Input("xp-per-minute-input", "value"),
        Input("current-spm-input", "value"),
        Input("goal-spm-input", "value"),
        Input("current-economy-dropdown", "value"),
        Input("goal-economy-dropdown", "value"),
        Input("end-date-picker", "date"),
        Input("target-gold-input", "value"),
        Input("end-condition-dropdown", "value"),
    ],
)
def update_graph(
    income,
    xp_per_minute,
    current_spm,
    goal_spm,
    current_economy,
    goal_economy,
    end_date,
    target_gold,
    end_condition,
):
    if end_condition == "end_date":
        end_date = datetime.strptime(end_date.split(" ")[0], "%Y-%m-%d")
        total_days = (end_date - datetime.today()).days
        total_minutes = total_days * 24 * 60
    else:  # If end condition is target gold
        total_minutes = 0
        temp_gold = 0
        while temp_gold < target_gold:
            total_minutes += 1
            temp_gold += income + (current_spm * 2.6 * total_minutes)

    minutes = list(range(1, total_minutes + 1))
    dates = [datetime.today() + timedelta(minutes=m) for m in minutes]

    # SPM Graph
    gold_earned_spm = []
    upgrade_points_x = []
    upgrade_points_y = []
    upgrade_points_text = []  # List to store hover text for upgrade points
    total_gold_spm = 0
    total_soldiers = 0
    current_xp = 0
    for m in minutes:
        total_soldiers += current_spm
        gold_this_minute = income + (total_soldiers * 2.6)
        total_gold_spm += gold_this_minute
        current_xp += xp_per_minute
        if (
            current_spm - 1 < len(spm_exp_costs)
            and current_xp >= spm_exp_costs[current_spm - 1]
            and current_spm < goal_spm
        ):
            upgrade_points_x.append(dates[m - 1])
            upgrade_points_y.append(total_gold_spm)
            upgrade_points_text.append(
                f"Upgrade to {current_spm + 1} SPM"
            )  # Add hover text for the upgrade point
            current_spm += 1
            current_xp = 0
        gold_earned_spm.append(total_gold_spm)

    # Economy Graph calculations
    gold_earned_econ = []
    econ_upgrade_points_x = []  # List to store x-values for upgrade points
    econ_upgrade_points_y = []  # List to store y-values for upgrade points
    econ_upgrade_points_text = []  # List to store hover text for upgrade points
    total_gold_econ = 0
    current_xp_econ = 0  # XP accumulated for economy upgrades
    current_economy_level = econ_levels.index(
        current_economy
    )  # Get the index of the user's current economy level
    goal_economy_index = econ_levels.index(
        goal_economy
    )  # Get the index of the user's goal economy level
    total_xp_spent_on_econ = 0  # Initialize the total XP spent on Economy upgrades

    for m in minutes:
        gold_this_minute_econ = income + current_economy
        total_gold_econ += gold_this_minute_econ
        current_xp_econ += xp_per_minute

        # Check if we can buy the next economy upgrade and if we haven't reached the goal economy level
        if (
            current_economy_level < goal_economy_index
            and current_xp_econ >= econ_exp_costs[current_economy_level]
        ):
            # Add the upgrade point to the lists
            econ_upgrade_points_x.append(dates[m - 1])
            econ_upgrade_points_y.append(total_gold_econ)
            new_econ_rate = econ_levels[
                current_economy_level + 1
            ]  # Get the new Economy rate from the econ_levels list
            total_xp_spent_on_econ += econ_exp_costs[
                current_economy_level
            ]  # Update the total XP spent on Economy upgrades
            accumulated_xp = sum(
                econ_exp_costs[: current_economy_level + 1]
            )  # Calculate the accumulated XP up to the current upgrade
            econ_upgrade_points_text.append(
                f"Buy Upgrade #{current_economy_level + 1}: New Econ Rate: {new_econ_rate}, XP Cost: {econ_exp_costs[current_economy_level]}, Total Accumulated XP: {accumulated_xp}"
            )

            # Update the current economy rate and increase the economy level
            current_economy = new_econ_rate
            current_economy_level += 1
            current_xp_econ = 0

        gold_earned_econ.append(total_gold_econ)

    # Calculate gold accumulation for user's current stats
    gold_earned_user = []
    total_gold_user = 0
    total_soldiers_user = 0
    for m in minutes:
        total_soldiers_user += current_spm
        gold_this_minute_user = income + (total_soldiers_user * 2.6)
        total_gold_user += gold_this_minute_user
        gold_earned_user.append(total_gold_user)

    # Calculate gold accumulation for combined stats (current econ + current income + current spm)
    gold_earned_combined = []
    total_gold_combined = 0
    total_soldiers_combined = 0
    for m in minutes:
        total_soldiers_combined += current_spm
        gold_this_minute_combined = (
            income + current_economy + (total_soldiers_combined * 2.6)
        )
        total_gold_combined += gold_this_minute_combined
        gold_earned_combined.append(total_gold_combined)

    # XP accumulation calculations
    xp_earned = []
    total_xp = 0
    for m in minutes:
        total_xp += xp_per_minute
        xp_earned.append(total_xp)

    trace_spm = go.Scatter(
        x=dates,
        y=gold_earned_spm,
        mode="lines",
        name="SPM Gold Earnings",
        line=dict(color="blue"),
    )

    trace_upgrade_points = go.Scatter(
        x=upgrade_points_x,
        y=upgrade_points_y,
        mode="markers",
        name="SPM Upgrades",
        marker=dict(size=10, color="black", symbol="square"),
        text=upgrade_points_text,  # Set the hover text
        hoverinfo="text+y",  # Display the custom hover text along with the y-value
    )

    layout_spm = go.Layout(
        title="SPM Gold Earnings Over Time",
        xaxis=dict(title="Date"),
        yaxis=dict(title="Accumulated Gold"),
    )

    # Economy Graph
    trace_econ = go.Scatter(
        x=dates,
        y=gold_earned_econ,
        mode="lines",
        name="Economy Gold Earnings",
        line=dict(color="red"),
    )

    trace_econ_upgrade_points = go.Scatter(
        x=econ_upgrade_points_x,
        y=econ_upgrade_points_y,
        mode="markers",
        name="Economy Upgrades",
        marker=dict(size=10, color="green", symbol="square"),
        text=econ_upgrade_points_text,  # Set the hover text
        hoverinfo="text+y",  # Display the custom hover text along with the y-value
    )

    layout_econ = go.Layout(
        title="Economy Gold Earnings Over Time",
        xaxis=dict(title="Date"),
        yaxis=dict(title="Accumulated Gold"),
    )

    total_accumulated_gold_spm = gold_earned_spm[-1]
    total_accumulated_gold_econ = gold_earned_econ[-1]
    spm_result_text = f"SPM Total Accumulated Gold: {total_accumulated_gold_spm:,.2f}"
    econ_result_text = (
        f"Economy Total Accumulated Gold: {total_accumulated_gold_econ:,.2f}"
    )

    if total_accumulated_gold_spm > total_accumulated_gold_econ:
        comparison_result_text = f"SPM results in higher income by {total_accumulated_gold_spm - total_accumulated_gold_econ:,.2f} gold."
    elif total_accumulated_gold_spm < total_accumulated_gold_econ:
        comparison_result_text = f"Economy results in higher income by {total_accumulated_gold_econ - total_accumulated_gold_spm:,.2f} gold."
    else:
        comparison_result_text = "Both SPM and Economy result in the same income."

    steps = optimal_upgrade_path()

    # Convert steps list to HTML format
    steps_html = [html.P(step) for step in steps]

    return (
        {"data": [trace_spm, trace_upgrade_points], "layout": layout_spm},
        {"data": [trace_econ, trace_econ_upgrade_points], "layout": layout_econ},
        spm_result_text,
        econ_result_text,
        comparison_result_text,
        steps_html,
    )


if __name__ == "__main__":
    app.run_server(debug=True)
