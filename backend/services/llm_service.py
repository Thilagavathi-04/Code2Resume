from typing import Iterator, Optional


class LLMError(Exception):
    pass


class GeminiProvider:
    def __init__(self, api_key: str, model: str, timeout: int):
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self._client = None

    def _get_client(self):
        if self._client is None:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self._client = genai.GenerativeModel(self.model)
        return self._client

    def generate(self, messages: list[dict], model: str = None) -> str:
        client = self._get_client()
        model_name = model or self.model
        if model_name != self.model:
            import google.generativeai as genai
            client = genai.GenerativeModel(model_name)

        contents = []
        system_instruction = None
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                system_instruction = content
            else:
                contents.append({"role": "user" if role == "user" else "model", "parts": [content]})

        if not contents:
            raise LLMError("No user messages provided")

        if system_instruction and contents:
            contents[0]["parts"][0] = f"[System: {system_instruction}]\n\n{contents[0]['parts'][0]}"

        gen_config = {"temperature": 0.3}
        response = client.generate_content(contents, generation_config=gen_config)

        if not response.text:
            raise LLMError("Gemini returned empty response")
        return response.text

    def generate_stream(self, messages: list[dict], model: str = None) -> Iterator[str]:
        client = self._get_client()
        model_name = model or self.model
        if model_name != self.model:
            import google.generativeai as genai
            client = genai.GenerativeModel(model_name)

        contents = []
        system_instruction = None
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                system_instruction = content
            else:
                contents.append({"role": "user" if role == "user" else "model", "parts": [content]})

        if not contents:
            raise LLMError("No user messages provided")

        if system_instruction and contents:
            contents[0]["parts"][0] = f"[System: {system_instruction}]\n\n{contents[0]['parts'][0]}"

        gen_config = {"temperature": 0.3}
        response = client.generate_content(contents, generation_config=gen_config, stream=True)

        for chunk in response:
            if chunk.text:
                yield chunk.text


class OllamaProvider:
    def __init__(self, base_url: str, model: str, timeout: int):
        self.base_url = base_url
        self.model = model
        self.timeout = timeout
        self._client = None

    def _get_client(self):
        if self._client is None:
            from ollama import Client
            self._client = Client(host=self.base_url, timeout=self.timeout)
        return self._client

    def generate(self, messages: list[dict], model: str = None) -> str:
        client = self._get_client()
        response = client.chat(
            model=model or self.model,
            messages=messages,
            options={"num_gpu": 99, "temperature": 0.3},
        )
        return response["message"]["content"]

    def generate_stream(self, messages: list[dict], model: str = None) -> Iterator[str]:
        client = self._get_client()
        stream = client.chat(
            model=model or self.model,
            messages=messages,
            stream=True,
            options={"num_gpu": 99, "temperature": 0.3},
        )
        for chunk in stream:
            if "message" in chunk and "content" in chunk["message"]:
                yield chunk["message"]["content"]


class LLMService:
    def __init__(
        self,
        gemini_api_key: Optional[str] = None,
        gemini_model: str = "gemini-2.0-flash",
        ollama_base_url: str = "http://localhost:11434",
        ollama_model: str = "qwen3:4b",
        timeout: int = 180,
    ):
        self.gemini = None
        if gemini_api_key:
            self.gemini = GeminiProvider(gemini_api_key, gemini_model, timeout)
        self.ollama = OllamaProvider(ollama_base_url, ollama_model, timeout)

    def generate_response(self, messages: list[dict], model: str = None) -> str:
        if self.gemini:
            try:
                result = self.gemini.generate(messages, model)
                print("[LLM] Response generated via Gemini")
                return result
            except Exception as e:
                print(f"[LLM] Gemini failed ({e}), falling back to Ollama")

        try:
            result = self.ollama.generate(messages, model)
            print("[LLM] Response generated via Ollama")
            return result
        except Exception as e:
            raise LLMError(f"Both providers failed. Ollama error: {e}")

    def generate_response_stream(self, messages: list[dict], model: str = None) -> Iterator[str]:
        if self.gemini:
            try:
                for chunk in self.gemini.generate_stream(messages, model):
                    yield chunk
                print("[LLM] Stream completed via Gemini")
                return
            except Exception as e:
                print(f"[LLM] Gemini stream failed ({e}), falling back to Ollama")

        try:
            for chunk in self.ollama.generate_stream(messages, model):
                yield chunk
            print("[LLM] Stream completed via Ollama")
        except Exception as e:
            raise LLMError(f"Both providers failed. Ollama error: {e}")


def create_llm_service() -> LLMService:
    from app.core.config import settings
    return LLMService(
        gemini_api_key=settings.GEMINI_API_KEY,
        gemini_model=settings.GEMINI_MODEL,
        ollama_base_url=settings.OLLAMA_BASE_URL,
        ollama_model=settings.OLLAMA_MODEL,
        timeout=settings.LLM_TIMEOUT,
    )


llm = None


def get_llm() -> LLMService:
    global llm
    if llm is None:
        llm = create_llm_service()
    return llm
