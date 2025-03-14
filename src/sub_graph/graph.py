from operator import add
from typing import List, Optional, Annotated, Dict
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from .state import (
    FailureAnalysisState,
    QuestionSummarizationState,
    Logs,
    EntryGraphState
)

# 子图 1
def get_failures(state):
    docs = state["docs"]
    failures = [doc for doc in docs if "grade" in doc and doc.get("grade") is not None]
    return {"failures": failures}


def generate_summary(state):
    failures = state["failures"]
    # Add fxn: fa_summary = summarize(failures)
    fa_summary = "Poor quality retrieval of Chroma documentation."
    return {"fa_summary": fa_summary}


fa_builder = StateGraph(FailureAnalysisState)
fa_builder.add_node("get_failures", get_failures)
fa_builder.add_node("generate_summary", generate_summary)
fa_builder.add_edge(START, "get_failures")
fa_builder.add_edge("get_failures", "generate_summary")
fa_builder.add_edge("generate_summary", END)

# 子图 2
def generate_summary_qs(state):
    docs = state["docs"]
    # Add fxn: summary = summarize(docs)
    summary = "Questions focused on usage of ChatOllama and Chroma vector store."
    return {"qs_summary": summary}


def send_to_slack(state):
    qs_summary = state["qs_summary"]
    # Add fxn: report = report_generation(qs_summary)
    report = "foo bar baz"
    return {"report": report}


def format_report_for_slack(state):
    report = state["report"]
    # Add fxn: formatted_report = report_format(report)
    formatted_report = "foo bar"
    return {"report": formatted_report}


qs_builder = StateGraph(QuestionSummarizationState)
qs_builder.add_node("generate_summary", generate_summary_qs)
qs_builder.add_node("send_to_slack", send_to_slack)
qs_builder.add_node("format_report_for_slack", format_report_for_slack)
qs_builder.add_edge(START, "generate_summary")
qs_builder.add_edge("generate_summary", "send_to_slack")
qs_builder.add_edge("send_to_slack", "format_report_for_slack")
qs_builder.add_edge("format_report_for_slack", END)


# 入口图
def convert_logs_to_docs(state):
    # Get logs
    raw_logs = state["raw_logs"]
    # 示例数据转换
    question_answer = {
        "id": "1",
        "question": "How do I use ChatOllama?",
        "docs": [],
        "answer": "ChatOllama is a...",
        "grade": None,
        "grader": None,
        "feedback": None
    }
    
    question_answer_feedback = {
        "id": "2",
        "question": "How do I use Chroma?",
        "docs": [],
        "answer": "Chroma is a vector store...",
        "grade": 3,
        "grader": "auto",
        "feedback": "The answer is incomplete."
    }
    
    docs = [question_answer, question_answer_feedback]
    return {"docs": docs}


entry_builder = StateGraph(EntryGraphState)
entry_builder.add_node("convert_logs_to_docs", convert_logs_to_docs)
entry_builder.add_node("question_summarization", qs_builder.compile())
entry_builder.add_node("failure_analysis", fa_builder.compile())

entry_builder.add_edge(START, "convert_logs_to_docs")
entry_builder.add_edge("convert_logs_to_docs", "failure_analysis")
entry_builder.add_edge("convert_logs_to_docs", "question_summarization")
entry_builder.add_edge("failure_analysis", END)
entry_builder.add_edge("question_summarization", END)

graph = entry_builder.compile()


if __name__ == "__main__":
    raw_logs = [{"foo": "bar"}, {"foo": "baz"}]
    result = graph.invoke({"raw_logs": raw_logs}, debug=False)
    print(result)
