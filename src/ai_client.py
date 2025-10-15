import instructor
import json
from openai import OpenAI
from pydantic import BaseModel
from typing import Type, Optional, Dict, Any

class AIClient:
    """General client wrapper for handling OpenAI interactions that return structured responses."""
    def __init__(self, client: OpenAI):
        """Initialize by patching the provided OpenAI client with `instructor` to support structured Pydantic models."""
        # We now store both the patched and original clients
        self.instructor_client = instructor.patch(client)
        self.native_client = client

    def get_structured_response(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: Optional[Type[BaseModel]] = None,
        response_format_options: Optional[Dict[str, Any]] = None,
        model: str = "gpt-4o",
        max_retries: int = 1
    ) -> Any:
        """
        Perform a general AI call and return a structured response.
        This method supports two modes:
        1. Pydantic Model Mode: If `response_model` is provided, it uses `instructor` to
           validate the response against the Pydantic model.
        2. Native JSON Mode: If `response_format_options` is provided, it uses OpenAI's
           native JSON mode. `response_format_options` should be a dict like {"type": "json_object"}
           or the more advanced json_schema format.

        Args:
            system_prompt: Instruction that defines the AI's role and task.
            user_prompt: The specific input/data the AI should process.
            response_model: The Pydantic class defining the expected output (for instructor).
            response_format_options: The response_format dictionary for native OpenAI JSON mode.
            model: Which OpenAI model to use.
            max_retries: How many times `instructor` should retry if validation fails.

        Returns:
            An instance of the Pydantic model, or a dictionary if using native JSON mode.

        Raises:
            ValueError: If neither or both response format methods are specified.
            Exception: If the API call fails after all retries.
        """
        if not response_model and not response_format_options:
            raise ValueError("You must provide either 'response_model' or 'response_format_options'.")
        if response_model and response_format_options:
            raise ValueError("You cannot provide both 'response_model' and 'response_format_options'.")

        try:
            # Mode 1: Pydantic model with instructor
            if response_model:
                return self.instructor_client.chat.completions.create(
                    model=model,
                    response_model=response_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_retries=max_retries
                )
            # Mode 2: Native JSON format
            else:
                response = self.native_client.chat.completions.create(
                    model=model,
                    response_format=response_format_options,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                )
                # The native client returns a string that needs to be parsed
                return json.loads(response.choices[0].message.content)

        except Exception as e:
            print(f"  - [AI_CLIENT] CRITICAL ERROR during API call: {e}")
            raise