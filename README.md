# Doctoome Data Case Study

## Overview

This project analyzes data from a synthetic Type 2 Diabetes awareness campaign.

The objective is to build a reproducible data pipeline, assess campaign performance, analyze questionnaire behavior, explore audience characteristics, and identify relevant patterns that could support business and product decisions.

The questionnaire outcomes used in this project are analytical/self-reported categories and should not be interpreted as medical diagnoses.

---

## Objectives

The project focuses on:

- Data quality assessment and cleaning
- Construction of reusable analytical datasets
- Campaign performance analysis
- Audience analysis
- Questionnaire completion and dropout analysis
- Acquisition source and device analysis
- Outcome distribution analysis
- Exploratory analysis of behavioral and temporal patterns

---

## Tech Stack

- Python 3.12
- Pandas
- DuckDB
- PyArrow
- Matplotlib
- Jupyter Notebook
- Parquet  
- Streamlit

---

## Data Pipeline

The project follows a three-layer architecture:

Raw  
  ↓  
Processed  
  ↓  
Analytics  

Raw

- Original datasets are kept unchanged.

Processed

- Contains cleaned and standardized datasets.

Main transformations include:

- Standardization of gender values  
- Standardization of region values  
- Standardization of acquisition sources  
- Removal of visitors identified as inconsistent according to the defined analytical rule  
- Preservation of relational consistency across sessions, events, answers and outcomes  
- Analytics  

Reusable analytical tables are generated from the processed layer:

- visitor_analytics.parquet
- session_analytics.parquet
- question_analytics.parquet

These tables are used for the final analysis.

---

## Project Structure


Doctoome_CaseStudy/  
│  
├── data/  
│   ├── raw/  
│   ├── processed/  
│   └── analytics/  
│  
├── notebooks/  
│   ├── 01_Display.ipynb  
│   ├── 02_EDA.ipynb  
│   ├── 03_Cleaning.ipynb  
│   ├── 04_Analytics.ipynb 
│   └── 05_Analysis.ipynb 
│  
├── src/  
│   ├── cleaning/  
│   └── analytics/  
│  
├──Visualitsation  
│   └── app.py  
│  
├── requirements.txt  
│  
└── README.md  

---

## Analytical Areas

The analysis covers several dimensions.

## Campaign Overview
- Unique visitors
- Total sessions
- Questionnaire start rate
- Questionnaire completion rate
- Returning visitors
- Outcome distribution

## Audience
- Age groups
- Gender
- Region
- Outcomes by demographic group
- Missing demographic information

## campaign Performance
- Sessions by campaign
- Completion rate by campaign
- Acquisition source performance
- Device performance
- Outcome distribution by campaign/source/device
- Questionnaire Behavior
- Questions reached
- Answer rate
- Dropout rate
- Average and median response time
- Response patterns
- Frequent answer combinations before abandonment

---

## Installation

Clone the repository:  
```bash
git clone <repository-url>
cd Doctoome_CaseStudy
```

Create a virtual environment:  
```bash
python -m venv .venv
```

Activate the virtual environment on Windows:  
```bash
.venv\Scripts\activate
```

Install the required dependencies:
```bash
pip install -r requirements.txt
```
---

## Reproducing the Analysis

run the notebooks in their respected order.  
- further explanation is listed in the notebooks content.  
- to the run the streamlit app you must run this command on root folder
```bash
streamlit run Visualisation/app.py
```

---

## Data Quality

The initial exploratory analysis included checks for:  

- Missing critical identifiers  
- Exact duplicates  
- Orphaned records  
- Timestamp inconsistencies  
- Questionnaire completion consistency  
- Answer/view consistency  
- Categorical inconsistencies  

The dataset was found to be structurally consistent overall, requiring mainly categorical normalization and limited filtering.  
---


## Disclaimer

- Questionnaire outcomes should not be interpreted as clinical diagnoses.  
- Observed relationships are associations and do not establish causality.  