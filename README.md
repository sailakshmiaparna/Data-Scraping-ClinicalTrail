# MedicalKnowledgeAcquisitionAgent

This project collects clinical trial data from ClinicalTrials.gov for the topic configured in `config/settings.yaml`, parses trials into a canonical `Trial` object, extracts basic medical knowledge, and appends normalized entries into a Markdown repository at `output/`.

Run with:

```
python main.py
```

## ClinicalTrials.gov Agent

The ClinicalTrials.gov Agent searches and collects relevant clinical trial records for **Metabolic Health / Insulin Resistance**. It retrieves available trial information through the ClinicalTrials.gov API, parses the raw response, and converts each study into the standard `Trial` object.

The pipeline is:

```
ClinicalTrials.gov
↓
Collector
↓
Parser
↓
Medical Knowledge Extractor
↓
Standard Trial Object
↓
Markdown Storage
```

- **Collector:** Searches and retrieves clinical trial records and handles pagination.
- **Parser:** Converts raw ClinicalTrials.gov data into the standard `Trial` object.
- **Medical Knowledge Extractor:** Extracts important medical and clinical information from the trial.
- **Markdown Storage:** Stores the normalized trial information in the Markdown repository.

## Extracted Clinical Trial Data

The system extracts the following information when available:

- NCT ID
- Brief Title
- Official Title
- Study Type
- Study Status
- Phase
- Sponsor
- Collaborators
- Enrollment / Sample Size
- Conditions / Diseases
- Population
- Eligibility Criteria
- Age
- Sex
- Intervention
- Comparator
- Primary Outcomes
- Secondary Outcomes
- Study Design
- Start Date
- Completion Date
- Locations
- Investigators
- Results
- Adverse Events
- Clinical Claims
- Evidence Type
- Evidence Level
- Confidence
- ClinicalTrials.gov URL

The medical knowledge extraction stage also identifies, when available:

- Diseases
- Biomarkers
- Risk Factors
- Population characteristics
- Interventions
- Comparators
- Outcomes
- Results
- Clinical Claims
- Evidence information

Field availability depends on the individual ClinicalTrials.gov record. The system does not invent missing information.

## Standard Trial Object

Every ClinicalTrials.gov record is converted into the same canonical Python object:

```
Trial(...)
```

This allows the downstream extraction and storage components to process all clinical trials using one standardized structure.

## Knowledge Repository

The normalized clinical trial data is stored in:

```
output/metabolic_health_insulin_resistance_clinicaltrials.md
```

Each processed clinical trial becomes a structured Markdown entry.
