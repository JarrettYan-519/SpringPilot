from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatZhipuAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from sqlalchemy.orm import Session
from backend.models.system import UserConfig


PROVIDER_DEFAULTS = {
    "openai": {"model": "gpt-4o-mini", "base_url": None},
    "deepseek": {"model": "deepseek-chat", "base_url": "https://api.deepseek.com/v1"},
    "claude": {"model": "claude-sonnet-4-6", "base_url": None},
    "glm": {"model": "glm-4-flash", "base_url": None},
}


class AIService:
    def __init__(self, db: Session):
        self.db = db

    def _get_config(self, key: str) -> str | None:
        config = self.db.query(UserConfig).filter(UserConfig.key == key).first()
        return config.value if config else None

    def _build_llm(self, provider: str, api_key: str, base_url: str | None, model: str):
        if provider == "glm":
            return ChatZhipuAI(api_key=api_key, model=model)
        kwargs = {"api_key": api_key, "model": model}
        if base_url:
            kwargs["base_url"] = base_url
        return ChatOpenAI(**kwargs)

    def get_llm(self, scenario: str = "default"):
        """Load LLM for a given scenario from UserConfig. Falls back through providers."""
        provider = self._get_config(f"llm_provider_{scenario}") or self._get_config("llm_provider_default") or "openai"
        api_key = self._get_config(f"llm_api_key_{provider}")
        base_url = self._get_config(f"llm_base_url_{provider}") or PROVIDER_DEFAULTS.get(provider, {}).get("base_url")
        model = self._get_config(f"llm_model_{provider}") or PROVIDER_DEFAULTS.get(provider, {}).get("model", "gpt-4o-mini")

        if not api_key:
            raise ValueError(f"No API key configured for provider: {provider}")

        return self._build_llm(provider=provider, api_key=api_key, base_url=base_url, model=model)

    async def analyze_jd(self, jd_text: str, resume_text: str | None = None) -> dict:
        llm = self.get_llm("jd_analysis")
        system_prompt = """你是一位资深HR和技术面试官。分析职位描述(JD)，提取关键技能要求，
        如果提供了简历，给出匹配度分析和差距建议。用JSON格式返回：
        {
          "key_skills": ["技能1", "技能2"],
          "requirements": ["要求1", "要求2"],
          "match_analysis": "匹配度分析（如有简历）",
          "gaps": ["差距1", "差距2"],
          "suggestions": ["建议1", "建议2"]
        }"""
        user_content = f"职位描述：\n{jd_text}"
        if resume_text:
            user_content += f"\n\n我的简历：\n{resume_text}"

        response = await llm.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_content),
        ])
        import json, re
        text = response.content
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return {"raw": text}

    async def generate_interview_questions(self, position: str, jd_text: str, question_count: int = 10) -> list[str]:
        llm = self.get_llm("interview_gen")
        prompt = f"""为以下职位生成{question_count}道面试题（技术题和HR题各半），职位：{position}
        职位描述：{jd_text}
        直接返回问题列表，每行一个问题，不要编号。"""
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        questions = [q.strip() for q in response.content.strip().split("\n") if q.strip()]
        return questions[:question_count]

    async def mock_interview_reply(self, history: list[dict], user_answer: str) -> str:
        llm = self.get_llm("mock_interview")
        messages = [SystemMessage(content="""你是一位专业面试官，正在进行技术面试。
        根据候选人的回答，追问更深入的问题，或者给出简短的反馈后进入下一个问题。
        保持专业，语言简洁，每次回复不超过200字。""")]
        for msg in history:
            if msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
            else:
                messages.append(HumanMessage(content=msg["content"]))
        messages.append(HumanMessage(content=user_answer))
        response = await llm.ainvoke(messages)
        return response.content

    async def estimate_calories(self, food_description: str) -> int:
        llm = self.get_llm("diet")
        prompt = f"估算以下食物的热量（卡路里），只返回数字，不要单位：{food_description}"
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        try:
            return int(response.content.strip().replace(",", ""))
        except ValueError:
            return 0

    async def daily_advice(self, job_summary: str, fitness_summary: str) -> str:
        llm = self.get_llm("default")
        prompt = f"""根据以下数据，给出今天的综合建议（求职+健身），简洁有重点，200字以内。
        求职情况：{job_summary}
        健身情况：{fitness_summary}"""
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        return response.content
