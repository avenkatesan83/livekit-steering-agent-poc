from functools import lru_cache
from pathlib import Path
import re


_INSTRUCTION_FILE = Path(__file__).with_name("agent_instructions.md")

_SECTION_PATTERN = re.compile(
  r"^##\s+(id_verification|itss_steering)\s*$\n(.*?)(?=^##\s+\w+\s*$|\Z)",
  re.MULTILINE | re.DOTALL,
)


@lru_cache(maxsize=1)
def _load_instruction_map() -> dict[str, str]:
  if not _INSTRUCTION_FILE.exists():
    raise FileNotFoundError(
      f"Missing instruction file: {_INSTRUCTION_FILE.name}"
    )

  instruction_map: dict[str, str] = {}
  content = _INSTRUCTION_FILE.read_text(encoding="utf-8")

  for match in _SECTION_PATTERN.finditer(content):
    section_name = match.group(1)
    section_body = match.group(2).strip()
    if section_body:
      instruction_map[section_name] = section_body

  return instruction_map


def _get_instruction(agent_key: str) -> str:
  instruction = _load_instruction_map().get(agent_key)
  if not instruction:
    raise KeyError(
      f"Missing instruction for agent '{agent_key}' in {_INSTRUCTION_FILE.name}."
    )
  return instruction


ID_VERIFICATION_AGENT_INSTRUCTIONS = _get_instruction("id_verification")
ITSS_STEERING_AGENT_INSTRUCTIONS = _get_instruction("itss_steering")
