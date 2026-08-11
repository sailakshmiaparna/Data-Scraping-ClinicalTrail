# MedicalKnowledgeAcquisitionAgent

This project collects clinical trial data from ClinicalTrials.gov for the topic configured in `config/settings.yaml`, parses trials into a canonical `Trial` object, extracts basic medical knowledge, and appends normalized entries into a Markdown repository at `output/`.

Run with:

```
python main.py
```
