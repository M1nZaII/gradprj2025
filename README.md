# AFL++ 하이브리드 MCP 서버

> AFL++ 퍼징을 위한 혁신적인 하이브리드 MCP 서버 시스템

## 🎯 프로젝트 개요

AFL++ 하이브리드 MCP 서버는 **원격 배포 가능성**과 **로컬 파일 시스템 접근성**을 모두 만족시키는 혁신적인 퍼징 솔루션입니다.

### 🌟 주요 특징

- **🚀 원격 배포**: 클라우드에서 배포하여 다른 사용자들이 쉽게 사용
- **💻 로컬 접근**: 실제 파일 시스템에 접근하여 정확한 AFL++ 퍼징 실행
- **🤖 에이전트 기반**: 로컬 에이전트와 원격 서버의 협력적 아키텍처
- **📊 실시간 모니터링**: 퍼징 진행 상황을 실시간으로 확인 가능
- **🔒 보안**: 안전한 통신 및 접근 제어

## 🏗️ 시스템 아키텍처

```
┌─────────────────┐    HTTP/WebSocket    ┌─────────────────┐
│   원격 MCP 서버  │ ←──────────────────→ │   로컬 에이전트  │
│  (클라우드)     │                      │  (사용자 PC)     │
└─────────────────┘                      └─────────────────┘
         │                                        │
         │                                        │
         ▼                                        ▼
┌─────────────────┐                      ┌─────────────────┐
│  AFL++ 제어     │                      │  AFL++ 실행     │
│  설정 관리      │                      │  파일 접근      │
│  결과 수집      │                      │  로컬 실행      │
└─────────────────┘                      └─────────────────┘
```

### 핵심 컴포넌트

1. **원격 MCP 서버 (FastMCP)**
   - 중앙 제어 및 조정
   - AFL++ 퍼징 작업 스케줄링
   - 로컬 에이전트와의 통신 관리
   - 퍼징 결과 수집 및 분석

2. **로컬 에이전트**
   - AFL++ 바이너리 실행
   - 로컬 파일 시스템 접근
   - 퍼징 결과 전송
   - 원격 서버와의 통신

## 🚀 빠른 시작

### 1. 원격 서버 배포

```bash
# 의존성 설치
pip install -r requirements.txt

# 서버 실행
python afl_plus_plus_server.py
```

### 2. 로컬 에이전트 설정

```bash
# 로컬 에이전트 실행 (별도 구현 필요)
python local_agent.py --server-url <원격서버URL>
```

### 3. MCP 클라이언트 연결

```json
// ~/.cursor/mcp_servers.json
{
  "afl-plus-plus-hybrid": {
    "command": "python",
    "args": ["afl_plus_plus_server.py"],
    "env": {}
  }
}
```

## 🛠️ 사용 가능한 도구

### 에이전트 관리
- `list_available_agents()` - 사용 가능한 로컬 에이전트 목록
- `register_local_agent(agent_id, agent_info)` - 로컬 에이전트 등록
- `unregister_local_agent(agent_id)` - 로컬 에이전트 제거

### 퍼징 제어
- `start_hybrid_fuzzing(target_binary, input_dir, output_dir, agent_id)` - 하이브리드 퍼징 시작
- `get_hybrid_fuzzing_status(session_id)` - 퍼징 상태 확인
- `stop_hybrid_fuzzing(session_id)` - 퍼징 중지
- `cleanup_fuzzing_session(session_id)` - 세션 정리

### 모니터링
- `list_fuzzing_sessions()` - 모든 퍼징 세션 목록
- `get_system_status()` - 시스템 전체 상태

## 📋 사용 예시

### 1. 에이전트 등록 및 퍼징 시작

```python
# 1. 사용 가능한 에이전트 확인
list_available_agents()

# 2. 로컬 에이전트 등록
register_local_agent("my-agent-001", '{"platform": "linux", "version": "1.0.0"}')

# 3. AFL++ 퍼징 시작
start_hybrid_fuzzing(
    target_binary="/home/user/target/program",
    input_dir="/home/user/inputs",
    output_dir="/home/user/outputs"
)
```

### 2. 퍼징 상태 모니터링

```python
# 퍼징 세션 목록 확인
list_fuzzing_sessions()

# 특정 세션 상태 확인
get_hybrid_fuzzing_status("session-uuid-here")

# 시스템 전체 상태 확인
get_system_status()
```

### 3. 퍼징 제어

```python
# 퍼징 중지
stop_hybrid_fuzzing("session-uuid-here")

# 세션 정리
cleanup_fuzzing_session("session-uuid-here")
```

## 🔧 기술적 세부사항

### 통신 프로토콜
- **WebSocket/HTTP**: 실시간 양방향 통신
- **JSON**: 구조화된 데이터 교환
- **세션 기반**: 안전한 퍼징 작업 관리

### 보안 기능
- **에이전트 인증**: 고유 ID 및 인증 토큰
- **세션 격리**: 퍼징 작업별 권한 관리
- **네트워크 보안**: HTTPS/WSS 암호화 통신

### 성능 최적화
- **비동기 처리**: 동시 다중 퍼징 작업 지원
- **상태 캐싱**: 빠른 응답을 위한 상태 정보 저장
- **리소스 관리**: 효율적인 메모리 및 CPU 사용

## 📁 프로젝트 구조

```
gradprj2025/
├── afl_plus_plus_server.py      # 하이브리드 MCP 서버 (원격)
├── server-info.json             # 서버 설정 및 도구 정보
├── requirements.txt             # Python 의존성
├── README.md                   # 프로젝트 문서
└── local_agent/                # 로컬 에이전트 (별도 구현)
    ├── local_agent.py         # 에이전트 메인 프로그램
    ├── afl_runner.py          # AFL++ 실행 엔진
    └── communicator.py        # 서버 통신 모듈
```

## 🚧 개발 로드맵

### Phase 1: 기본 인프라 ✅
- [x] 하이브리드 MCP 서버 구현
- [x] 에이전트 관리 시스템
- [x] 기본 퍼징 제어 기능

### Phase 2: 로컬 에이전트 구현 🚧
- [ ] 로컬 에이전트 프로그램
- [ ] AFL++ 실행 엔진
- [ ] 실시간 통신 모듈

### Phase 3: 고급 기능
- [ ] 다중 에이전트 지원
- [ ] 퍼징 작업 스케줄링
- [ ] 결과 분석 및 시각화

### Phase 4: 최적화 및 안정성
- [ ] 성능 최적화
- [ ] 오류 처리 및 복구
- [ ] 로깅 및 모니터링

## 🤝 기여하기

1. **Fork** 이 저장소
2. **Feature branch** 생성 (`git checkout -b feature/amazing-feature`)
3. **Commit** 변경사항 (`git commit -m 'Add amazing feature'`)
4. **Push** 브랜치 (`git push origin feature/amazing-feature`)
5. **Pull Request** 생성

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🔗 관련 링크

- [AFL++ 공식 저장소](https://github.com/AFLplusplus/AFLplusplus)
- [FastMCP 문서](https://github.com/fastmcp/fastmcp)
- [MCP 프로토콜](https://modelcontextprotocol.io/)

## 📞 지원 및 문의

- **이슈 리포트**: [GitHub Issues](https://github.com/your-username/gradprj2025/issues)
- **문의사항**: [Discussions](https://github.com/your-username/gradprj2025/discussions)
- **기여 가이드**: [CONTRIBUTING.md](CONTRIBUTING.md)

---

**⭐ 이 프로젝트가 도움이 되었다면 스타를 눌러주세요!**
