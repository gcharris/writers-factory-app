import os
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
from dotenv import load_dotenv

# Load environment variables explicitly if not already loaded
# This helps when running scripts directly that might not have loaded .env
load_dotenv()

class LLMService:
    def __init__(self):
        # Helper to get API key with a fallback to prevent initialization errors
        # if a key is missing, the client is created but will fail on request if key is needed.
        # Alternatively, we can make client creation lazy or conditional.
        # For now, we'll use a dummy key if missing to allow service init, 
        # but specific provider calls will fail if they try to use it.
        
        def get_key(env_var):
            return os.getenv(env_var, "missing-key")

        # Initialize OpenAI Client
        self.openai_client = AsyncOpenAI(
            api_key=get_key("OPENAI_API_KEY")
        )
        
        # Initialize Anthropic Client
        self.anthropic_client = AsyncAnthropic(
            api_key=get_key("ANTHROPIC_API_KEY")
        )
        
        # Initialize XAI (Grok) Client
        self.xai_client = AsyncOpenAI(
            api_key=get_key("XAI_API_KEY"),
            base_url="https://api.x.ai/v1"
        )

        # --- Chinese / Asian Tier (OpenAI Compatible) ---
        
        # DeepSeek
        self.deepseek_client = AsyncOpenAI(
            api_key=get_key("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )

        # Alibaba Qwen (DashScope)
        # Using International Endpoint
        self.qwen_client = AsyncOpenAI(
            api_key=get_key("QWEN_API_KEY"),
            base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
        )

        # Moonshot Kimi
        self.kimi_client = AsyncOpenAI(
            api_key=get_key("KIMI_API_KEY"),
            base_url="https://api.moonshot.cn/v1"
        )

        # Zhipu ChatGLM
        self.zhipu_client = AsyncOpenAI(
            api_key=get_key("ZHIPU_API_KEY"),
            base_url="https://open.bigmodel.cn/api/paas/v4"
        )
        
        # Tencent Hunyuan
        self.tencent_client = AsyncOpenAI(
            api_key=get_key("TENCENT_API_KEY"),
            base_url="https://api.hunyuan.cloud.tencent.com/v1"
        )

        # --- European Tier ---

        # Mistral AI
        self.mistral_client = AsyncOpenAI(
            api_key=get_key("MISTRAL_API_KEY"),
            base_url="https://api.mistral.ai/v1"
        )

        # --- Russian Tier ---

        # Yandex YandexGPT (Russian-native)
        # Uses IAM token or API key authentication
        self.yandex_client = AsyncOpenAI(
            api_key=get_key("YANDEX_API_KEY"),
            base_url="https://llm.api.cloud.yandex.net/foundationModels/v1"
        )

    async def generate_response(self, provider: str, model: str, system_role: str, prompt: str) -> str:
        try:
            # --- Big Three ---
            if provider == "openai":
                return await self._call_openai_compatible(self.openai_client, model, system_role, prompt)

            elif provider == "anthropic":
                response = await self.anthropic_client.messages.create(
                    model=model,
                    max_tokens=4096,
                    system=system_role,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.content[0].text

            elif provider == "xai":
                return await self._call_openai_compatible(self.xai_client, model, system_role, prompt)
            
            # --- Extended Roster ---
            elif provider == "deepseek":
                return await self._call_openai_compatible(self.deepseek_client, model, system_role, prompt)
                
            elif provider == "qwen":
                return await self._call_openai_compatible(self.qwen_client, model, system_role, prompt)
                
            elif provider == "kimi":
                return await self._call_openai_compatible(self.kimi_client, model, system_role, prompt)
                
            elif provider == "zhipu":
                return await self._call_openai_compatible(self.zhipu_client, model, system_role, prompt)
                
            elif provider == "tencent":
                return await self._call_openai_compatible(self.tencent_client, model, system_role, prompt)
                
            elif provider == "mistral":
                return await self._call_openai_compatible(self.mistral_client, model, system_role, prompt)

            elif provider == "yandex":
                return await self._call_yandex(model, system_role, prompt)

            else:
                return f"Error: Unknown provider '{provider}'"

        except Exception as e:
            return f"Error generating response from {provider}: {str(e)}"

    async def _call_openai_compatible(self, client: AsyncOpenAI, model: str, system_role: str, prompt: str) -> str:
        """
        Helper for all OpenAI-compatible endpoints to avoid code duplication.
        """
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_role},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

    async def _call_yandex(self, model: str, system_role: str, prompt: str) -> str:
        """
        Helper for Yandex YandexGPT API.

        Yandex uses a slightly different format but is mostly OpenAI-compatible.
        Model names: yandexgpt-lite, yandexgpt (pro), yandexgpt-32k

        Note: The full model URI format is:
        gpt://<folder_id>/yandexgpt-lite/latest

        For simplicity, we accept short names and the service routes appropriately.
        """
        # Yandex accepts OpenAI-compatible format through their completion endpoint
        response = await self.yandex_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_role},
                {"role": "user", "content": prompt}
            ],
            # Yandex-specific parameters
            max_tokens=4096,
            temperature=0.7
        )
        return response.choices[0].message.content
