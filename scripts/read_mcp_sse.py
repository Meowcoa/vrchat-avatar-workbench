#!/usr/bin/env python3
"""Read MCP resources over JSON or multi-event Server-Sent Events.

This helper is intentionally read-only: it initializes an MCP session and sends
only ``resources/read`` requests.  It handles every SSE event in a response;
the older one-message parser incorrectly joined multiple ``data:`` fields from
different events into one JSON document.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Any, Iterable, Iterator


@dataclass(frozen=True)
class SSEEvent:
    event: str | None
    data: str
    event_id: str | None = None
    retry: int | None = None


def parse_sse_lines(lines: Iterable[str]) -> Iterator[SSEEvent]:
    """Parse SSE framing and emit one event per blank-line-delimited frame."""

    event_name: str | None = None
    event_id: str | None = None
    retry: int | None = None
    data_lines: list[str] = []

    def flush() -> SSEEvent | None:
        nonlocal event_name, event_id, retry, data_lines
        if not data_lines and event_name is None and event_id is None and retry is None:
            return None
        event = SSEEvent(event_name, "\n".join(data_lines), event_id, retry)
        event_name = None
        event_id = None
        retry = None
        data_lines = []
        return event

    for raw_line in lines:
        line = raw_line.rstrip("\r\n")
        if line == "":
            event = flush()
            if event is not None:
                yield event
            continue
        if line.startswith(":"):
            continue
        field, separator, value = line.partition(":")
        if separator and value.startswith(" "):
            value = value[1:]
        if field == "event":
            event_name = value
        elif field == "data":
            data_lines.append(value)
        elif field == "id":
            event_id = value
        elif field == "retry":
            try:
                retry = int(value)
            except ValueError:
                retry = None
    event = flush()
    if event is not None:
        yield event


def parse_sse_text(text: str) -> list[SSEEvent]:
    return list(parse_sse_lines(StringIO(text)))


def json_messages_from_sse(text: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    messages: list[dict[str, Any]] = []
    non_json_events: list[dict[str, Any]] = []
    for event in parse_sse_text(text):
        if not event.data:
            non_json_events.append({"event": event.event, "data": "", "id": event.event_id})
            continue
        try:
            value = json.loads(event.data)
        except json.JSONDecodeError:
            non_json_events.append({"event": event.event, "data": event.data, "id": event.event_id})
            continue
        if isinstance(value, dict):
            messages.append(value)
        else:
            non_json_events.append({"event": event.event, "data": value, "id": event.event_id})
    return messages, non_json_events


def parse_response(body: bytes, content_type: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    text = body.decode("utf-8", errors="replace")
    if "text/event-stream" in content_type.lower() or text.lstrip().startswith(("event:", "data:", ":")):
        return json_messages_from_sse(text)
    if not text.strip():
        return [], []
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        return [], [{"event": None, "data": text, "parse_error": exc.msg}]
    return ([value] if isinstance(value, dict) else []), ([] if isinstance(value, dict) else [{"event": None, "data": value}])


def header_value(headers: Any, wanted: str) -> str | None:
    wanted = wanted.casefold()
    for key, value in headers.items():
        if key.casefold() == wanted:
            return value
    return None


def post_json_rpc(
    url: str,
    payload: dict[str, Any],
    session_id: str | None,
    timeout: float,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], str | None]:
    headers = {
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json",
    }
    if session_id:
        headers["Mcp-Session-Id"] = session_id
    request = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = response.read()
        content_type = response.headers.get("Content-Type", "")
        messages, non_json = parse_response(body, content_type)
        return messages, non_json, header_value(response.headers, "mcp-session-id")


def response_for_id(messages: list[dict[str, Any]], request_id: int) -> dict[str, Any] | None:
    for message in messages:
        if message.get("id") == request_id:
            return message
    return None


def read_resources(url: str, uris: list[str], protocol_version: str, timeout: float) -> dict[str, Any]:
    session_id: str | None = None
    initialize = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": protocol_version,
            "capabilities": {},
            "clientInfo": {"name": "vrchat-avatar-workbench", "version": "1.0"},
        },
    }
    init_messages, init_non_json, response_session = post_json_rpc(url, initialize, session_id, timeout)
    session_id = response_session or session_id
    init_response = response_for_id(init_messages, 1)
    if init_response is None:
        raise RuntimeError("MCP initialize returned no JSON-RPC response")
    if "error" in init_response:
        raise RuntimeError(json.dumps(init_response["error"], ensure_ascii=False))

    initialized = {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}
    _, initialized_non_json, response_session = post_json_rpc(url, initialized, session_id, timeout)
    session_id = response_session or session_id

    results: list[dict[str, Any]] = []
    for request_id, uri in enumerate(uris, start=2):
        payload = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": "resources/read",
            "params": {"uri": uri},
        }
        messages, non_json, response_session = post_json_rpc(url, payload, session_id, timeout)
        session_id = response_session or session_id
        response = response_for_id(messages, request_id)
        results.append(
            {
                "uri": uri,
                "response": response,
                "extra_messages": [message for message in messages if message is not response],
                "non_json_events": non_json,
            }
        )
    return {
        "schema_version": "mcp-resource-read/1",
        "mode": "mcp_post",
        "url": url,
        "session_id_present": bool(session_id),
        "initialize_non_json_events": init_non_json,
        "initialized_non_json_events": initialized_non_json,
        "resources": results,
        "read_only": True,
        "write_methods_attempted": [],
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--url", help="MCP HTTP endpoint; only initialize/resources/read are sent")
    source.add_argument("--input", help="Captured JSON or SSE response; use '-' for stdin")
    parser.add_argument("--uri", action="append", dest="uris", help="MCP resource URI; repeatable with --url")
    parser.add_argument("--protocol-version", default="2025-03-26")
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        if args.input is not None:
            if args.input == "-":
                text = sys.stdin.read()
            else:
                text = Path(args.input).read_text(encoding="utf-8-sig", errors="replace")
            messages, non_json = parse_response(text.encode("utf-8"), "text/event-stream")
            result = {
                "schema_version": "mcp-resource-read/1",
                "mode": "parse_sse",
                "messages": messages,
                "non_json_events": non_json,
                "event_count": len(parse_sse_text(text)),
                "read_only": True,
                "write_methods_attempted": [],
            }
        else:
            uris = args.uris or []
            if not uris:
                raise ValueError("--uri is required with --url")
            result = read_resources(args.url, uris, args.protocol_version, args.timeout)
    except (OSError, ValueError, RuntimeError) as exc:
        print(json.dumps({"error": str(exc), "read_only": True}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
