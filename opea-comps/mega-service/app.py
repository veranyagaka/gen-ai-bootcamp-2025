from fastapi import HTTPException
from comps.cores.proto.api_protocol import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionResponseChoice,
    ChatMessage,
    UsageInfo,
)
from comps.cores.mega.constants import ServiceType, ServiceRoleType
from comps import MicroService, ServiceOrchestrator
import os
import httpx
import json

LLM_SERVICE_HOST_IP = os.getenv("LLM_SERVICE_HOST_IP", "http://ollama-server")  # Use container name as host
LLM_SERVICE_PORT = os.getenv("LLM_SERVICE_PORT", 11434)  # Ollama's default port

class ExampleService:
    def __init__(self, host="0.0.0.0", port=8000):
        print('hello')
        os.environ["TELEMETRY_ENDPOINT"] = ""
        self.host = host
        self.port = port
        self.endpoint = "/v1/example-service"
        self.megaservice = ServiceOrchestrator()
        self.http_client = httpx.AsyncClient() #add httpx client

    def add_remote_service(self):
        llm = MicroService(
            name="llm",
            host=LLM_SERVICE_HOST_IP,
            port=LLM_SERVICE_PORT,
            endpoint="/api/generate",  # Ollama's generate endpoint
            use_remote_service=True,
            service_type=ServiceType.LLM,
        )
        self.megaservice.add(llm)

    def start(self):
        self.service = MicroService(
            self.__class__.__name__,
            service_role=ServiceRoleType.MEGASERVICE,
            host=self.host,
            port=self.port,
            endpoint=self.endpoint,
            input_datatype=ChatCompletionRequest,
            output_datatype=ChatCompletionResponse,
        )
        self.service.add_route(self.endpoint, self.handle_request, methods=["POST"])
        self.service.start()

    async def handle_request(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        try:
            # Format the request for Ollama
            ollama_request = {
                "model": request.model or "llama3.2:1b",  # or whatever default model you're using
                "prompt": request.messages,  # Ollama uses "prompt" not "messages"
                "stream": False,  # disable streaming for now
            }

            # Directly make an HTTP request to Ollama, bypassing the microservice orchestrator, to simplify
            url = f"{LLM_SERVICE_HOST_IP}:{LLM_SERVICE_PORT}/api/generate"
            response = await self.http_client.post(url, json=ollama_request) # use httpx client

            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            ollama_response = response.json()
            content = ollama_response.get("response", "No response content available")

            # Create the response
            response = ChatCompletionResponse(
                model=request.model or "example-model",
                choices=[
                    ChatCompletionResponseChoice(
                        index=0,
                        message=ChatMessage(role="assistant", content=content),
                        finish_reason="stop",
                    )
                ],
                usage=UsageInfo(prompt_tokens=0, completion_tokens=0, total_tokens=0),
            )

            return response

        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Ollama API Error: {e.response.text}")

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def close(self):
        await self.http_client.aclose()

example = ExampleService()
example.add_remote_service()
example.start()

# Add a cleanup function to close the httpx client.
import asyncio
import signal
async def shutdown(signal, loop):
    print(f"Received exit signal {signal.name}")
    print("Closing httpx client")
    await example.close()
    print("httpx client closed")
    loop.stop()

loop = asyncio.get_event_loop()
for signame in (signal.SIGINT, signal.SIGTERM):
    loop.add_signal_handler(signame, lambda: asyncio.create_task(shutdown(signame, loop)))

try:
    loop.run_forever()
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    loop.close()