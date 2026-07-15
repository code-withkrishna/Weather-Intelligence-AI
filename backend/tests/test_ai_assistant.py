"""Unit tests for the rule-based weather assistant (no API key required)."""
from app.services.ai_assistant import RuleBasedWeatherAssistant, WeatherSnapshot

engine = RuleBasedWeatherAssistant()


def test_umbrella_question_says_yes_when_rainy():
    snapshot = WeatherSnapshot(weather_condition="Rain", pop=80)
    result = engine.answer("Should I carry an umbrella?", snapshot)
    assert result["recommendation"] == "unfavorable"
    assert "umbrella" in result["answer"].lower()


def test_umbrella_question_says_no_when_clear():
    snapshot = WeatherSnapshot(weather_condition="Clear", pop=5, temperature=25)
    result = engine.answer("Should I carry an umbrella?", snapshot)
    assert result["recommendation"] == "favorable"


def test_hiking_question_unfavorable_in_thunderstorm():
    snapshot = WeatherSnapshot(weather_condition="Thunderstorm", pop=90)
    result = engine.answer("Is tomorrow good for hiking?", snapshot)
    assert result["recommendation"] == "unfavorable"


def test_hiking_question_favorable_in_mild_weather():
    snapshot = WeatherSnapshot(
        weather_condition="Clear", temperature=22, wind_speed=3, uv_index=3, visibility=10
    )
    result = engine.answer("Is tomorrow good for hiking?", snapshot)
    assert result["recommendation"] == "favorable"


def test_jogging_caution_in_extreme_heat():
    snapshot = WeatherSnapshot(weather_condition="Clear", temperature=36, humidity=50)
    result = engine.answer("Can I go jogging today?", snapshot)
    assert result["recommendation"] == "caution"


def test_jogging_unfavorable_in_rain():
    snapshot = WeatherSnapshot(weather_condition="Rain", pop=70)
    result = engine.answer("Can I go jogging today?", snapshot)
    assert result["recommendation"] == "unfavorable"


def test_trip_postponement_unfavorable_in_severe_weather():
    snapshot = WeatherSnapshot(weather_condition="Tornado")
    result = engine.answer("Should I postpone my trip?", snapshot)
    assert result["recommendation"] == "unfavorable"


def test_trip_postponement_favorable_in_good_weather():
    snapshot = WeatherSnapshot(weather_condition="Clear", temperature=24, visibility=10)
    result = engine.answer("Should I postpone my trip?", snapshot)
    assert result["recommendation"] == "favorable"


def test_generic_question_falls_back_to_overall_summary():
    snapshot = WeatherSnapshot(weather_condition="Clouds", temperature=25)
    result = engine.answer("What's it like outside?", snapshot)
    assert result["recommendation"] in {"favorable", "caution", "unfavorable"}
    assert result["reasoning"]  # never empty


def test_reasoning_defaults_when_no_signals():
    snapshot = WeatherSnapshot()
    result = engine.answer("How's the weather?", snapshot)
    assert result["reasoning"] == ["No significant weather concerns detected."]
