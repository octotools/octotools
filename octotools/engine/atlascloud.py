import base64
import json
import os
from typing import List, Union

import platformdirs
from openai import OpenAI

from .base import CachedEngine, EngineLM


ATLASCLOUD_DEFAULT_BASE_URL = "https://api.atlascloud.ai/v1"


class ChatAtlasCloud(EngineLM, CachedEngine):
    DEFAULT_SYSTEM_PROMPT = "You are a helpful, creative, and smart assistant."

    def __init__(
        self,
        model_string: str,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        is_multimodal: bool = False,
        use_cache: bool = False,
        **kwargs,
    ):
        api_key = os.getenv("ATLASCLOUD_API_KEY")
        if api_key is None:
            raise ValueError(
                "Please set the ATLASCLOUD_API_KEY environment variable to use "
                "Atlas Cloud models."
            )

        self.model_string = model_string.removeprefix("atlascloud/")
        self.system_prompt = system_prompt
        self.is_multimodal = is_multimodal
        self.use_cache = use_cache

        if self.use_cache:
            root = platformdirs.user_cache_dir("octotools")
            cache_model_string = self.model_string.replace("/", "_")
            super().__init__(
                cache_path=os.path.join(
                    root, f"cache_atlascloud_{cache_model_string}.db"
                )
            )

        self.client = OpenAI(
            api_key=api_key,
            base_url=os.getenv("ATLASCLOUD_API_BASE")
            or ATLASCLOUD_DEFAULT_BASE_URL,
            max_retries=0,
            **kwargs,
        )

    def generate(
        self,
        content: Union[str, List[Union[str, bytes]]],
        system_prompt=None,
        temperature=0,
        max_tokens=4000,
        top_p=0.99,
        **kwargs,
    ):
        if isinstance(content, list):
            if not self.is_multimodal:
                raise NotImplementedError(
                    "Multimodal generation is only supported when is_multimodal=True."
                )
            content = self._format_content(content)
        elif not isinstance(content, str):
            raise ValueError(f"Unsupported input type: {type(content)}")

        sys_prompt = system_prompt or self.system_prompt
        cache_key = sys_prompt + json.dumps(content, sort_keys=True)
        if self.use_cache:
            cached = self._check_cache(cache_key)
            if cached is not None:
                return cached

        response = self.client.chat.completions.create(
            model=self.model_string,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": content},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            **kwargs,
        )
        response_text = response.choices[0].message.content

        if self.use_cache:
            self._save_cache(cache_key, response_text)
        return response_text

    @staticmethod
    def _format_content(content: List[Union[str, bytes]]) -> List[dict]:
        formatted_content = []
        for item in content:
            if isinstance(item, bytes):
                encoded = base64.b64encode(item).decode("utf-8")
                formatted_content.append(
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{encoded}"},
                    }
                )
            elif isinstance(item, str):
                formatted_content.append({"type": "text", "text": item})
            else:
                raise ValueError(f"Unsupported input type: {type(item)}")
        return formatted_content

    def __call__(self, prompt, **kwargs):
        return self.generate(prompt, **kwargs)
