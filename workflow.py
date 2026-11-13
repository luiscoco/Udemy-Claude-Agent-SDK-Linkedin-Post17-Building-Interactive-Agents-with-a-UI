"""Lesson-specific workflow. Read this file before the execution adapter."""
from __future__ import annotations
import asyncio
import json
from pathlib import Path
from runtime import atomic_json, contained_path, in_process_tool

async def run(agent, data):
    question = data['question'].strip()
    if not question:
        raise ValueError('Enter a question before submitting')
    answer = await agent.ask('answer', 'Answer the user question clearly in at most three sentences.',
        {'question': question}, 'An async iterator produces values over time. Use async for to wait for each value.', streaming=True)
    return {'question': question, 'answer': answer, 'conversation': 'This submission is stateless.'}
