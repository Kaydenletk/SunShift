"""Notification service — generates hurricane alerts using Gemini API, Claude API, or templates."""
from __future__ import annotations

from backend.services.hurricane_shield import StormInfo, ThreatLevel


class AlertGenerator:
    def __init__(self, gemini_api_key: str = "", anthropic_api_key: str = "") -> None:
        self.gemini_api_key = gemini_api_key
        self.anthropic_api_key = anthropic_api_key

    async def generate_alert(self, storms: list[StormInfo], threat_level: ThreatLevel) -> str:
        """Generate a human-readable alert message for the given storms and threat level."""
        if not storms:
            return "No active storms. Hurricane Shield on standby."

        # Try Gemini first, then Claude, then template fallback
        if self.gemini_api_key:
            try:
                return await self._gemini_alert(storms, threat_level)
            except Exception:
                pass

        if self.anthropic_api_key:
            try:
                return await self._claude_alert(storms, threat_level)
            except Exception:
                pass

        return self._template_alert(storms, threat_level)

    async def _gemini_alert(self, storms: list[StormInfo], threat_level: ThreatLevel) -> str:
        import google.generativeai as genai

        genai.configure(api_key=self.gemini_api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")

        storm_desc = ", ".join(
            f"{s.name} (Category {s.category}, {s.wind_mph}mph)" for s in storms
        )

        response = model.generate_content(
            f"Generate a brief, calm alert for a small business owner in Tampa, FL. "
            f"Active storms: {storm_desc}. Threat level: {threat_level.value}. "
            f"Use plain language, no jargon. 2-3 sentences max. "
            f"Focus on what SunShift is doing to protect their data."
        )
        return response.text

    async def _claude_alert(self, storms: list[StormInfo], threat_level: ThreatLevel) -> str:
        import anthropic

        client = anthropic.AsyncAnthropic(api_key=self.anthropic_api_key)
        storm_desc = ", ".join(
            f"{s.name} (Category {s.category}, {s.wind_mph}mph)" for s in storms
        )

        message = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=200,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Generate a brief, calm alert for a small business owner in Tampa, FL. "
                        f"Active storms: {storm_desc}. Threat level: {threat_level.value}. "
                        "Use plain language, no jargon. 2-3 sentences max. "
                        "Focus on what SunShift is doing to protect their data."
                    ),
                }
            ],
        )
        return message.content[0].text

    def _template_alert(self, storms: list[StormInfo], threat_level: ThreatLevel) -> str:
        storm = storms[0]
        if threat_level in (ThreatLevel.HIGH, ThreatLevel.CRITICAL):
            return (
                f"{storm.name} (Category {storm.category}) is approaching Tampa Bay. "
                "Hurricane Shield is active — your data is being backed up to AWS Ohio. "
                "No action needed from you."
            )
        elif threat_level == ThreatLevel.MEDIUM:
            return (
                f"{storm.name} is in the region. Hurricane Shield is monitoring. "
                "We'll activate full protection if it gets closer."
            )
        else:
            return (
                f"{storm.name} is active but far from Tampa. No immediate risk. "
                "Hurricane Shield is on standby."
            )
