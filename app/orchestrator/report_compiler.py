from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Report:
    query: str
    sections: list[dict] = field(default_factory=list)
    generated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_markdown(self) -> str:
        lines = [f"# Research Report: {self.query}", f"_Generated: {self.generated_at}_\n"]
        for section in self.sections:
            lines.append(f"## {section['sub_question']}")
            lines.append(section["summary_text"])
            if section.get("unverified_claims"):
                lines.append("\n> ⚠️ Unverified claims:")
                for claim in section["unverified_claims"]:
                    lines.append(f"> - {claim}")
            lines.append("\n**Sources:**")
            for i, src in enumerate(section["sources"], 1):
                lines.append(f"{i}. [{src['title']}]({src['url']})")
            lines.append("")
        return "\n".join(lines)


class ReportCompiler:
    def __init__(self, config):
        self.config = config

    def compile(self, query: str, results: dict) -> Report:
        sections = []
        for sub_question, data in results.items():
            verification = data["verification"]
            sections.append({
                "sub_question": sub_question,
                "summary_text": data["summary"].text,
                "sources": data["sources"],
                "unverified_claims": verification.unverified_claims,
            })
        return Report(query=query, sections=sections)