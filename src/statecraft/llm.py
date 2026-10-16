"""
Multi-provider LLM Adapter with Deterministic Offline Simulator and Real Model Support.

Enables:
1. Zero-cost, 100% offline local testability and recruiter demos without needing API keys.
2. Production connectivity to OpenAI (ChatOpenAI) or Google Gemini (ChatGoogleGenerativeAI).
3. Realistic error simulation (for testing self-correction reflection and retry mechanisms).
"""

import os
import json
import re
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

try:
    from langchain_core.language_models.chat_models import BaseChatModel
    from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
except ImportError:
    BaseChatModel = Any
    AIMessage = Any
    BaseMessage = Any
    HumanMessage = Any
    SystemMessage = Any


class MockLLMEngine:
    """A deterministic, state-aware mock LLM engine.
    
    Simulates realistic agent behavior including:
    - Step 1: Initial draft with subtle bug
    - Step 2: Receiving evaluator critique and fixing the bug
    - Step 3: Complex routing classification
    - Step 4: Multi-agent specialized responses
    """
    
    def __init__(self):
        self.call_history: List[Dict[str, Any]] = []

    def invoke(self, prompt_text: str, context: Optional[Dict[str, Any]] = None) -> str:
        prompt_lower = prompt_text.lower()
        self.call_history.append({"prompt": prompt_text, "context": context or {}})

        # 1. Routing / Intent Classification
        if "classify" in prompt_lower or "route" in prompt_lower or "triage" in prompt_lower:
            search_target = ""
            if context and "query" in context:
                search_target = str(context["query"]).lower()
            else:
                query_match = re.search(r"query:\s*['\"](.*?)['\"]", prompt_text, re.IGNORECASE)
                if query_match:
                    search_target = query_match.group(1).lower()
                else:
                    search_target = prompt_lower
            
            if any(k in search_target for k in ["security", "vulnerability", "auth", "bypass", "exploit", "cve"]):
                return json.dumps({
                    "category": "security",
                    "complexity_score": 0.88,
                    "reasoning": "High-risk security query requiring strict audit and manual sign-off."
                })
            elif any(k in search_target for k in ["crash", "leak", "deadlock", "algorithm", "bug", "stack"]):
                return json.dumps({
                    "category": "technical",
                    "complexity_score": 0.75,
                    "reasoning": "Deep technical issue requiring comprehensive test generation."
                })
            elif any(k in search_target for k in ["invoice", "charge", "refund", "subscription", "billing", "pay"]):
                return json.dumps({
                    "category": "billing",
                    "complexity_score": 0.35,
                    "reasoning": "Standard customer billing inquiry with deterministic policy rules."
                })
            else:
                return json.dumps({
                    "category": "general",
                    "complexity_score": 0.20,
                    "reasoning": "Standard informational request suitable for fast-path caching."
                })

        # 2. Self-Correction Code Generation
        if any(k in prompt_lower for k in ["generate python code", "solve this coding task", "fix the code", "requirement:"]):
            # Check if there is an error critique provided in the prompt (Iteration >= 2)
            if "critique" in prompt_lower or "syntaxerror" in prompt_lower or "assertionerror" in prompt_lower or "fix" in prompt_lower:
                # Fixed version on retry
                return (
                    "```python\n"
                    "def calculate_moving_average(numbers: list[float], window_size: int) -> list[float]:\n"
                    "    \"\"\"Calculates moving average with full bounds check and zero-division protection.\"\"\"\n"
                    "    if not numbers or window_size <= 0:\n"
                    "        return []\n"
                    "    if window_size > len(numbers):\n"
                    "        return [sum(numbers) / len(numbers)]\n"
                    "    \n"
                    "    result = []\n"
                    "    window_sum = sum(numbers[:window_size])\n"
                    "    result.append(round(window_sum / window_size, 2))\n"
                    "    \n"
                    "    for i in range(window_size, len(numbers)):\n"
                    "        window_sum += numbers[i] - numbers[i - window_size]\n"
                    "        result.append(round(window_sum / window_size, 2))\n"
                    "    return result\n"
                    "```"
                )
            else:
                # First attempt: Introduce an intentional subtle bug (off-by-one or missing edge case)
                return (
                    "```python\n"
                    "def calculate_moving_average(numbers: list[float], window_size: int) -> list[float]:\n"
                    "    \"\"\"Calculates moving average - Initial Draft (contains deliberate edge-case bug).\"\"\"\n"
                    "    # Intentional bug for demo: Does not check window_size <= len(numbers) or empty list!\n"
                    "    result = []\n"
                    "    for i in range(len(numbers) - window_size): # BUG: should be range(len(numbers) - window_size + 1)\n"
                    "        window = numbers[i:i + window_size]\n"
                    "        result.append(round(sum(window) / window_size, 2))\n"
                    "    return result\n"
                    "```"
                )

        # 3. Unit Test Generation
        if "generate unit tests" in prompt_lower or "test suite" in prompt_lower:
            return (
                "```python\n"
                "def test_suite():\n"
                "    # Test 1: Standard window\n"
                "    assert calculate_moving_average([10, 20, 30, 40], 2) == [15.0, 25.0, 35.0], 'Failed standard moving average'\n"
                "    # Test 2: Window equals length\n"
                "    assert calculate_moving_average([5, 15], 2) == [10.0], 'Failed window equals length'\n"
                "    # Test 3: Empty input handling\n"
                "    assert calculate_moving_average([], 2) == [], 'Failed empty list test'\n"
                "    return True\n"
                "```"
            )

        # 4. Multi-Agent Supervisor / Worker synthesis
        if "researcher" in prompt_lower:
            return "Research Findings: Evaluated modern enterprise microservices. Primary security vulnerability vectors reside in token deserialization and unvalidated gateway redirects."
        if "writer" in prompt_lower or "engineer" in prompt_lower or "architect" in prompt_lower:
            return "Technical Specification: Implemented token signature verification with HMAC-SHA256, isolated tenant secrets, and bounded replay windows."
        if "auditor" in prompt_lower or "compliance" in prompt_lower:
            return "Security Audit: Static analysis passed with zero CVE warnings. Code compliance verified against OWASP Top 10 A01 (Broken Access Control)."

        # Fallback general response
        return f"MockLLM: Successfully analyzed prompt ({len(prompt_text)} chars) with deterministic output."


def get_llm(temperature: float = 0.0) -> Any:
    """Factory returning configured LLM or Deterministic Mock engine."""
    provider = os.getenv("LLM_PROVIDER", "mock").lower()

    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            try:
                from langchain_openai import ChatOpenAI
                model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
                return ChatOpenAI(model=model, temperature=temperature, api_key=api_key)
            except Exception as e:
                print(f"[Warning] Failed initializing ChatOpenAI ({e}). Falling back to MockLLM.")

    elif provider == "google":
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                model = os.getenv("GOOGLE_MODEL", "gemini-2.0-flash")
                return ChatGoogleGenerativeAI(model=model, temperature=temperature, google_api_key=api_key)
            except Exception as e:
                print(f"[Warning] Failed initializing ChatGoogleGenerativeAI ({e}). Falling back to MockLLM.")

    return MockLLMEngine()


def extract_code_block(text: str, language: str = "python") -> str:
    """Utility to extract clean code from markdown code fences."""
    pattern = rf"```{language}\s*(.*?)\s*```"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    # Check general fence
    match_general = re.search(r"```\s*(.*?)\s*```", text, re.DOTALL)
    if match_general:
        return match_general.group(1).strip()
    return text.strip()
