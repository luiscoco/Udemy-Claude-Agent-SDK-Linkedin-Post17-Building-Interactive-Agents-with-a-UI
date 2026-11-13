"""Optional local UI: python ui.py (offline), or python ui.py --live."""
import argparse
import asyncio
import json
from pathlib import Path
import tempfile

from runtime import Agent, temporary_workspace

ROOT = Path(__file__).resolve().parent


def make_stream(live):
    async def stream(question):
        if not question.strip():
            yield 'Enter a question before submitting.'
            return
        with temporary_workspace(prefix='lesson16-ui-') as directory:
            output = Path(directory).resolve()
            assert output.is_relative_to(Path(tempfile.gettempdir()).resolve())
            fragments = asyncio.Queue()
            agent = Agent(ROOT, output, live=live, on_text=fragments.put_nowait)
            task = asyncio.create_task(agent.ask('ui_answer', 'Answer the supplied question concisely.', {'question': question},
                                                'An async iterator yields values over time; async for consumes them.', streaming=True))
            answer = ''
            try:
                while not task.done() or not fragments.empty():
                    try:
                        fragment = await asyncio.wait_for(fragments.get(), timeout=.1)
                    except asyncio.TimeoutError:
                        continue
                    answer += fragment
                    yield answer
                final = await task
                if not answer:
                    yield final
                # Complete text is deliberately not appended again.
            except Exception as error:
                yield answer + '\n\nIncomplete response: ' + type(error).__name__
            finally:
                if not task.done():
                    task.cancel()
                    await asyncio.gather(task, return_exceptions=True)
    return stream


if __name__ == '__main__':
    import gradio as gr
    parser = argparse.ArgumentParser()
    parser.add_argument('--live', action='store_true')
    args = parser.parse_args()
    gr.Interface(fn=make_stream(args.live), inputs=gr.Textbox(label='Your question'), outputs=gr.Markdown(),
                 title='Lesson 16: Interactive Question Desk', description='Offline fixtures by default. Each submission starts a fresh conversation.').queue().launch(server_name='127.0.0.1', share=False)
