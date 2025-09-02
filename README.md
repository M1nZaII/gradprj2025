# AFL++ MCP 서버

FastMCP를 사용해서 만든 AFL++ 퍼징 도구 MCP 서버입니다.

## 기능

- 🚀 **퍼징 시작**: AFL++ 퍼징 세션 시작
- 📊 **상태 모니터링**: 실시간 퍼징 상태 확인
- 🔍 **결과 분석**: 크래시, 행, 큐 파일 분석
- 🔄 **크래시 재현**: 발견된 크래시 재현 테스트
- ⏹️ **퍼징 제어**: 퍼징 프로세스 시작/중지
- 📋 **프로세스 관리**: 실행 중인 AFL++ 프로세스 목록

## 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. AFL++ 설치 (필수)
```bash
# macOS (Homebrew)
brew install afl-plus-plus

# Ubuntu/Debian
sudo apt-get install afl++

# 소스에서 빌드
git clone https://github.com/AFLplusplus/AFLplusplus.git
cd AFLplusplus
make
sudo make install
```

### 3. 서버 정보 확인
```bash
fastmcp inspect afl_plus_plus_server.py
```

**결과 예시:**
```
✓ Inspected server: afl-plus-plus-server
  Tools: 7
  Prompts: 0
  Resources: 0
  Templates: 0
  Report saved to: server-info.json
```

## 다양한 실행 모드

### 1. STDIO 모드 (Claude Desktop용)
```bash
python3 afl_plus_plus_server.py
```

**특징:**
- Claude Desktop과 통신하기 위한 기본 모드
- 표준 입출력을 통한 JSON-RPC 2.0 통신
- 백그라운드에서 실행되어 Claude의 요청을 처리

### 2. HTTP 모드 (웹 API)
```bash
fastmcp run afl_plus_plus_server.py --transport http --port 8000
```

**특징:**
- HTTP를 통한 REST API 제공
- `http://127.0.0.1:8000/mcp`에서 접근 가능
- 브라우저 직접 접근 시 406 오류 발생 (정상 - MCP 프로토콜 사용)

### 3. 개발 모드 (웹 인터페이스)
```bash
export PATH="$HOME/.local/bin:$PATH" && fastmcp dev afl_plus_plus_server.py
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
    "afl-plus-plus": {
      "command": "python3",
      "args": [
        "/Users/mjimj/Documents/GitHub/gradprj2025/afl_plus_plus_server.py"
      ],
      "env": {}
    }
  }
}
```

### 사용법
Claude에서 다음과 같이 테스트해보세요:
- "AFL++ 퍼징을 시작해줘"
- "퍼징 상태 확인해줘"
- "발견된 크래시 분석해줘"
- "크래시 재현해줘"

## 제공되는 도구들

### 1. `start_afl_fuzzing(target_binary, input_dir, output_dir)`
- AFL++ 퍼징을 시작합니다
- 타겟 바이너리와 입력 디렉토리를 지정하여 퍼징 세션 시작

### 2. `get_fuzzing_status(output_dir)`
- 현재 퍼징 상태를 확인합니다
- 실행 횟수, 초당 실행 횟수, 발견된 경로, 크래시 수 등 표시

### 3. `analyze_fuzzing_results(output_dir)`
- 퍼징 결과를 분석합니다
- 크래시, 행, 큐 파일 개수와 최근 실행 통계 제공

### 4. `analyze_crash_file(output_dir, crash_id)`
- 특정 크래시 파일을 분석합니다
- 파일 크기, 타입, 바이너리 패턴 분석

### 5. `reproduce_crash(target_binary, crash_file)`
- 크래시를 재현합니다
- 타겟 바이너리로 크래시 파일 실행하여 결과 확인

### 6. `stop_fuzzing(process_id)`
- 퍼징을 중지합니다
- 특정 프로세스 또는 모든 AFL++ 프로세스 종료

### 7. `list_fuzzing_processes()`
- 현재 실행 중인 AFL++ 프로세스를 나열합니다
- 프로세스 ID, 실행 시간, 명령어 정보 제공

## 사용 예시

### 퍼징 시작
```
🎯 타겟 바이너리: /path/to/target
📂 입력 디렉토리: /path/to/inputs
📂 출력 디렉토리: afl_output_1234567890
🆔 프로세스 ID: 12345
```

### 퍼징 상태 확인
```
📊 AFL++ 퍼징 상태 (2025-01-25 19:36:32)

📂 출력 디렉토리: afl_output_1234567890
⏱️ 실행 시간: 2시간 15분 30초

📈 실행 통계:
- 총 실행 횟수: 1,234,567
- 초당 실행 횟수: 1,234
- 총 경로 수: 1,000
- 발견된 경로: 850

🚨 발견된 문제:
- 크래시: 5
- 행: 2
```

### 크래시 분석
```
🔍 크래시 파일 분석 (2025-01-25 19:36:32)

📁 크래시 파일: id:000000,sig:11,src:000000,op:flip1,pos:0
📂 경로: afl_output_1234567890/crashes/id:000000,sig:11,src:000000,op:flip1,pos:0
📏 파일 크기: 1024 바이트
📋 파일 타입: 바이너리 파일

🔬 내용 분석:
- 처음 100바이트 중 출력 가능한 문자: 15개
- 널 바이트: 25개
- 바이너리 데이터 비율: 85%
```

## 문제 해결

### 1. AFL++ 명령어 오류
```bash
command not found: afl-fuzz
```

**해결:**
```bash
# AFL++ 설치 확인
which afl-fuzz

# 설치되지 않은 경우 설치
brew install afl-plus-plus  # macOS
sudo apt-get install afl++  # Ubuntu
```

### 2. psutil 모듈 오류
```bash
ModuleNotFoundError: No module named 'psutil'
```

**해결:**
```bash
pip3 install psutil --break-system-packages
```

### 3. 권한 오류
```bash
Permission denied
```

**해결:**
```bash
# 실행 권한 부여
chmod +x afl_plus_plus_server.py

# 타겟 바이너리 권한 확인
chmod +x /path/to/target
```

### 4. 메모리 부족
```bash
Out of memory
```

**해결:**
```bash
# AFL++ 메모리 제한 설정
export AFL_MEMORY_LIMIT=512

# 또는 퍼징 중지 후 재시작
stop_fuzzing()
```

## 보안 고려사항

### 1. 타겟 바이너리 검증
- 실행 전 타겟 바이너리의 안전성 확인
- 신뢰할 수 있는 소스에서만 다운로드

### 2. 환경 격리
- Docker 컨테이너 내에서 퍼징 실행 권장
- 시스템 리소스 모니터링

### 3. 결과 파일 관리
- 크래시 파일의 민감한 정보 확인
- 필요시 결과 파일 암호화

## 참고

- AFL++ 4.0 이상 버전 권장
- FastMCP 2.11.3 버전을 사용합니다
- MCP 1.13.1 프로토콜을 지원합니다
- 퍼징 결과는 `afl_output_*` 디렉토리에 저장됩니다
- 크래시 파일은 `crashes/` 하위 디렉토리에 저장됩니다
