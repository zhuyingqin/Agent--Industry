from typing import List, Dict, TypedDict, Optional, Annotated
from operator import add

# The structure of the logs
class Logs(TypedDict):
    id: str
    question: str
    docs: Optional[List]
    answer: str
    grade: Optional[int]
    grader: Optional[str]
    feedback: Optional[str]


# Failure Analysis Sub-graph
class FailureAnalysisState(TypedDict):
    docs: List[Logs] # from entry graph
    failures: List[Logs]
    fa_summary: str


# Summarization subgraph
class QuestionSummarizationState(TypedDict):
    docs: List[Logs] # from entry graph
    qs_summary: str
    report: str

# Entry Graph
class EntryGraphState(TypedDict):
    raw_logs: Annotated[List[Dict], add]
    docs: Annotated[List[Logs], add]  # This will be used in sub-graphs
    fa_summary: str                   # This will be generated in the FA sub-graph
    report: str                       # This will be generated in the QS sub-graph