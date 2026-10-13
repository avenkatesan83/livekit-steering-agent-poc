from dataclasses import dataclass


@dataclass
class UserData:
    session_id: str | None = None
    ani: str | None = None
    caller_name: str = "XYZ"
    authenticated: bool = False
    intent: str | None = None
