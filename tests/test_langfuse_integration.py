import pytest
from app.main import CommandRequest, execute_command, get_langfuse_stats
from app.engine.command_parser import CommandParser
from app.feeds.ai_research import ai_research_feed

def test_command_parser_lang():
    parsed = CommandParser.parse("LANG <GO>")
    assert parsed["valid"] is True
    assert parsed["function"] == "LANG"

    parsed_trace = CommandParser.parse("TRACE")
    assert parsed_trace["valid"] is True
    assert parsed_trace["function"] == "LANG"

def test_ai_research_memo_tracing():
    memo = ai_research_feed.generate_research_memo("NVDA", 120.0)
    assert "langfuse_trace_id" in memo
    assert "langfuse_url" in memo
    assert memo["langfuse_trace_id"]
    assert "traces/" in memo["langfuse_url"]

    telemetry = ai_research_feed.get_langfuse_telemetry()
    assert "total_traces" in telemetry
    assert telemetry["total_traces"] >= 1
    assert len(telemetry["recent_traces"]) >= 1
    latest = telemetry["recent_traces"][0]
    assert latest["symbol"] == "NVDA"

@pytest.mark.asyncio
async def test_execute_command_lang():
    res = await execute_command(CommandRequest(command="LANG <GO>"))
    assert res["success"] is True
    assert res["parsed"]["function"] == "LANG"
    data = res["data"]
    assert "total_traces" in data
    assert "host" in data
    assert "recent_traces" in data

@pytest.mark.asyncio
async def test_api_langfuse_stats():
    stats = await get_langfuse_stats()
    assert isinstance(stats, dict)
    assert "host" in stats
    assert "total_traces" in stats
    assert "external_url" in stats
