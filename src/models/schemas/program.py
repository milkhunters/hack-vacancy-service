from pydantic import BaseModel


class ProgramResult(BaseModel):
    is_correct: bool
    stdout: str | None
    stderr: str | None
    service_message: str | None
