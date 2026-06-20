"""
LLM Client module for interacting with various language models.
"""

import os
import json
import time
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import logging
from dataclasses import dataclass

import openai
import anthropic
import google.generativeai as genai
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """Container for LLM response data."""
    text: str
    model: str
    prompt: str
    timestamp: float
    tokens_used: Optional[int] = None
    latency_ms: Optional[float] = None


class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    def generate_sql(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate SQL from a natural language prompt."""
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """Return the model name."""
        pass


class OpenAIClient(LLMClient):
    """Client for OpenAI models."""

    def __init__(
        self,
        model_name: str = "gpt-4",
        api_key: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 500,
    ):
        self.model_name = model_name
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.temperature = temperature
        self.max_tokens = max_tokens

        if not self.api_key:
            raise ValueError("OpenAI API key not found")

        openai.api_key = self.api_key
        self.client = openai.OpenAI(api_key=self.api_key)

    def generate_sql(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate SQL using OpenAI API."""
        start_time = time.time()

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an SQL generation assistant. Generate only valid SQL queries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
            )

            latency_ms = (time.time() - start_time) * 1000

            return LLMResponse(
                text=response.choices[0].message.content,
                model=self.model_name,
                prompt=prompt,
                timestamp=time.time(),
                tokens_used=response.usage.total_tokens,
                latency_ms=latency_ms,
            )

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    def get_model_name(self) -> str:
        return self.model_name


class AnthropicClient(LLMClient):
    """Client for Anthropic Claude models."""

    def __init__(
        self,
        model_name: str = "claude-3-opus-20240229",
        api_key: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 500,
    ):
        self.model_name = model_name
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.temperature = temperature
        self.max_tokens = max_tokens

        if not self.api_key:
            raise ValueError("Anthropic API key not found")

        self.client = anthropic.Anthropic(api_key=self.api_key)

    def generate_sql(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate SQL using Anthropic API."""
        start_time = time.time()

        try:
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                temperature=kwargs.get("temperature", self.temperature),
                system="You are an SQL generation assistant. Generate only valid SQL queries.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            latency_ms = (time.time() - start_time) * 1000

            return LLMResponse(
                text=response.content[0].text,
                model=self.model_name,
                prompt=prompt,
                timestamp=time.time(),
                tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                latency_ms=latency_ms,
            )

        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise

    def get_model_name(self) -> str:
        return self.model_name


class GoogleGeminiClient(LLMClient):
    """Client for Google Gemini models."""

    def __init__(
        self,
        model_name: str = "gemini-1.5-pro",
        api_key: Optional[str] = None,
        temperature: float = 0.2,
    ):
        self.model_name = model_name
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.temperature = temperature

        if not self.api_key:
            raise ValueError("Google API key not found")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)

    def generate_sql(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate SQL using Gemini API."""
        start_time = time.time()

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=kwargs.get("temperature", self.temperature),
                )
            )

            latency_ms = (time.time() - start_time) * 1000

            return LLMResponse(
                text=response.text,
                model=self.model_name,
                prompt=prompt,
                timestamp=time.time(),
                tokens_used=None,  # Gemini doesn't provide token count in the same way
                latency_ms=latency_ms,
            )

        except Exception as e:
            logger.error(f"Google Gemini API error: {e}")
            raise

    def get_model_name(self) -> str:
        return self.model_name


class HuggingFaceClient(LLMClient):
    """Client for Hugging Face models."""

    def __init__(
        self,
        model_name: str = "meta-llama/Llama-2-7b-chat-hf",
        temperature: float = 0.2,
        max_tokens: int = 500,
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
    ):
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.device = device

        logger.info(f"Loading model {model_name} on {device}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            device_map="auto" if device == "cuda" else None,
        )
        if device == "cpu":
            self.model.to(device)
        logger.info("Model loaded successfully")

    def generate_sql(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate SQL using Hugging Face model."""
        start_time = time.time()

        try:
            inputs = self.tokenizer(prompt, return_tensors="pt")
            if self.device == "cuda":
                inputs = {k: v.cuda() for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=kwargs.get("max_tokens", self.max_tokens),
                    temperature=kwargs.get("temperature", self.temperature),
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                )

            response_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            # Extract only the generated part after the prompt
            if prompt in response_text:
                response_text = response_text.split(prompt)[-1].strip()

            latency_ms = (time.time() - start_time) * 1000

            return LLMResponse(
                text=response_text,
                model=self.model_name,
                prompt=prompt,
                timestamp=time.time(),
                tokens_used=len(outputs[0]),
                latency_ms=latency_ms,
            )

        except Exception as e:
            logger.error(f"Hugging Face model error: {e}")
            raise

    def get_model_name(self) -> str:
        return self.model_name


class LLMClientFactory:
    """Factory class for creating LLM clients."""

    @staticmethod
    def create_client(
        model_name: str,
        deployment_mode: str = "api",
        **kwargs,
    ) -> LLMClient:
        """
        Create an LLM client based on model name and deployment mode.

        Args:
            model_name: Name of the model
            deployment_mode: "api" or "web" or "local"
            **kwargs: Additional arguments

        Returns:
            LLMClient instance
        """
        # Map model names to client classes
        openai_models = ["gpt-4", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
        anthropic_models = ["claude-3-opus", "claude-3-sonnet", "claude-2"]
        google_models = ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"]
        huggingface_models = ["meta-llama", "mistral", "mixtral", "qwen"]

        if any(model_name.startswith(m) for m in openai_models):
            return OpenAIClient(model_name, **kwargs)
        elif any(model_name.startswith(m) for m in anthropic_models):
            return AnthropicClient(model_name, **kwargs)
        elif any(model_name.startswith(m) for m in google_models):
            return GoogleGeminiClient(model_name, **kwargs)
        elif any(model_name.startswith(m) for m in huggingface_models):
            return HuggingFaceClient(model_name, **kwargs)
        else:
            raise ValueError(f"Unsupported model: {model_name}")