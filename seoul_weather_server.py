#!/usr/bin/env python3
"""
서울 날씨를 알려주는 간단한 FastMCP 서버
"""

from datetime import datetime
import platform
from fastmcp import FastMCP

# FastMCP 서버 인스턴스 생성
app = FastMCP("seoul-weather-server")


@app.tool()
def get_seoul_weather() -> str:
    """서울의 현재 날씨 정보를 가져옵니다."""
    try:
        # 더미 데이터 반환 (실제 API 키가 없으므로)
        current_time = datetime.now().strftime("%Y년 %m월 %d일 %H시 %M분")
        
        return f"""
🌤️ 서울 날씨 정보 ({current_time})

현재 날씨: 맑음 ☀️
기온: 22°C
체감 온도: 24°C
습도: 65%
풍속: 3.2 m/s
기압: 1013 hPa

오늘은 날씨가 좋네요! 외출하기 좋은 날씨입니다. 😊
        """.strip()
        
    except Exception as e:
        return f"날씨 정보를 가져오는 중 오류가 발생했습니다: {e}"


@app.tool()
def get_seoul_forecast() -> str:
    """서울의 5일 날씨 예보를 가져옵니다."""
    current_time = datetime.now().strftime("%Y년 %m월 %d일")
    
    return f"""
📅 서울 5일 날씨 예보 ({current_time})

🗓️ 오늘: 맑음 ☀️ (최고 25°C, 최저 18°C)
🗓️ 내일: 흐림 ☁️ (최고 23°C, 최저 16°C)
🗓️ 모레: 비 🌧️ (최고 20°C, 최저 15°C)
🗓️ 3일 후: 맑음 ☀️ (최고 26°C, 최저 19°C)
🗓️ 4일 후: 구름 많음 ⛅ (최고 24°C, 최저 17°C)

주말에는 날씨가 좋을 예정입니다! 🎉
        """.strip()


@app.tool()
def get_weather_tip() -> str:
    """현재 날씨에 맞는 생활 팁을 제공합니다."""
    return """
💡 오늘의 날씨 생활 팁

🌡️ 기온이 22°C로 쾌적합니다:
- 가벼운 겉옷만 걸치고 외출하세요
- 야외 활동하기 좋은 날씨입니다

☀️ 맑은 날씨:
- 자외선 차단제를 발라주세요
- 선글라스를 착용하는 것을 추천합니다

💨 바람이 약간 있습니다:
- 모자를 쓰면 좋겠어요
- 머리카락이 날릴 수 있으니 주의하세요

🚶‍♂️ 외출 추천:
- 공원 산책하기 좋은 날씨
- 카페 테라스에서 커피 마시기
- 쇼핑하기 좋은 날씨

즐거운 하루 되세요! 😊
        """.strip()


if __name__ == "__main__":
    print("서울 날씨 MCP 서버를 시작합니다...")
    app.run()
