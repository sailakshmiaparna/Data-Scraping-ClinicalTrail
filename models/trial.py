"""Canonical, source-neutral clinical trial model."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Trial:
    source: str
    nct_id: str
    brief_title: str = ""
    official_title: str = ""
    study_type: str = ""
    study_status: str = ""
    phase: list[str] = field(default_factory=list)
    sponsor: str = ""
    collaborators: list[str] = field(default_factory=list)
    enrollment: int | None = None
    conditions: list[str] = field(default_factory=list)
    interventions: list[dict[str, str]] = field(default_factory=list)
    outcomes: list[dict[str, str]] = field(default_factory=list)
    eligibility: dict[str, Any] = field(default_factory=dict)
    study_design: dict[str, Any] = field(default_factory=dict)
    locations: list[dict[str, str]] = field(default_factory=list)
    investigators: list[dict[str, str]] = field(default_factory=list)
    start_date: str = ""
    completion_date: str = ""
    results: dict[str, Any] = field(default_factory=dict)
    url: str = ""
    medical_knowledge: dict[str, Any] = field(default_factory=dict)
