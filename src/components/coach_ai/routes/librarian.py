# Import standard library modules
import asyncio
import json
import time
import traceback

# Import third-party library modules
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from langchain.callbacks.base import AsyncCallbackHandler
from sse_starlette.sse import EventSourceResponse

# Import local modules
from src.components.coach_ai.helpers.callback import NonStreamingLLMCallbackHandler, StreamingLLMCallbackHandler
from src.components.coach_ai.helpers.chat_history import get_librarian_chat_history
from src.components.coach_ai.helpers.logging import log
from src.components.coach_ai.helpers.messages import (
    bot_error_response,
    bot_process_step_response,
    bot_source_images_response,
    bot_sources_response,
    bot_stream_message_response,
    bot_suggestions_response,
    sender_token_response,
    user_stream_message_response,
)
from src.components.coach_ai.helpers.storage import find_and_return_source_images
from src.components.coach_ai.helpers.utils import (
    format_source_similarity_search_results,
    get_last_user_message,
    lowercase_user_roles,
)
from src.components.coach_ai.modules.common.chains.question_generator import suggest_follow_up_questions
from src.components.coach_ai.modules.common.chains.response_rewriter import rewrite_response_with_instruction
from src.components.coach_ai.modules.librarian.chains.answer_generator import answer_question_based_on_context
from src.components.coach_ai.modules.librarian.chains.document_retriever import (
    generate_context_from_documents,
    retrieve_source_documents,
)
from src.components.coach_ai.modules.librarian.chains.question_generator import rephrase_question_based_on_chat
from src.components.coach_ai.modules.librarian.utils.process_step import sources_found_callback
from src.components.coach_ai.modules.librarian.utils.response_rewriter import expand_rewrite_instruction
from src.components.coach_ai.schemas import ChatRequest, LibrarianRewriteResponseRequest, LinkRequest
from src.components.coach_ai.services.az_storage import (
    generate_blob_url,
    source_container_name,
    storage_container_name,
)
from src.components.coach_ai.services.openai import retry_chain_ainvoke
from src.components.coach_ai.settings import ModuleStoragePath

router = APIRouter()


async def answer_query(
    input: dict,
    question_handler: AsyncCallbackHandler,
    answer_handler: AsyncCallbackHandler,
    suggestion_handler: AsyncCallbackHandler,
    group_filter: str = "",
    process_step_dict: dict = {},
):
    # Rephrase the question based on chat history
    rephrased_question = asyncio.create_task(
        retry_chain_ainvoke(rephrase_question_based_on_chat(question_handler), input)
    )
    rephrased_question.add_done_callback(
        lambda fn: process_step_dict.update({"SEARCH_SOURCES": True})
    )

    # Retrieve related documents from vector store
    documents = asyncio.create_task(
        retrieve_source_documents.ainvoke(
            {
                "question": await rephrased_question,
                "group_filter": group_filter,
            }
        )
    )
    documents.add_done_callback(
        lambda fn: sources_found_callback(
            doc_list=documents.result(),
            process_step_dict=process_step_dict,
            key="SOURCES_FOUND_START_SYNTHESIZE",
        )
    )

    # Format documents into context for prompt
    context = asyncio.create_task(
        generate_context_from_documents.ainvoke(await documents)
    )

    # Answer the question based on context
    answer = asyncio.create_task(
        retry_chain_ainvoke(
            answer_question_based_on_context(answer_handler),
            {
                "question": await rephrased_question,
                "context": await context,
            },
        )
    )

    # Suggest follow-up questions based on additional context
    question_suggestions = asyncio.create_task(
        retry_chain_ainvoke(
            suggest_follow_up_questions(suggestion_handler),
            {"question": await rephrased_question, "answer": await answer},
        )
    )

    return {
        "question": await rephrased_question,
        "documents": await documents,
        "answer": await answer,
        "question_suggestions": await question_suggestions,
    }


@router.post("/api/knowledge-ai/chat", response_class=StreamingResponse)
async def chat(
    req_body: ChatRequest,
    req: Request,
):
    async def event_generator():
        email, group_ids = req.state.user_email, req.state.group_ids
        with log.contextualize(
            user=email, ip=req.client.host, method=req.method, path=req.url.path
        ):
            conversation = req_body.conversation
            last_user_message = get_last_user_message(conversation)
            chat_history = get_librarian_chat_history(req_body.conversationId)

            if group_ids is None:
                group_ids = []

            log.info("Sanitizing Group Ids", "api-librarian-chat")
            group_ids = lowercase_user_roles(group_ids=group_ids)
            group_filter = ",".join(group_ids)

            yield user_stream_message_response(last_user_message)
            try:
                yield sender_token_response(sender="you", message=last_user_message)
            except Exception as error:
                log.error(
                    message=str(error), instance_name="api-librarian-chat-tokencount"
                )
                traceback.print_exc()

            try:
                answer_handler = StreamingLLMCallbackHandler()

                start_time = time.time()

                logged_steps = set()
                process_step_dict = {
                    "SEARCH_SOURCES": False,
                    "SOURCES_FOUND_START_SYNTHESIZE": False,
                }
                msg_started_streaming = False
                yield bot_process_step_response("CREATE_EMBEDDINGS")
                answer_task_in_background = asyncio.create_task(
                    answer_query(
                        input={
                            "question": last_user_message,
                            "chat_history": chat_history,
                        },
                        question_handler=NonStreamingLLMCallbackHandler(),
                        answer_handler=answer_handler,
                        suggestion_handler=NonStreamingLLMCallbackHandler(),
                        group_filter=group_filter,
                        process_step_dict=process_step_dict,
                    )
                )

                while True:
                    if len(logged_steps) != len(process_step_dict):
                        for step, status in process_step_dict.items():
                            if status and step not in logged_steps:
                                if not isinstance(status, bool):
                                    step_with_value = json.dumps({step: status})
                                    yield bot_process_step_response(step_with_value)
                                else:
                                    yield bot_process_step_response(step)
                                logged_steps.add(step)

                    # If disconnected, exit
                    if await req.is_disconnected():
                        break
                    # While connected, stream output to UI
                    try:
                        data = answer_handler.queue.get_nowait()
                    except asyncio.queues.QueueEmpty:
                        await asyncio.sleep(0.1)
                        if not answer_handler.queue.empty():
                            continue
                        continue
                    # If answer stream is not yet done, keep on yielding
                    if data != "[DONE]":
                        if not msg_started_streaming:
                            msg_started_streaming = True
                            yield bot_process_step_response("START_STREAM_MSG")
                        yield bot_stream_message_response(data)
                    # If answer stream is done, await
                    else:
                        await answer_task_in_background
                        log.info(
                            f"Benchmark: Time Spent = {time.time() - start_time}",
                            "api-librarian-chat",
                        )
                        conversation.clear()

                        error = answer_task_in_background.exception()
                        if error:
                            yield bot_error_response(str(error))
                            break

                        result = answer_task_in_background.result()
                        source_files = result["documents"]
                        answer = result["answer"]
                        suggestions = result["question_suggestions"]

                        # Return source files and images
                        if len(source_files):
                            source_files_for_image_search = [
                                {
                                    "page": doc.metadata["page"],
                                    "source": doc.metadata["source"],
                                }
                                for doc in source_files
                            ]
                            formatted_source_images = find_and_return_source_images(
                                source_files=source_files_for_image_search,
                                source_image_path=ModuleStoragePath.LIBRARIAN.value,
                                answer=answer,
                                filter_explicit_sources=True,
                            )
                            yield bot_source_images_response(formatted_source_images)

                            formatted_source_files = (
                                format_source_similarity_search_results(source_files)
                            )
                            yield bot_sources_response(sources=formatted_source_files)

                        # Return suggestions
                        if len(suggestions):
                            yield bot_suggestions_response(suggestions=suggestions)

                        # Return token count
                        try:
                            yield sender_token_response(sender="bot", message=answer)
                        except Exception:
                            log.error("Token count failed", "api-librarian-chat")
                            traceback.print_exc()

                        # To end the SSE connection to the client frontend
                        yield json.dumps({"done": True})
                        break
            except asyncio.CancelledError as error:
                log.error(
                    message=f"Discounnected from client: {str(error)}",
                    instance_name="api-librarian-chat-stream",
                )
                yield bot_error_response(str(error))
            except Exception as error:
                log.error(message=str(error), instance_name="api-librarian-chat-stream")
                traceback.print_exc()
                yield bot_error_response(str(error))

    return EventSourceResponse(event_generator())


@router.post("/api/knowledge-ai/rewrite")
async def rewrite_response(
    req_body: LibrarianRewriteResponseRequest,
):
    try:
        callback_handler = NonStreamingLLMCallbackHandler()

        expanded_instruction = expand_rewrite_instruction(req_body.rewrite_instruction)
        rewritten_response = await asyncio.create_task(
            retry_chain_ainvoke(
                rewrite_response_with_instruction(callback_handler),
                {"message": req_body.message, "instruction": expanded_instruction},
            )
        )
        return rewritten_response
    except Exception as error:
        log.error(message=str(error), instance_name="api-librarian-rewrite-post")
        raise HTTPException(status_code=500, detail=str(error))


@router.post("/api/knowledge-ai/link")
async def generate_links(body: LinkRequest):
    try:
        return {
            source: generate_blob_url(source, source_container_name)
            for source in body.sources
        }
    except Exception as error:
        log.error(message=str(error), instance_name="api-librarian-link-post")
        raise HTTPException(status_code=500, detail=str(error))


@router.post("/api/knowledge-ai/storage-link")
async def generate_storage_links(body: LinkRequest):
    try:
        return {
            source: generate_blob_url(source, storage_container_name)
            for source in body.sources
        }
    except Exception as error:
        log.error(message=str(error), instance_name="api-librarian-storagelink-post")
        raise HTTPException(status_code=500, detail=str(error))
