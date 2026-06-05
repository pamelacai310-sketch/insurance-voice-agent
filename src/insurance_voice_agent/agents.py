"""Agent role definitions for the planned collection pipeline."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AgentRole:
    name: str
    responsibility: str
    primary_output: str


AGENT_ROLES: tuple[AgentRole, ...] = (
    AgentRole(
        name="source_planner",
        responsibility="Expand insurance terms, brands, products, and complaint scenarios into source-specific collection tasks.",
        primary_output="Prioritized search and source tasks with a six-month date window.",
    ),
    AgentRole(
        name="compliance_gate",
        responsibility="Block sources that require login, bypassing controls, or unsafe personal-data handling.",
        primary_output="Allow, deny, or manual-review decision with reason.",
    ),
    AgentRole(
        name="collector",
        responsibility="Fetch public comments through APIs, crawlers, or browser automation with rate limits and retry state.",
        primary_output="Raw page/comment evidence and collection metadata.",
    ),
    AgentRole(
        name="extractor",
        responsibility="Transform raw evidence into validated InsuranceMention records.",
        primary_output="Schema-valid candidate mentions.",
    ),
    AgentRole(
        name="analyzer",
        responsibility="Assign sentiment, aspect, product-category, and intent labels.",
        primary_output="Analysis labels with confidence and model trace metadata.",
    ),
    AgentRole(
        name="qa_auditor",
        responsibility="Sample records, compare against source evidence, and flag extraction or compliance issues.",
        primary_output="Quality findings and adapter improvement tasks.",
    ),
)
