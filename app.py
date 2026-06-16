import json

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="GitHub Issue Classification Evaluator",
    layout="wide"
)

st.title("GitHub Issue Classification Evaluator")


MODELS = [
    "alibaba-qwen3-32b",
    "mistral-3-14b",
    "deepseek-r1-distill-llama-70b",
    "llama3.3-70b-instruct",
    "llama-4-maverick"
]


# ==================================================
# Load metrics
# ==================================================

metric_rows = []

for model in MODELS:

    with open(
        f"metrics/{model}_metrics.json"
    ) as f:

        m = json.load(f)

    metric_rows.append({

        "Model": model,

        "Accuracy":
            round(
                m["accuracy"],
                3
            ),

        "P50 Latency":
            round(
                m["p50_latency_seconds"],
                2
            ),

        "P95 Latency":
            round(
                m["p95_latency_seconds"],
                2
            ),

        "Throughput":
            round(
                m["throughput_rps"],
                2
            )

    })

metrics_df = pd.DataFrame(
    metric_rows
)


tab1, tab2, tab3, tab4 = st.tabs(

    [

        "Scored View",

        "Unscored View",

        "Operational Metrics",

        "Recommendation"

    ]

)


# ==================================================
# TAB 1
# ==================================================

with tab1:

    st.header(
        "Scored Evaluation"
    )

    st.dataframe(
        metrics_df,
        use_container_width=True
    )

    fig_accuracy = px.bar(

        metrics_df,

        x="Model",

        y="Accuracy",

        title="Accuracy Comparison"

    )

    st.plotly_chart(
        fig_accuracy,
        use_container_width=True
    )

    st.subheader(
        "Confusion Matrix"
    )

    selected_model = st.selectbox(

        "Select model",

        MODELS

    )

    with open(
        f"metrics/{selected_model}_metrics.json"
    ) as f:

        metric_data = json.load(f)

    cm = np.array(
        metric_data["confusion_matrix"]
    )

    labels = metric_data["labels"]

    fig_cm = px.imshow(

        cm,

        x=labels,

        y=labels,

        text_auto=True,

        title=f"{selected_model}"

    )

    st.plotly_chart(
        fig_cm,
        use_container_width=True
    )

    st.subheader(
        "Per-Class Metrics"
    )

    report = metric_data[
        "classification_report"
    ]

    rows = []

    for label, values in report.items():

        if label in [

            "accuracy",

            "macro avg",

            "weighted avg"

        ]:

            continue

        rows.append(

            {

                "Class": label,

                "Precision":
                    round(
                        values["precision"],
                        3
                    ),

                "Recall":
                    round(
                        values["recall"],
                        3
                    ),

                "F1":
                    round(
                        values["f1-score"],
                        3
                    )

            }

        )

    st.dataframe(

        pd.DataFrame(rows),

        use_container_width=True

    )


# ==================================================
# TAB 2
# ==================================================

with tab2:

    st.header(
        "Unscored Predictions"
    )

    selected_model = st.selectbox(

        "Prediction model",

        MODELS,

        key="prediction_model"

    )

    with open(

        f"results/{selected_model}.json"

    ) as f:

        result_data = json.load(f)

    predictions = pd.DataFrame(

        result_data["results"]

    )

    st.subheader(
        "Prediction Distribution"
    )

    counts = (

        predictions[
            "prediction"
        ]

        .value_counts()

        .reset_index()

    )

    counts.columns = [

        "label",

        "count"

    ]

    fig_dist = px.bar(

        counts,

        x="label",

        y="count",

        title="Label Distribution"

    )

    st.plotly_chart(

        fig_dist,

        use_container_width=True

    )

    st.subheader(
        "Predictions"
    )

    st.dataframe(

        predictions[
            [

                "issue_number",

                "prediction",

                "raw_output",

                "latency_seconds"

            ]

        ],

        use_container_width=True

    )

    # -------------------------------------

    st.header(
        "Model Agreement"
    )

    with open(
        "results/llama3.3-70b-instruct.json"
    ) as f:

        model_a = json.load(f)

    with open(
        "results/llama-4-maverick.json"
    ) as f:

        model_b = json.load(f)

    a_df = pd.DataFrame(
        model_a["results"]
    )[
        [

            "issue_number",

            "prediction"

        ]

    ]

    a_df.rename(

        columns={

            "prediction":

                "llama3.3"

        },

        inplace=True

    )

    b_df = pd.DataFrame(
        model_b["results"]
    )[
        [

            "issue_number",

            "prediction"

        ]

    ]

    b_df.rename(

        columns={

            "prediction":

                "maverick"

        },

        inplace=True

    )

    merged = a_df.merge(

        b_df,

        on="issue_number"

    )

    merged[
        "agree"
    ] = (

        merged[
            "llama3.3"
        ]

        ==

        merged[
            "maverick"
        ]

    )

    agreement_rate = (

        merged[
            "agree"
        ]

        .mean()

        * 100

    )

    st.metric(

        "Agreement Rate",

        f"{agreement_rate:.1f}%"

    )

    disagreements = merged[
        ~merged["agree"]
    ]

    st.subheader(
        "Disagreements"
    )

    st.dataframe(

        disagreements,

        use_container_width=True

    )


# ==================================================
# TAB 3
# ==================================================

with tab3:

    st.header(
        "Operational Metrics"
    )

    fig1 = px.bar(

        metrics_df,

        x="Model",

        y="P50 Latency",

        title="P50 Latency"

    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

    fig2 = px.bar(

        metrics_df,

        x="Model",

        y="P95 Latency",

        title="P95 Latency"

    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    fig3 = px.bar(

        metrics_df,

        x="Model",

        y="Throughput",

        title="Throughput"

    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )


# ==================================================
# TAB 4
# ==================================================

with tab4:

    st.header(
        "Recommended Models"
    )

    st.subheader(
        "Primary Recommendation"
    )

    st.markdown(
        """
### llama3.3-70b-instruct

- Highest accuracy
- Strong latency profile
- Best quality-oriented model
"""
    )

    st.subheader(
        "Secondary Recommendation"
    )

    st.markdown(
        """
### llama-4-maverick

- Fastest model
- Highest throughput
- Suitable for high-volume workloads
"""
    )

    st.subheader(
        "Tradeoff"

    )

    st.markdown(
        """
| Model | Strength |
|--------|----------|
| llama3.3-70b-instruct | Quality |
| llama-4-maverick | Speed |
"""
    )
