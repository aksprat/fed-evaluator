# GitHub Issue Classification Evaluator

## Overview

This project implements an evaluation harness for classifying GitHub issues from the `digitalocean/doctl` repository using DigitalOcean Serverless Inference.

The system:

* Collects issues from the `doctl` GitHub repository.
* Builds a manually curated ground truth dataset.
* Evaluates multiple candidate models.
* Measures both quality and operational metrics.
* Provides a Streamlit-based interface for analysis and comparison.
* Recommends two models based on observed tradeoffs.

---

# Problem Statement

Classify GitHub issues into exactly one of the following categories:

* bug
* enhancement
* question
* documentation
* security
* other

Each issue is processed independently using one inference request.

---

# Repository Structure

```
.
├── app.py
├── Dockerfile
├── requirements.txt
├── README.md
│
├── data/
│   ├── issues_snapshot.json
│   └── ground_truth.csv
│
├── github/
│   └── fetch_issues.py
│
├── inference/
│   ├── client.py
│   └── classifier.py
│
├── evaluation/
│   ├── runner.py
│   └── metrics.py
│
├── results/
│
└── metrics/
```

---

# Data Collection

Issues were collected from:

```
digitalocean/doctl
```

using the GitHub API.

Configuration:

* Open issues included
* Closed issues included
* Pull requests excluded

### Corpus Size

Total issues:

```
239
```

These represent the full corpus used for inference.

---

# Ground Truth Construction

Historical GitHub labels are inconsistent and heavily skewed toward bug reports.

Therefore, ground truth was constructed separately from the full corpus.

## Methodology

Started with high-confidence issues having a single maintainer label.

Then manually reviewed and curated issues to better align with the target schema and used keywrods like: 
*suggestions, incomplete, feature -> enhancement
*how, what, why, can, unclear, ? -> question
*failing, error, bug, cannot -> bug
*auth, credentials,security vulnerabilities, login -> security
*docs, update -> documentation
*spam, duplicate, off topic, ambigious -> other


### Final Ground Truth Size

```
96 issues
```

The remaining issues are treated as unscored data.

---

# Candidate Models Evaluated

Five candidate models were evaluated.

1. alibaba-qwen3-32b
2. mistral-3-14b
3. deepseek-r1-distill-llama-70b
4. llama3.3-70b-instruct
5. llama-4-maverick

The final two models shown in the UI were selected based on empirical evaluation rather than assumption.

---

# Prompting Strategy

Each issue is classified independently.

Inputs:

* issue title
* issue body

Temperature:

```
0
```

Output format:

```json
{
  "label": "bug"
}
```

A strict JSON response was enforced.

---

# Parallel Processing

Inference requests are executed concurrently.

Concurrency is configurable through:

```bash
CONCURRENCY=10
```

Each issue corresponds to exactly one inference request.

Failures are tracked individually.

---

# Evaluation Metrics

## Quality Metrics

Computed on the 96-issue ground truth set:

* Accuracy
* Precision
* Recall
* F1 score
* Per-class metrics
* Confusion matrix

---

## Operational Metrics

Computed on the full corpus:

* p50 latency
* p95 latency
* Throughput
* Wall-clock time
* Error breakdown

---

# Results

## Model Comparison

| Model                         | Accuracy | P50 Latency | Throughput  |
| ----------------------------- | -------- | ----------- | ----------- |
| alibaba-qwen3-32b             | 54.2%    | 7.5 sec     | 1.03 req/s  |
| mistral-3-14b                 | 57.3%    | 8.7 sec     | 0.80 req/s  |
| deepseek-r1-distill-llama-70b | 53.1%    | 13.3 sec    | 0.72 req/s  |
| llama3.3-70b-instruct         | 58.3%    | 1.6 sec     | 5.91 req/s  |
| llama-4-maverick              | 54.2%    | 0.34 sec    | 27.16 req/s |

---

# Recommended Models

## Primary Recommendation

### llama3.3-70b-instruct

Strengths:

* Highest observed accuracy
* Strong latency profile
* Good throughput
* Best overall quality

Suitable for:

* quality-sensitive workloads

---

## Secondary Recommendation

### llama-4-maverick

Strengths:

* Extremely low latency
* Highest throughput
* Competitive accuracy

Suitable for:

* high-volume workloads
* latency-sensitive applications

---

# Streamlit Application

The application provides four views.

## Scored View

Displays:

* Accuracy comparison
* Confusion matrices
* Per-class precision
* Recall
* F1 scores

---

## Unscored View

Displays:

* Predictions
* Raw model outputs
* Label distributions
* Agreement rates
* Disagreement explorer

---

## Operational Metrics

Displays:

* P50 latency
* P95 latency
* Throughput

---

## Recommendation

Summarizes:

* Recommended models
* Tradeoffs
* Deployment considerations

---

# Running Locally

## Install dependencies

```bash
pip install -r requirements.txt
```

---

## Configure environment variables

Create:

```
.env
```

Example:

```bash
DO_API_KEY=your_api_key
CONCURRENCY=10
```

---

## Launch Streamlit

```bash
streamlit run app.py
```

Application:

```
http://localhost:8501
```

---

# Docker

Build:

```bash
docker build -t fed-evaluator .
```

Run:

```bash
docker run \
-p 8501:8501 \
--env-file .env \
fed-evaluator
```

---


# Conclusion

This project demonstrates an end-to-end evaluation workflow for LLM-powered issue classification.

The implementation emphasizes:

* reproducible evaluation
* measurable tradeoffs
* operational observability
* production-oriented thinking

rather than optimizing solely for benchmark accuracy.
