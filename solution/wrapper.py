"""YOUR mitigation + observability layer."""
from __future__ import annotations
import time
import re
from telemetry.logger import logger
from telemetry.redact import redact

def mitigate(call_next, question, config, context):
    # 1. Sanitize Input (Prompt Injection Defense)
    # Strip out lines starting with 'GHI CHU', 'GHI CHÚ' or similar text blocks 
    # to protect against the injection twist.
    sanitized_question = re.sub(r'(?i)ghi ch[uú].*$', '', question, flags=re.MULTILINE).strip()
    
    t0 = time.time()
    
    # 2. Call the Agent
    result = call_next(sanitized_question, config)
    
    latency_ms = int((time.time() - t0) * 1000)
    meta = result.get("meta", {})
    usage = meta.get("usage", {})
    tools_used = meta.get("tools_used", [])
    steps = result.get("steps", 0)
    
    # 3. Observability Logging
    logger.log_event("CALL", {
        "qid": context.get("qid"),
        "session_id": context.get("session_id"),
        "turn_index": context.get("turn_index"),
        "wall_ms": latency_ms,
        "latency_ms": meta.get("latency_ms", latency_ms),
        "usage": usage,
        "tools_used": tools_used,
        "steps": steps,
        "status": result.get("status"),
        "error": result.get("error")
    })
    
    # 4. Redact PII from Answer
    if result.get("answer"):
        result["answer"] = redact(result["answer"])
        
    return result
