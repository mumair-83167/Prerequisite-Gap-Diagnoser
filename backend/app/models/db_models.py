from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import time


class SessionState(str, Enum):
    PRESENT_PROBLEM = "PRESENT_PROBLEM"
    AWAIT_RESULT = "AWAIT_RESULT"
    DIAGNOSING = "DIAGNOSING"
    TEACHING = "TEACHING"
    TEACH_BACK = "TEACH_BACK"
    RE_TEST = "RE_TEST"
    RESOLVED = "RESOLVED"


class SessionRecord(BaseModel):
    session_id: str
    state: SessionState = SessionState.PRESENT_PROBLEM
    target_node_id: str = "recursion"
    diagnosed_gap_node_id: Optional[str] = None
    current_candidate_node_id: Optional[str] = None
    probing_question: Optional[str] = None
    traversal_path: List[str] = Field(default_factory=list)
    mastered_nodes: List[str] = Field(default_factory=list)
    history: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)
