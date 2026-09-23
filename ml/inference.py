from pathlib import Path
import joblib
import numpy as np
import pandas as pd


# ============================================================
# MODEL DIRECTORY
# ============================================================

MODEL_DIR = Path(__file__).resolve().parent / "models"


# ============================================================
# LOAD SAVED ARTIFACTS
# ============================================================

eta_model = joblib.load(
    MODEL_DIR / "eta_linear_regression_v1.joblib"
)

eta_uncertainty = joblib.load(
    MODEL_DIR / "eta_uncertainty_v1.joblib"
)

anomaly_model = joblib.load(
    MODEL_DIR / "anomaly_isolation_forest_v1.joblib"
)

operator_baselines = joblib.load(
    MODEL_DIR / "operator_baseline_mad_v1.joblib"
)

anomaly_features = joblib.load(
    MODEL_DIR / "anomaly_features_v1.joblib"
)

weather_impact = joblib.load(
    MODEL_DIR / "weather_impact_v1.joblib"
)


print("All ML artifacts loaded successfully.")


# ============================================================
# 1. ETA PREDICTION
# ============================================================

def predict_eta_with_uncertainty(task_row):

    if isinstance(task_row, dict):
        task_row = pd.DataFrame([task_row])

    elif isinstance(task_row, pd.Series):
        task_row = task_row.to_frame().T

    model_features = [
        "Task Type",
        "Weather",
        "Operator Skill",
        "Machine Age (yrs)",
        "Estimated Time (min)"
    ]

    task_input = task_row[model_features]

    prediction = float(
        eta_model.predict(task_input)[0]
    )

    lower_bound = (
        prediction +
        eta_uncertainty["residual_lower"]
    )

    upper_bound = (
        prediction +
        eta_uncertainty["residual_upper"]
    )

    baseline = float(
        task_input["Estimated Time (min)"].iloc[0]
    )

    difference = prediction - baseline

    return {
        "predicted_time_min": round(prediction, 2),
        "lower_bound_min": round(lower_bound, 2),
        "upper_bound_min": round(upper_bound, 2),
        "baseline_time_min": round(baseline, 2),
        "difference_min": round(difference, 2)
    }


# ============================================================
# 2. ANOMALY DETECTION
# ============================================================

def predict_anomaly(machine_row):

    if isinstance(machine_row, dict):
        machine_row = pd.Series(machine_row)

    fuel = float(
        machine_row["Fuel Used (L)"]
    )

    load_cycles = float(
        machine_row["Load Cycles"]
    )

    idle_time = float(
        machine_row["Idling Time (min)"]
    )

    engine_hours = float(
        machine_row["Engine Hours"]
    )

    fuel_per_load = (
        fuel / load_cycles
        if load_cycles != 0
        else 0.0
    )

    idle_ratio = (
        idle_time / engine_hours
        if engine_hours != 0
        else 0.0
    )

    X = pd.DataFrame(
        [[
            fuel,
            load_cycles,
            idle_time,
            fuel_per_load,
            idle_ratio
        ]],
        columns=anomaly_features
    )

    prediction = anomaly_model.predict(X)[0]

    score = anomaly_model.decision_function(X)[0]

    is_anomaly = prediction == -1

    return {
        "anomaly": bool(is_anomaly),
        "anomaly_score": round(float(score), 4),

        "features": {
            "fuel_used_l": round(fuel, 3),
            "load_cycles": round(load_cycles, 3),
            "idling_time_min": round(idle_time, 3),
            "fuel_per_load_cycle": round(
                fuel_per_load, 4
            ),
            "idle_ratio": round(
                idle_ratio, 4
            )
        }
    }


# ============================================================
# 3. OPERATOR BASELINE DEVIATIONS
# ============================================================

def calculate_operator_deviations(
    row,
    operator_baseline
):

    operator = row["Operator ID"]

    if operator not in operator_baseline:
        return {}

    baseline = operator_baseline[operator]

    baseline_features = [
        "Fuel Used (L)",
        "Load Cycles",
        "Idling Time (min)",
        "Fuel per Load Cycle",
        "Idle Ratio"
    ]

    deviations = {}

    for feature in baseline_features:

        median = baseline[feature]["median"]

        mad = baseline[feature]["mad"]

        mad_safe = max(
            float(mad),
            1e-6
        )

        deviations[feature] = abs(
            float(row[feature]) - float(median)
        ) / mad_safe

    return deviations


# ============================================================
# 4. ANOMALY SEVERITY
# ============================================================

def calculate_anomaly_severity(
    deviations
):

    if not deviations:
        return "NORMAL", 0.0

    max_deviation = max(
        deviations.values()
    )

    if max_deviation > 3:
        severity = "HIGH"

    elif max_deviation >= 2:
        severity = "MEDIUM"

    else:
        severity = "LOW"

    return severity, max_deviation


# ============================================================
# 5. GROUPED ANOMALY EXPLANATION
# ============================================================

def build_grouped_anomaly_explanation(
    row,
    operator_baseline
):

    is_anomaly = bool(
        row["anomaly"]
    )

    # --------------------------------------------------------
    # Normal observation
    # --------------------------------------------------------

    if not is_anomaly:

        return {
            "anomaly": False,
            "operator_id": row["Operator ID"],
            "machine_id": row["Machine ID"],
            "severity": "NORMAL",
            "anomaly_score": round(
                float(row["anomaly_score"]),
                4
            ),
            "reasons": []
        }

    # --------------------------------------------------------
    # Calculate personalized deviations
    # --------------------------------------------------------

    deviations = calculate_operator_deviations(
        row,
        operator_baseline
    )

    severity, max_deviation = (
        calculate_anomaly_severity(
            deviations
        )
    )

    # --------------------------------------------------------
    # Feature groups
    # --------------------------------------------------------

    groups = {

        "Idling behavior": [
            "Idling Time (min)",
            "Idle Ratio"
        ],

        "Fuel efficiency": [
            "Fuel Used (L)",
            "Fuel per Load Cycle"
        ],

        "Work activity": [
            "Load Cycles"
        ]
    }

    reasons = []

    for factor, features in groups.items():

        available_features = [
            feature
            for feature in features
            if feature in deviations
        ]

        if not available_features:
            continue

        strongest_feature = max(
            available_features,
            key=lambda feature:
                deviations[feature]
        )

        deviation = deviations[
            strongest_feature
        ]

        if deviation >= 2:

            baseline = operator_baseline[
                row["Operator ID"]
            ][strongest_feature]["median"]

            reasons.append({

                "factor": factor,

                "feature": strongest_feature,

                "current_value": round(
                    float(
                        row[strongest_feature]
                    ),
                    3
                ),

                "baseline_median": round(
                    float(baseline),
                    3
                ),

                "deviation_mad": round(
                    float(deviation),
                    2
                )
            })

    reasons.sort(
        key=lambda x:
            x["deviation_mad"],
        reverse=True
    )

    return {

        "anomaly": True,

        "operator_id":
            row["Operator ID"],

        "machine_id":
            row["Machine ID"],

        "severity":
            severity,

        "anomaly_score":
            round(
                float(row["anomaly_score"]),
                4
            ),

        "reasons":
            reasons
    }


# ============================================================
# 6. SAFETY RULE ENGINE
# ============================================================

def evaluate_safety_rules(row):

    conditions = []

    if row["Seatbelt Status"] == "Unfastened":

        conditions.append({
            "rule":
                "SEATBELT_UNFASTENED",

            "severity":
                "CRITICAL",

            "message":
                "Seatbelt is unfastened."
        })

    if row["Safety Alert Triggered"] == "Yes":

        conditions.append({
            "rule":
                "SAFETY_ALERT",

            "severity":
                "HIGH",

            "message":
                "Safety alert has been triggered."
        })

    if any(
        condition["severity"] == "CRITICAL"
        for condition in conditions
    ):

        overall_status = "CRITICAL"

    elif any(
        condition["severity"] == "HIGH"
        for condition in conditions
    ):

        overall_status = "HIGH"

    else:

        overall_status = "NORMAL"

    return {
        "safety_status":
            overall_status,

        "conditions":
            conditions
    }


# ============================================================
# 7. SAFETY SCORE
# ============================================================

def calculate_safety_score(row):

    score = 100

    penalties = []

    if row["Seatbelt Status"] == "Unfastened":

        score -= 40

        penalties.append({
            "rule":
                "SEATBELT_UNFASTENED",

            "penalty":
                40
        })

    if row["Safety Alert Triggered"] == "Yes":

        score -= 20

        penalties.append({
            "rule":
                "SAFETY_ALERT",

            "penalty":
                20
        })

    score = max(
        0,
        score
    )

    if score < 50:

        status = "CRITICAL"

    elif score < 70:

        status = "HIGH"

    elif score < 85:

        status = "CAUTION"

    else:

        status = "NORMAL"

    return {

        "safety_score":
            score,

        "safety_status":
            status,

        "penalties":
            penalties
    }


# ============================================================
# 8. SAFETY ENGINE
# ============================================================

def safety_engine(row):

    rule_result = evaluate_safety_rules(
        row
    )

    score_result = calculate_safety_score(
        row
    )

    return {

        "safety_score":
            score_result["safety_score"],

        "safety_status":
            score_result["safety_status"],

        "conditions":
            rule_result["conditions"],

        "penalties":
            score_result["penalties"]
    }


# ============================================================
# 9. WEATHER IMPACT ENGINE
# ============================================================

def weather_impact_engine(
    task_type,
    weather
):

    matching = weather_impact[
        (weather_impact["Task Type"] == task_type) &
        (weather_impact["Weather"] == weather)
    ]

    if matching.empty:

        return {
            "available": False,
            "task_type": task_type,
            "weather": weather
        }

    result = matching.iloc[0]

    historical_delay = float(
        result["avg_delay"]
    )

    impact_vs_sunny = float(
        result["weather_delay_vs_sunny"]
    )

    if impact_vs_sunny > 1:

        direction = "increases"

    elif impact_vs_sunny < -1:

        direction = "decreases"

    else:

        direction = "minimal"

    return {

        "available": True,

        "task_type":
            task_type,

        "weather":
            weather,

        "historical_delay_min":
            round(
                historical_delay,
                2
            ),

        "weather_impact_vs_sunny_min":
            round(
                impact_vs_sunny,
                2
            ),

        "direction":
            direction
    }

# ============================================================
# 10. ETA WHAT-IF
# ============================================================

def eta_what_if(
    task_row,
    scenario_changes
):

    if isinstance(task_row, dict):

        original = pd.DataFrame(
            [task_row]
        )

    elif isinstance(task_row, pd.Series):

        original = task_row.to_frame().T

    else:

        original = task_row.copy()

    scenario = original.copy()

    for feature, value in (
        scenario_changes.items()
    ):

        scenario.loc[
            scenario.index[0],
            feature
        ] = value

    original_prediction = float(
        eta_model.predict(original)[0]
    )

    scenario_prediction = float(
        eta_model.predict(scenario)[0]
    )

    return {

        "original_context": {

            "weather":
                original[
                    "Weather"
                ].iloc[0],

            "task_type":
                original[
                    "Task Type"
                ].iloc[0]
        },

        "scenario":
            scenario_changes,

        "original_eta_min":
            round(
                original_prediction,
                2
            ),

        "scenario_eta_min":
            round(
                scenario_prediction,
                2
            ),

        "eta_change_min":
            round(
                scenario_prediction -
                original_prediction,
                2
            )
    }


# ============================================================
# 11. MULTI-SCENARIO ETA COMPARISON
# ============================================================

def compare_eta_scenarios(
    task_row,
    scenarios
):

    if isinstance(task_row, dict):

        task_row = pd.DataFrame(
            [task_row]
        )

    elif isinstance(task_row, pd.Series):

        task_row = task_row.to_frame().T

    current_prediction = float(
        eta_model.predict(
            task_row
        )[0]
    )

    results = []

    for scenario_name, changes in (
        scenarios.items()
    ):

        scenario = task_row.copy()

        for feature, value in (
            changes.items()
        ):

            scenario.loc[
                scenario.index[0],
                feature
            ] = value

        scenario_prediction = float(
            eta_model.predict(
                scenario
            )[0]
        )

        results.append({

            "scenario":
                scenario_name,

            "changes":
                changes,

            "predicted_eta_min":
                round(
                    scenario_prediction,
                    2
                ),

            "change_from_current_min":
                round(
                    scenario_prediction -
                    current_prediction,
                    2
                )
        })

    return {

        "current_eta_min":
            round(
                current_prediction,
                2
            ),

        "scenarios":
            results
    }


# ============================================================
# 12. COMPLETE INTELLIGENCE FUNCTION
# ============================================================

def run_intelligence(
    task_row,
    machine_row
):

    # --------------------------------------------------------
    # ETA
    # --------------------------------------------------------

    eta = predict_eta_with_uncertainty(
        task_row
    )

    # --------------------------------------------------------
    # Weather
    # --------------------------------------------------------

    task_type = (
        task_row["Task Type"]
        if isinstance(task_row, dict)
        else task_row["Task Type"]
    )

    weather = (
        task_row["Weather"]
        if isinstance(task_row, dict)
        else task_row["Weather"]
    )

    weather_context = weather_impact_engine(
        task_type,
        weather
    )

    # --------------------------------------------------------
    # What-if scenarios
    # --------------------------------------------------------

    scenarios = {

        "Sunny": {
            "Weather": "Sunny"
        },

        "Rainy": {
            "Weather": "Rainy"
        },

        "Windy": {
            "Weather": "Windy"
        }
    }

    what_if = compare_eta_scenarios(
        task_row,
        scenarios
    )

    # --------------------------------------------------------
    # Safety
    # --------------------------------------------------------

    safety = safety_engine(
        machine_row
    )

    # --------------------------------------------------------
    # Anomaly detection
    # --------------------------------------------------------

    anomaly_result = predict_anomaly(
        machine_row
    )

    # --------------------------------------------------------
    # Personalized baseline
    # --------------------------------------------------------

    if isinstance(machine_row, dict):

        behavior_row = pd.Series(
            machine_row
        )

    else:

        behavior_row = machine_row.copy()

    fuel = float(
        behavior_row["Fuel Used (L)"]
    )

    load_cycles = float(
        behavior_row["Load Cycles"]
    )

    engine_hours = float(
        behavior_row["Engine Hours"]
    )

    behavior_row[
        "Fuel per Load Cycle"
    ] = (
        fuel / load_cycles
        if load_cycles != 0
        else 0
    )

    behavior_row[
        "Idle Ratio"
    ] = (
        float(
            behavior_row[
                "Idling Time (min)"
            ]
        ) / engine_hours
        if engine_hours != 0
        else 0
    )

    # --------------------------------------------------------
    # Personalized anomaly explanation
    # --------------------------------------------------------

    operator_id = (
        behavior_row["Operator ID"]
    )

    if operator_id in operator_baselines:

        deviations = (
            calculate_operator_deviations(
                behavior_row,
                operator_baselines
            )
        )

        if anomaly_result["anomaly"]:

            severity, _ = (
                calculate_anomaly_severity(
                    deviations
                )
            )

            groups = {

                "Idling behavior": [
                    "Idling Time (min)",
                    "Idle Ratio"
                ],

                "Fuel efficiency": [
                    "Fuel Used (L)",
                    "Fuel per Load Cycle"
                ],

                "Work activity": [
                    "Load Cycles"
                ]
            }

            reasons = []

            for factor, features in (
                groups.items()
            ):

                available = [
                    feature
                    for feature in features
                    if feature in deviations
                ]

                if not available:
                    continue

                strongest = max(
                    available,
                    key=lambda feature:
                        deviations[feature]
                )

                deviation = deviations[
                    strongest
                ]

                if deviation >= 2:

                    baseline = (
                        operator_baselines[
                            operator_id
                        ][strongest]["median"]
                    )

                    reasons.append({

                        "factor":
                            factor,

                        "feature":
                            strongest,

                        "current_value":
                            round(
                                float(
                                    behavior_row[
                                        strongest
                                    ]
                                ),
                                3
                            ),

                        "baseline_median":
                            round(
                                float(baseline),
                                3
                            ),

                        "deviation_mad":
                            round(
                                float(deviation),
                                2
                            )
                    })

            reasons.sort(
                key=lambda x:
                    x["deviation_mad"],
                reverse=True
            )

            behavior = {

                "anomaly": True,

                "operator_id":
                    operator_id,

                "machine_id":
                    behavior_row[
                        "Machine ID"
                    ],

                "severity":
                    severity,

                "anomaly_score":
                    anomaly_result[
                        "anomaly_score"
                    ],

                "reasons":
                    reasons
            }

        else:

            behavior = {

                "anomaly": False,

                "operator_id":
                    operator_id,

                "machine_id":
                    behavior_row[
                        "Machine ID"
                    ],

                "severity":
                    "NORMAL",

                "anomaly_score":
                    anomaly_result[
                        "anomaly_score"
                    ],

                "reasons":
                    []
            }

    else:

        behavior = {

            "anomaly":
                anomaly_result[
                    "anomaly"
                ],

            "operator_id":
                operator_id,

            "machine_id":
                behavior_row[
                    "Machine ID"
                ],

            "severity":
                "UNKNOWN",

            "anomaly_score":
                anomaly_result[
                    "anomaly_score"
                ],

            "reasons":
                [],

            "message":
                "No operator baseline available."
        }

    # --------------------------------------------------------
    # Final unified response
    # --------------------------------------------------------

    return {

        "task": {

            "task_type":
                task_type,

            "weather":
                weather,

            "operator_skill":
                task_row[
                    "Operator Skill"
                ],

            "machine_age_years":
                float(
                    task_row[
                        "Machine Age (yrs)"
                    ]
                )
        },

        "eta":
            eta,

        "weather_context":
            weather_context,

        "what_if":
            what_if,

        "safety":
            safety,

        "behavior":
            behavior,

        "model_versions": {

            "eta":
                "eta_lr_v1",

            "anomaly":
                "anomaly_if_v1",

            "operator_baseline":
                "operator_mad_v1"
        }
    }