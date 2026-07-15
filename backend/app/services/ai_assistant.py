"""
AI-powered Weather Assistant.

Design goal: the feature must work with zero configuration. A deterministic,
fully-tested rule-based engine is the source of truth for the recommendation
label; an LLM (Groq or OpenAI, if a key is configured) is only used to
phrase a friendlier natural-language answer around that same verdict. This
means the assistant is testable, explainable, and never silently broken by
a missing/invalid API key.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.core.config import get_settings

settings = get_settings()


@dataclass
class WeatherSnapshot:
    temperature: float | None = None  # Celsius
    feels_like: float | None = None
    humidity: float | None = None  # %
    wind_speed: float | None = None  # m/s
    uv_index: float | None = None
    visibility: float | None = None  # km
    pop: float | None = None  # probability of precipitation, %
    weather_condition: str | None = None


class RuleBasedWeatherAssistant:
    """Deterministic recommendation engine — always available, no API key needed."""

    RAIN_KEYWORDS = {"rain", "drizzle", "thunderstorm", "shower"}
    SEVERE_KEYWORDS = {"thunderstorm", "tornado", "squall", "hurricane"}

    def answer(self, question: str, snapshot: WeatherSnapshot) -> dict:
        question_lower = question.lower()
        reasoning: list[str] = []

        condition = (snapshot.weather_condition or "").lower()
        is_rainy = any(k in condition for k in self.RAIN_KEYWORDS) or (
            snapshot.pop is not None and snapshot.pop >= 40
        )
        is_severe = any(k in condition for k in self.SEVERE_KEYWORDS)
        is_hot = snapshot.temperature is not None and snapshot.temperature >= 33
        is_cold = snapshot.temperature is not None and snapshot.temperature <= 5
        is_windy = snapshot.wind_speed is not None and snapshot.wind_speed >= 10.8  # ~ Beaufort 6
        is_high_uv = snapshot.uv_index is not None and snapshot.uv_index >= 6
        is_humid = snapshot.humidity is not None and snapshot.humidity >= 80
        is_low_visibility = snapshot.visibility is not None and snapshot.visibility < 2

        if is_rainy:
            reasoning.append(
                f"Precipitation is likely (condition: {snapshot.weather_condition or 'n/a'}"
                + (f", {snapshot.pop:.0f}% chance" if snapshot.pop is not None else "")
                + ")."
            )
        if is_severe:
            reasoning.append("Severe weather conditions detected.")
        if is_hot:
            reasoning.append(f"High temperature ({snapshot.temperature:.0f}°C).")
        if is_cold:
            reasoning.append(f"Low temperature ({snapshot.temperature:.0f}°C).")
        if is_windy:
            reasoning.append(f"Strong winds ({snapshot.wind_speed:.1f} m/s).")
        if is_high_uv:
            reasoning.append(f"High UV index ({snapshot.uv_index:.0f}).")
        if is_humid:
            reasoning.append(f"High humidity ({snapshot.humidity:.0f}%).")
        if is_low_visibility:
            reasoning.append(f"Reduced visibility ({snapshot.visibility:.1f} km).")

        # --- Intent routing -------------------------------------------------
        if "umbrella" in question_lower or "rain" in question_lower:
            if is_rainy:
                answer = "Yes, carry an umbrella — rain is likely."
                rec = "unfavorable"
            else:
                answer = "No umbrella needed — no significant rain expected."
                rec = "favorable"

        elif "hik" in question_lower:
            if is_severe or is_rainy or is_hot or is_low_visibility:
                answer = "Tomorrow isn't ideal for hiking given the conditions."
                rec = "unfavorable"
            elif is_windy or is_high_uv:
                answer = "Hiking is possible, but take precautions."
                rec = "caution"
            else:
                answer = "Good conditions for a hike."
                rec = "favorable"

        elif "jog" in question_lower or "run" in question_lower:
            if is_severe or is_rainy:
                answer = "Better to skip jogging outdoors today."
                rec = "unfavorable"
            elif is_hot or is_high_uv or is_humid:
                answer = "You can jog, but go early/late and stay hydrated."
                rec = "caution"
            else:
                answer = "Great conditions for a jog."
                rec = "favorable"

        elif "postpone" in question_lower or "trip" in question_lower or "travel" in question_lower:
            if is_severe:
                answer = "Consider postponing — severe weather is expected."
                rec = "unfavorable"
            elif is_rainy or is_low_visibility:
                answer = "Travel is possible but build in extra time for delays."
                rec = "caution"
            else:
                answer = "No weather-related reason to postpone your trip."
                rec = "favorable"

        else:
            # Generic fallback: overall favorability summary.
            unfavorable_signals = sum([is_rainy, is_severe, is_hot, is_cold, is_low_visibility])
            if unfavorable_signals >= 2 or is_severe:
                answer = "Conditions look unfavorable for outdoor plans."
                rec = "unfavorable"
            elif unfavorable_signals == 1 or is_windy or is_high_uv:
                answer = "Conditions are workable, but plan around the caveats below."
                rec = "caution"
            else:
                answer = "Conditions look favorable for outdoor activities."
                rec = "favorable"

        if not reasoning:
            reasoning.append("No significant weather concerns detected.")

        return {"answer": answer, "recommendation": rec, "reasoning": reasoning}


class LLMWeatherAssistant:
    """Optional: phrases the rule-based verdict using an LLM for a more
    natural tone. Falls back to the rule-based engine on any failure."""

    def __init__(self):
        self.rule_based = RuleBasedWeatherAssistant()

    async def answer(self, question: str, snapshot: WeatherSnapshot) -> dict:
        base = self.rule_based.answer(question, snapshot)

        if settings.AI_PROVIDER == "groq" and settings.GROQ_API_KEY:
            try:
                return await self._phrase_with_groq(question, snapshot, base)
            except Exception:
                pass  # graceful degradation to rule-based
        elif settings.AI_PROVIDER == "openai" and settings.OPENAI_API_KEY:
            try:
                return await self._phrase_with_openai(question, snapshot, base)
            except Exception:
                pass

        base["source"] = "rule_based"
        return base

    async def _phrase_with_groq(self, question, snapshot, base) -> dict:
        import httpx

        prompt = self._build_prompt(question, snapshot, base)
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.GROQ_API_KEY}"},
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 200,
                    "temperature": 0.4,
                },
            )
            resp.raise_for_status()
            text = resp.json()["choices"][0]["message"]["content"].strip()
        return {**base, "answer": text, "source": "groq"}

    async def _phrase_with_openai(self, question, snapshot, base) -> dict:
        import httpx

        prompt = self._build_prompt(question, snapshot, base)
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 200,
                    "temperature": 0.4,
                },
            )
            resp.raise_for_status()
            text = resp.json()["choices"][0]["message"]["content"].strip()
        return {**base, "answer": text, "source": "openai"}

    @staticmethod
    def _build_prompt(question: str, snapshot: WeatherSnapshot, base: dict) -> str:
        return (
            "You are a concise weather assistant. A rule engine already determined the "
            f"verdict is '{base['recommendation']}' for reasons: {'; '.join(base['reasoning'])}. "
            f"User question: '{question}'. Weather snapshot: temp={snapshot.temperature}C, "
            f"feels_like={snapshot.feels_like}C, humidity={snapshot.humidity}%, "
            f"wind={snapshot.wind_speed}m/s, uv={snapshot.uv_index}, "
            f"condition={snapshot.weather_condition}. "
            "Respond in 1-2 short sentences, matching the verdict exactly — do not contradict it."
        )


def get_weather_assistant() -> LLMWeatherAssistant:
    return LLMWeatherAssistant()
