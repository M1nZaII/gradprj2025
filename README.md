# 서울 날씨 MCP 서버

FastMCP를 사용해서 만든 간단한 서울 날씨 정보 서버입니다.

## 기능

- 🌤️ **현재 날씨**: 서울의 현재 날씨 정보
- 📅 **5일 예보**: 서울의 5일 날씨 예보
- 💡 **생활 팁**: 날씨에 맞는 생활 팁 제공

## 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 서버 정보 확인
```bash
fastmcp inspect seoul_weather_server.py
```

**결과 예시:**
```
✓ Inspected server: seoul-weather-server
  Tools: 3
  Prompts: 0
  Resources: 0
  Templates: 0
  Report saved to: server-info.json
```

## 다양한 실행 모드

### 1. STDIO 모드 (Claude Desktop용)
```bash
python3 seoul_weather_server.py
```

**특징:**
- Claude Desktop과 통신하기 위한 기본 모드
- 표준 입출력을 통한 JSON-RPC 2.0 통신
- 백그라운드에서 실행되어 Claude의 요청을 처리

### 2. HTTP 모드 (웹 API)
```bash
fastmcp run seoul_weather_server.py --transport http --port 8000
```

**특징:**
- HTTP를 통한 REST API 제공
- `http://127.0.0.1:8000/mcp`에서 접근 가능
- 브라우저 직접 접근 시 406 오류 발생 (정상 - MCP 프로토콜 사용)

### 3. 개발 모드 (웹 인터페이스)
```bash
export PATH="$HOME/.local/bin:$PATH" && fastmcp dev seoul_weather_server.py
```

**특징:**
- 웹 기반 MCP Inspector 제공
- `http://localhost:6274`에서 접근 가능
- 도구들을 시각적으로 테스트할 수 있는 인터페이스
- 실시간 도구 실행 및 결과 확인

## Claude Desktop 통합

### MCP 설정
Claude Desktop 앱에서 다음 설정을 추가하세요:

```json
{
  "mcpServers": {
    "seoul-weather": {
      "command": "python3",
      "args": [
        "/Users/mjimj/Documents/GitHub/gradprj2025/seoul_weather_server.py"
      ],
      "env": {}
    }
  }
}
```

### 사용법
Claude에서 다음과 같이 테스트해보세요:
- "서울 날씨 알려줘"
- "서울 5일 예보 보여줘"
- "오늘 날씨에 맞는 팁 알려줘"

## 제공되는 도구들

서버가 실행되면 다음과 같은 도구들을 사용할 수 있습니다:

1. `get_seoul_weather()` - 서울 현재 날씨
2. `get_seoul_forecast()` - 서울 5일 예보  
3. `get_weather_tip()` - 날씨 생활 팁

## 예시 출력

### 현재 날씨
```
🌤️ 서울 날씨 정보 (2025년 01월 24일 14시 30분)

현재 날씨: 맑음 ☀️
기온: 22°C
체감 온도: 24°C
습도: 65%
풍속: 3.2 m/s
기압: 1013 hPa

오늘은 날씨가 좋네요! 외출하기 좋은 날씨입니다. 😊
```

### 5일 예보
```
📅 서울 5일 날씨 예보 (2025년 01월 24일)

🗓️ 오늘: 맑음 ☀️ (최고 25°C, 최저 18°C)
🗓️ 내일: 흐림 ☁️ (최고 23°C, 최저 16°C)
🗓️ 모레: 비 🌧️ (최고 20°C, 최저 15°C)
🗓️ 3일 후: 맑음 ☀️ (최고 26°C, 최저 19°C)
🗓️ 4일 후: 구름 많음 ⛅ (최고 24°C, 최저 17°C)

주말에는 날씨가 좋을 예정입니다! 🎉
```

## 문제 해결

### 1. FastMCP 모듈 오류
```bash
ModuleNotFoundError: No module named 'fastmcp'
```

**해결:**
```bash
pip3 install fastmcp --break-system-packages
```

### 2. uv 명령어 오류 (개발 모드)
```bash
spawn uv ENOENT
```

**해결:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
```

### 3. 포트 충돌
```bash
address already in use
```

**해결:**
```bash
pkill -f "fastmcp\|python.*seoul_weather_server"
```

## 참고

- 현재는 더미 데이터를 사용합니다
- 실제 날씨 API를 사용하려면 OpenWeatherMap API 키가 필요합니다
- FastMCP 2.11.3 버전을 사용합니다
- MCP 1.13.1 프로토콜을 지원합니다
