#!/usr/bin/env python3
"""
AFL++ 퍼징을 위한 하이브리드 FastMCP 서버
원격 서버에서 로컬 에이전트와 통신하여 AFL++ 퍼징을 제어합니다.
"""

from fastmcp import FastMCP
import json
import time
import uuid
import os
from datetime import datetime
from typing import Dict, List, Optional
import asyncio
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastMCP("afl-plus-plus-hybrid-server")

# 전역 상태 관리
class HybridFuzzingManager:
    def __init__(self):
        self.agents: Dict[str, dict] = {}  # 등록된 에이전트들
        self.sessions: Dict[str, dict] = {}  # 퍼징 세션들
        self.agent_connections: Dict[str, bool] = {}  # 에이전트 연결 상태
        
    def register_agent(self, agent_id: str, agent_info: dict) -> bool:
        """로컬 에이전트를 등록합니다."""
        try:
            self.agents[agent_id] = {
                "id": agent_id,
                "info": agent_info,
                "registered_at": datetime.now().isoformat(),
                "last_heartbeat": datetime.now().isoformat(),
                "status": "active"
            }
            self.agent_connections[agent_id] = True
            logger.info(f"에이전트 등록됨: {agent_id}")
            return True
        except Exception as e:
            logger.error(f"에이전트 등록 실패: {e}")
            return False
    
    def unregister_agent(self, agent_id: str) -> bool:
        """로컬 에이전트를 제거합니다."""
        try:
            if agent_id in self.agents:
                del self.agents[agent_id]
                del self.agent_connections[agent_id]
                logger.info(f"에이전트 제거됨: {agent_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"에이전트 제거 실패: {e}")
            return False
    
    def create_session(self, agent_id: str, target_binary: str, input_dir: str, output_dir: str) -> str:
        """새로운 퍼징 세션을 생성합니다."""
        try:
            session_id = str(uuid.uuid4())
            self.sessions[session_id] = {
                "id": session_id,
                "agent_id": agent_id,
                "target_binary": target_binary,
                "input_dir": input_dir,
                "output_dir": output_dir,
                "status": "created",
                "created_at": datetime.now().isoformat(),
                "progress": {
                    "execs_done": 0,
                    "execs_per_sec": 0,
                    "paths_total": 0,
                    "paths_found": 0,
                    "crashes": 0,
                    "hangs": 0
                }
            }
            logger.info(f"세션 생성됨: {session_id}")
            return session_id
        except Exception as e:
            logger.error(f"세션 생성 실패: {e}")
            return None
    
    def update_session_status(self, session_id: str, status: str, progress: dict = None):
        """세션 상태를 업데이트합니다."""
        if session_id in self.sessions:
            self.sessions[session_id]["status"] = status
            if progress:
                self.sessions[session_id]["progress"].update(progress)
            self.sessions[session_id]["updated_at"] = datetime.now().isoformat()
            logger.info(f"세션 상태 업데이트: {session_id} -> {status}")
    
    def get_session(self, session_id: str) -> Optional[dict]:
        """세션 정보를 반환합니다."""
        return self.sessions.get(session_id)
    
    def list_sessions(self) -> List[dict]:
        """모든 세션 목록을 반환합니다."""
        return list(self.sessions.values())
    
    def cleanup_session(self, session_id: str) -> bool:
        """세션을 정리합니다."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"세션 정리됨: {session_id}")
            return True
        return False

# 전역 매니저 인스턴스
fuzzing_manager = HybridFuzzingManager()

# 에이전트 코드 생성 함수들
def generate_linux_agent(agent_name: str, server_url: str) -> str:
    """Linux용 에이전트 코드 생성"""
    return f'''#!/usr/bin/env python3
"""
{agent_name} - Linux용 AFL++ 로컬 에이전트
자동 생성된 에이전트입니다.
"""

import asyncio
import json
import logging
import signal
import sys
import uuid
import subprocess
import os
import requests
from pathlib import Path

class LocalAgent:
    def __init__(self, server_url: str, agent_id: str = None):
        self.server_url = server_url
        self.agent_id = agent_id or str(uuid.uuid4())
        self.afl_process = None
        self.running_sessions = {{}}
        self.shutdown_event = asyncio.Event()
        
        # 시그널 핸들러
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        logging.info(f"시그널 {{signum}} 수신, 종료 중...")
        self.shutdown_event.set()
    
    async def start(self):
        try:
            logging.info(f"에이전트 시작: {{self.agent_id}}")
            
            # AFL++ 설치 확인
            self._check_afl_installation()
            
            # 서버에 등록
            await self._register_with_server()
            
            # 메인 루프
            await self._main_loop()
            
        except Exception as e:
            logging.error(f"에이전트 실행 오류: {{e}}")
        finally:
            await self._cleanup()
    
    def _check_afl_installation(self):
        try:
            subprocess.run(["afl-fuzz", "--help"], capture_output=True, check=True)
            logging.info("AFL++ 설치 확인됨")
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError("AFL++가 설치되지 않았습니다. 'sudo apt-get install afl++' 또는 'brew install afl-plus-plus'로 설치하세요.")
    
    async def _register_with_server(self):
        try:
            response = requests.post(
                f"{{self.server_url}}/register_agent",
                json={{
                    "agent_id": self.agent_id,
                    "platform": "linux",
                    "capabilities": ["afl_fuzzing"]
                }},
                timeout=10
            )
            if response.status_code == 200:
                logging.info("서버에 등록 성공")
            else:
                logging.warning("서버 등록 실패")
        except Exception as e:
            logging.warning(f"서버 등록 실패: {{e}}")
    
    async def _main_loop(self):
        while not self.shutdown_event.is_set():
            try:
                # 간단한 하트비트
                await self._send_heartbeat()
                await asyncio.sleep(30)
            except Exception as e:
                logging.error(f"메인 루프 오류: {{e}}")
                await asyncio.sleep(5)
    
    async def _send_heartbeat(self):
        try:
            requests.post(
                f"{{self.server_url}}/heartbeat",
                json={{"agent_id": self.agent_id}},
                timeout=5
            )
        except Exception:
            pass
    
    async def _cleanup(self):
        if self.afl_process:
            self.afl_process.terminate()
        logging.info("에이전트 정리 완료")

async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="AFL++ 로컬 에이전트")
    parser.add_argument("--server-url", required=True, help="서버 URL")
    parser.add_argument("--agent-id", help="에이전트 ID")
    
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    
    agent = LocalAgent(args.server_url, args.agent_id)
    await agent.start()

if __name__ == "__main__":
    asyncio.run(main())
'''

def generate_macos_agent(agent_name: str, server_url: str) -> str:
    """macOS용 에이전트 코드 생성"""
    return f'''#!/usr/bin/env python3
"""
{agent_name} - macOS용 AFL++ 로컬 에이전트
자동 생성된 에이전트입니다.
"""

import asyncio
import json
import logging
import signal
import sys
import uuid
import subprocess
import os
import requests
from pathlib import Path

class LocalAgent:
    def __init__(self, server_url: str, agent_id: str = None):
        self.server_url = server_url
        self.agent_id = agent_id or str(uuid.uuid4())
        self.afl_process = None
        self.running_sessions = {{}}
        self.shutdown_event = asyncio.Event()
        
        # 시그널 핸들러
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        logging.info(f"시그널 {{signum}} 수신, 종료 중...")
        self.shutdown_event.set()
    
    async def start(self):
        try:
            logging.info(f"에이전트 시작: {{self.agent_id}}")
            
            # AFL++ 설치 확인
            self._check_afl_installation()
            
            # 서버에 등록
            await self._register_with_server()
            
            # 메인 루프
            await self._main_loop()
            
        except Exception as e:
            logging.error(f"에이전트 실행 오류: {{e}}")
        finally:
            await self._cleanup()
    
    def _check_afl_installation(self):
        try:
            subprocess.run(["afl-fuzz", "--help"], capture_output=True, check=True)
            logging.info("AFL++ 설치 확인됨")
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError("AFL++가 설치되지 않았습니다. 'brew install afl-plus-plus'로 설치하세요.")
    
    async def _register_with_server(self):
        try:
            response = requests.post(
                f"{{self.server_url}}/register_agent",
                json={{
                    "agent_id": self.agent_id,
                    "platform": "darwin",
                    "capabilities": ["afl_fuzzing"]
                }},
                timeout=10
            )
            if response.status_code == 200:
                logging.info("서버에 등록 성공")
            else:
                logging.warning("서버 등록 실패")
        except Exception as e:
            logging.warning(f"서버 등록 실패: {{e}}")
    
    async def _main_loop(self):
        while not self.shutdown_event.is_set():
            try:
                # 간단한 하트비트
                await self._send_heartbeat()
                await asyncio.sleep(30)
            except Exception as e:
                logging.error(f"메인 루프 오류: {{e}}")
                await asyncio.sleep(5)
    
    async def _send_heartbeat(self):
        try:
            requests.post(
                f"{{self.server_url}}/heartbeat",
                json={{"agent_id": self.agent_id}},
                timeout=5
            )
        except Exception:
            pass
    
    async def _cleanup(self):
        if self.afl_process:
            self.afl_process.terminate()
        logging.info("에이전트 정리 완료")

async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="AFL++ 로컬 에이전트")
    parser.add_argument("--server-url", required=True, help="서버 URL")
    parser.add_argument("--agent-id", help="에이전트 ID")
    
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    
    agent = LocalAgent(args.server_url, args.agent_id)
    await agent.start()

if __name__ == "__main__":
    asyncio.run(main())
'''

def generate_windows_agent(agent_name: str, server_url: str) -> str:
    """Windows용 에이전트 코드 생성"""
    return f'''#!/usr/bin/env python3
"""
{agent_name} - Windows용 AFL++ 로컬 에이전트
자동 생성된 에이전트입니다.
"""

import asyncio
import json
import logging
import signal
import sys
import uuid
import subprocess
import os
import requests
from pathlib import Path

class LocalAgent:
    def __init__(self, server_url: str, agent_id: str = None):
        self.server_url = server_url
        self.agent_id = agent_id or str(uuid.uuid4())
        self.afl_process = None
        self.running_sessions = {{}}
        self.shutdown_event = asyncio.Event()
    
    async def start(self):
        try:
            logging.info(f"에이전트 시작: {{self.agent_id}}")
            
            # AFL++ 설치 확인
            self._check_afl_installation()
            
            # 서버에 등록
            await self._register_with_server()
            
            # 메인 루프
            await self._main_loop()
            
        except Exception as e:
            logging.error(f"에이전트 실행 오류: {{e}}")
        finally:
            await self._cleanup()
    
    def _check_afl_installation(self):
        try:
            subprocess.run(["afl-fuzz", "--help"], capture_output=True, check=True)
            logging.info("AFL++ 설치 확인됨")
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError("AFL++가 설치되지 않았습니다. Windows용 AFL++를 설치하세요.")
    
    async def _register_with_server(self):
        try:
            response = requests.post(
                f"{{self.server_url}}/register_agent",
                json={{
                    "agent_id": self.agent_id,
                    "platform": "windows",
                    "capabilities": ["afl_fuzzing"]
                }},
                timeout=10
            )
            if response.status_code == 200:
                logging.info("서버에 등록 성공")
            else:
                logging.warning("서버 등록 실패")
        except Exception as e:
            logging.warning(f"서버 등록 실패: {{e}}")
    
    async def _main_loop(self):
        while not self.shutdown_event.is_set():
            try:
                # 간단한 하트비트
                await self._send_heartbeat()
                await asyncio.sleep(30)
            except Exception as e:
                logging.error(f"메인 루프 오류: {{e}}")
                await asyncio.sleep(5)
    
    async def _send_heartbeat(self):
        try:
            requests.post(
                f"{{self.server_url}}/heartbeat",
                json={{"agent_id": self.agent_id}},
                timeout=5
            )
        except Exception:
            pass
    
    async def _cleanup(self):
        if self.afl_process:
            self.afl_process.terminate()
        logging.info("에이전트 정리 완료")

async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="AFL++ 로컬 에이전트")
    parser.add_argument("--server-url", required=True, help="서버 URL")
    parser.add_argument("--agent-id", help="에이전트 ID")
    
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    
    agent = LocalAgent(args.server_url, args.agent_id)
    await agent.start()

if __name__ == "__main__":
    asyncio.run(main())
'''

def generate_requirements(platform: str) -> str:
    """플랫폼별 requirements.txt 생성"""
    base_reqs = "requests>=2.31.0"
    
    if platform == "windows":
        return base_reqs
    else:
        return f"{base_reqs}\\npsutil>=5.9.0"

def generate_run_script(platform: str, agent_name: str) -> str:
    """실행 스크립트 생성"""
    if platform == "windows":
        return f'''@echo off
echo {agent_name} 시작 중...
echo 사용법: run.bat <서버URL>
echo 예시: run.bat http://localhost:8000
echo.

if "%1"=="" (
    echo 서버 URL을 입력해주세요.
    echo 사용법: run.bat <서버URL>
    pause
    exit /b 1
)

set SERVER_URL=%1
echo 서버 URL: %SERVER_URL%
echo.

REM Python 설치 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo Python이 설치되지 않았습니다.
    pause
    exit /b 1
)

REM 의존성 설치
echo 의존성 설치 중...
pip install -r requirements.txt

REM 에이전트 실행
echo 에이전트 실행 중...
python local_agent.py --server-url "%SERVER_URL%"
pause
'''
    else:
        return f'''#!/bin/bash
echo "{agent_name} 시작 중..."
echo "사용법: ./run.sh <서버URL>"
echo "예시: ./run.sh http://localhost:8000"
echo ""

if [ $# -eq 0 ]; then
    echo "서버 URL을 입력해주세요."
    echo "사용법: ./run.sh <서버URL>"
    exit 1
fi

SERVER_URL=$1
echo "서버 URL: $SERVER_URL"
echo ""

# Python 설치 확인
if ! command -v python3 &> /dev/null; then
    echo "Python3가 설치되지 않았습니다."
    exit 1
fi

# 가상환경 생성 (선택사항)
if [ ! -d "venv" ]; then
    echo "가상환경 생성 중..."
    python3 -m venv venv
fi

# 가상환경 활성화
source venv/bin/activate

# 의존성 설치
echo "의존성 설치 중..."
pip install -r requirements.txt

# 에이전트 실행
echo "에이전트 실행 중..."
python3 local_agent.py --server-url "$SERVER_URL"
'''

def generate_readme(agent_name: str, platform: str) -> str:
    """README.md 생성"""
    return f"""# {agent_name}

AFL++ 로컬 에이전트 (자동 생성됨)

## 플랫폼
{platform}

## 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 에이전트 실행
```bash
python local_agent.py --server-url <서버URL>
```

### 3. 또는 실행 스크립트 사용
```bash
chmod +x run.sh
./run.sh <서버URL>
```

## 예시
```bash
python local_agent.py --server-url http://localhost:8000
```

## 주의사항
- AFL++가 시스템에 설치되어 있어야 합니다
- 서버 URL은 올바른 형식이어야 합니다
"""

@app.tool()
def generate_local_agent(
    agent_name: str = None,
    platform: str = None,
    output_dir: str = None
) -> str:
    """로컬 에이전트를 자동으로 생성합니다."""
    
    try:
        # 플랫폼 자동 감지 또는 사용자 지정
        if platform is None:
            import platform
            platform = platform.system().lower()
        
        # 에이전트 이름 설정
        if agent_name is None:
            agent_name = f"afl-agent-{int(time.time())}"
        
        # 출력 디렉토리 설정
        if output_dir is None:
            output_dir = f"./generated_agents/{agent_name}"
        
        # 디렉토리 생성
        os.makedirs(output_dir, exist_ok=True)
        
        # 플랫폼별 에이전트 코드 생성
        if platform == "linux":
            agent_code = generate_linux_agent(agent_name, "YOUR_SERVER_URL")
        elif platform == "darwin":  # macOS
            agent_code = generate_macos_agent(agent_name, "YOUR_SERVER_URL")
        elif platform == "windows":
            agent_code = generate_windows_agent(agent_name, "YOUR_SERVER_URL")
        else:
            agent_code = generate_linux_agent(agent_name, "YOUR_SERVER_URL")  # 기본값
        
        # 메인 에이전트 파일
        with open(f"{output_dir}/local_agent.py", "w") as f:
            f.write(agent_code)
        
        # requirements.txt
        with open(f"{output_dir}/requirements.txt", "w") as f:
            f.write(generate_requirements(platform))
        
        # 실행 스크립트
        script_file = f"{output_dir}/run.sh" if platform != "windows" else f"{output_dir}/run.bat"
        with open(script_file, "w") as f:
            f.write(generate_run_script(platform, agent_name))
        
        # README
        with open(f"{output_dir}/README.md", "w") as f:
            f.write(generate_readme(agent_name, platform))
        
        # 실행 권한 부여 (Linux/macOS)
        if platform != "windows":
            os.chmod(script_file, 0o755)
        
        return f"""
✅ 로컬 에이전트 생성 완료!

🤖 생성 위치: {output_dir}
🆔 에이전트 이름: {agent_name}
💻 플랫폼: {platform}

🚀 실행 방법:
cd {output_dir}

# 방법 1: 직접 실행
python3 local_agent.py --server-url <서버URL>

# 방법 2: 실행 스크립트 사용
chmod +x run.sh
./run.sh <서버URL>

💡 서버 URL 예시:
- HTTP: http://localhost:8000
- HTTPS: https://your-server.com
- WebSocket: ws://localhost:8000

⚠️ 주의: local_agent.py 파일에서 'YOUR_SERVER_URL'을 실제 서버 URL로 변경하세요!
        """.strip()
        
    except Exception as e:
        return f"❌ 에이전트 생성 실패: {str(e)}"

@app.tool()
def list_available_agents() -> str:
    """사용 가능한 로컬 에이전트 목록을 반환합니다."""
    try:
        agents = fuzzing_manager.agents
        if not agents:
            return "📋 등록된 로컬 에이전트가 없습니다.\n\n💡 로컬 에이전트를 실행하여 연결해주세요."
        
        result = "📋 등록된 로컬 에이전트 목록\n\n"
        for agent_id, agent_info in agents.items():
            status = "🟢 연결됨" if fuzzing_manager.agent_connections.get(agent_id, False) else "🔴 연결 끊김"
            result += f"🆔 {agent_id}\n"
            result += f"   상태: {status}\n"
            result += f"   등록 시간: {agent_info['registered_at']}\n"
            result += f"   마지막 연결: {agent_info['last_heartbeat']}\n"
            result += "─" * 40 + "\n"
        
        return result
    except Exception as e:
        return f"❌ 에이전트 목록 조회 실패: {str(e)}"

@app.tool()
def register_local_agent(agent_id: str, agent_info: str = "") -> str:
    """로컬 에이전트를 등록합니다."""
    try:
        info = json.loads(agent_info) if agent_info else {}
        if fuzzing_manager.register_agent(agent_id, info):
            return f"✅ 로컬 에이전트 등록 성공!\n\n🆔 에이전트 ID: {agent_id}\n📅 등록 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n💡 이제 start_hybrid_fuzzing() 함수를 사용하여 퍼징을 시작할 수 있습니다."
        else:
            return "❌ 로컬 에이전트 등록 실패"
    except Exception as e:
        return f"❌ 에이전트 등록 중 오류 발생: {str(e)}"

@app.tool()
def unregister_local_agent(agent_id: str) -> str:
    """로컬 에이전트를 제거합니다."""
    try:
        if fuzzing_manager.unregister_agent(agent_id):
            return f"✅ 로컬 에이전트 제거 성공!\n\n🆔 에이전트 ID: {agent_id}\n📅 제거 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        else:
            return f"❌ 에이전트를 찾을 수 없습니다: {agent_id}"
    except Exception as e:
        return f"❌ 에이전트 제거 중 오류 발생: {str(e)}"

@app.tool()
def start_hybrid_fuzzing(
    target_binary: str,
    input_dir: str,
    output_dir: str = None,
    agent_id: str = None
) -> str:
    """하이브리드 AFL++ 퍼징을 시작합니다."""
    try:
        # 에이전트 선택
        if agent_id is None:
            available_agents = [aid for aid, connected in fuzzing_manager.agent_connections.items() if connected]
            if not available_agents:
                return "❌ 연결된 로컬 에이전트가 없습니다.\n\n💡 먼저 로컬 에이전트를 실행하고 연결해주세요."
            agent_id = available_agents[0]
        
        # 에이전트 존재 확인
        if agent_id not in fuzzing_manager.agents:
            return f"❌ 에이전트를 찾을 수 없습니다: {agent_id}"
        
        # 에이전트 연결 상태 확인
        if not fuzzing_manager.agent_connections.get(agent_id, False):
            return f"❌ 에이전트가 연결되지 않았습니다: {agent_id}"
        
        # 출력 디렉토리 설정
        if output_dir is None:
            timestamp = int(time.time())
            output_dir = f"afl_output_{timestamp}"
        
        # 세션 생성
        session_id = fuzzing_manager.create_session(agent_id, target_binary, input_dir, output_dir)
        if not session_id:
            return "❌ 퍼징 세션 생성 실패"
        
        # 세션 상태를 시작으로 업데이트
        fuzzing_manager.update_session_status(session_id, "starting")
        
        result = f"""
🚀 하이브리드 AFL++ 퍼징 시작됨 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})

🆔 세션 ID: {session_id}
🤖 에이전트 ID: {agent_id}
🎯 타겟 바이너리: {target_binary}
📂 입력 디렉토리: {input_dir}
📂 출력 디렉토리: {output_dir}

💡 퍼징 상태 확인: get_hybrid_fuzzing_status("{session_id}")
⏹️ 퍼징 중지: stop_hybrid_fuzzing("{session_id}")
        """.strip()
        
        return result
        
    except Exception as e:
        return f"❌ 하이브리드 퍼징 시작 실패: {str(e)}"

@app.tool()
def get_hybrid_fuzzing_status(session_id: str) -> str:
    """하이브리드 퍼징 상태를 확인합니다."""
    try:
        session = fuzzing_manager.get_session(session_id)
        if not session:
            return f"❌ 세션을 찾을 수 없습니다: {session_id}"
        
        progress = session["progress"]
        status = session["status"]
        
        # 상태별 이모지
        status_emoji = {
            "created": "🆕",
            "starting": "🚀",
            "running": "🔄",
            "completed": "✅",
            "stopped": "⏹️",
            "error": "❌"
        }
        
        emoji = status_emoji.get(status, "❓")
        
        result = f"""
{emoji} 퍼징 세션 상태 ({session_id})

📊 상태: {status}
🤖 에이전트: {session['agent_id']}
🎯 타겟: {session['target_binary']}
📂 입력: {session['input_dir']}
📂 출력: {session['output_dir']}
📅 생성 시간: {session['created_at']}

📈 진행 상황:
   • 실행 횟수: {progress['execs_done']:,}
   • 초당 실행: {progress['execs_per_sec']:.1f}
   • 총 경로: {progress['paths_total']}
   • 발견된 경로: {progress['paths_found']}
   • 크래시: {progress['crashes']}
   • 행: {progress['hangs']}
        """.strip()
        
        return result
        
    except Exception as e:
        return f"❌ 퍼징 상태 조회 실패: {str(e)}"

@app.tool()
def list_fuzzing_sessions() -> str:
    """모든 퍼징 세션 목록을 반환합니다."""
    try:
        sessions = fuzzing_manager.list_sessions()
        if not sessions:
            return "📋 실행 중인 퍼징 세션이 없습니다."
        
        result = "📋 퍼징 세션 목록\n\n"
        for session in sessions:
            status_emoji = {
                "created": "🆕",
                "starting": "🚀",
                "running": "🔄",
                "completed": "✅",
                "stopped": "⏹️",
                "error": "❌"
            }
            emoji = status_emoji.get(session["status"], "❓")
            
            result += f"{emoji} 세션: {session['id'][:8]}...\n"
            result += f"   상태: {session['status']}\n"
            result += f"   에이전트: {session['agent_id']}\n"
            result += f"   타겟: {session['target_binary']}\n"
            result += f"   생성: {session['created_at']}\n"
            result += "─" * 40 + "\n"
        
        return result
        
    except Exception as e:
        return f"❌ 세션 목록 조회 실패: {str(e)}"

@app.tool()
def stop_hybrid_fuzzing(session_id: str) -> str:
    """하이브리드 퍼징을 중지합니다."""
    try:
        session = fuzzing_manager.get_session(session_id)
        if not session:
            return f"❌ 세션을 찾을 수 없습니다: {session_id}"
        
        if session["status"] in ["completed", "stopped", "error"]:
            return f"ℹ️ 세션이 이미 {session['status']} 상태입니다."
        
        # 세션 상태를 중지로 업데이트
        fuzzing_manager.update_session_status(session_id, "stopped")
        
        return f"""
⏹️ 퍼징 세션 중지됨

🆔 세션 ID: {session_id}
📅 중지 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🎯 타겟: {session['target_binary']}

💡 세션 정리: cleanup_fuzzing_session("{session_id}")
        """.strip()
        
    except Exception as e:
        return f"❌ 퍼징 중지 실패: {str(e)}"

@app.tool()
def cleanup_fuzzing_session(session_id: str) -> str:
    """퍼징 세션을 정리합니다."""
    try:
        if fuzzing_manager.cleanup_session(session_id):
            return f"✅ 퍼징 세션 정리 완료!\n\n🆔 세션 ID: {session_id}\n📅 정리 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        else:
            return f"❌ 세션을 찾을 수 없습니다: {session_id}"
    except Exception as e:
        return f"❌ 세션 정리 실패: {str(e)}"

@app.tool()
def get_system_status() -> str:
    """시스템 전체 상태를 확인합니다."""
    try:
        total_agents = len(fuzzing_manager.agents)
        connected_agents = sum(fuzzing_manager.agent_connections.values())
        total_sessions = len(fuzzing_manager.sessions)
        active_sessions = sum(1 for s in fuzzing_manager.sessions.values() if s["status"] in ["starting", "running"])
        
        result = f"""
📊 하이브리드 AFL++ 서버 상태

🤖 에이전트:
   • 총 등록: {total_agents}
   • 연결됨: {connected_agents}
   • 연결 끊김: {total_agents - connected_agents}

📋 퍼징 세션:
   • 총 세션: {total_sessions}
   • 활성 세션: {active_sessions}
   • 완료/중지: {total_sessions - active_sessions}

⏰ 서버 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """.strip()
        
        return result
        
    except Exception as e:
        return f"❌ 시스템 상태 조회 실패: {str(e)}"

@app.tool()
def install_local_agent_to_client(
    agent_name: str = None,
    install_dir: str = None
) -> str:
    """클라이언트 환경에 로컬 에이전트를 자동으로 설치합니다."""
    
    try:
        # 에이전트 이름 설정
        if agent_name is None:
            agent_name = f"afl-agent-{int(time.time())}"
        
        # 설치 디렉토리 설정
        if install_dir is None:
            install_dir = f"./afl_agents/{agent_name}"
        
        # 클라이언트 환경 감지 (MCP 클라이언트 정보 활용)
        client_info = get_client_environment_info()
        platform = client_info.get("platform", "unknown")
        
        # 플랫폼별 에이전트 코드 생성
        if platform == "darwin":  # macOS
            agent_code = generate_macos_agent(agent_name, "YOUR_SERVER_URL")
            script_name = "run.sh"
        elif platform == "linux":
            agent_code = generate_linux_agent(agent_name, "YOUR_SERVER_URL")
            script_name = "run.sh"
        elif platform == "win32":
            agent_code = generate_windows_agent(agent_name, "YOUR_SERVER_URL")
            script_name = "run.bat"
        else:
            # 기본값으로 Linux용 생성
            agent_code = generate_linux_agent(agent_name, "YOUR_SERVER_URL")
            script_name = "run.sh"
        
        # 설치 스크립트 생성 (클라이언트에서 실행)
        install_script = generate_install_script(platform, agent_name, install_dir, agent_code)
        
        return f"""
🚀 로컬 에이전트 자동 설치 준비 완료!

🤖 에이전트 이름: {agent_name}
💻 감지된 플랫폼: {platform}
📁 설치 위치: {install_dir}

📋 **설치 방법:**

1️⃣ **터미널에서 다음 명령어 실행:**
```bash
{install_script}
```

2️⃣ **또는 수동으로 파일 생성:**
   - `{install_dir}/local_agent.py` 생성
   - `{install_dir}/requirements.txt` 생성  
   - `{install_dir}/{script_name}` 생성

3️⃣ **에이전트 실행:**
```bash
cd {install_dir}
python3 local_agent.py --server-url <서버URL>
```

💡 **자동 설치 스크립트가 준비되었습니다!**
        """.strip()
        
    except Exception as e:
        return f"❌ 에이전트 설치 준비 실패: {str(e)}"

def get_client_environment_info() -> dict:
    """클라이언트 환경 정보를 가져옵니다."""
    try:
        import platform
        return {
            "platform": platform.system().lower(),
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
            "os_info": platform.platform()
        }
    except Exception:
        return {"platform": "unknown"}

def generate_install_script(platform: str, agent_name: str, install_dir: str, agent_code: str) -> str:
    """플랫폼별 설치 스크립트 생성"""
    
    if platform == "win32":
        return f'''@echo off
echo {agent_name} 설치 중...
echo.

REM 설치 디렉토리 생성
if not exist "{install_dir}" mkdir "{install_dir}"
cd "{install_dir}"

REM 에이전트 파일 생성
echo {agent_name} 파일 생성 중...
echo {agent_code.replace(chr(10), "\\n")} > local_agent.py

REM requirements.txt 생성
echo requests>=2.31.0 > requirements.txt

REM 실행 스크립트 생성
echo @echo off > run.bat
echo echo {agent_name} 시작 중... >> run.bat
echo python local_agent.py --server-url %%1 >> run.bat

echo.
echo ✅ 설치 완료!
echo.
echo 실행 방법:
echo   cd {install_dir}
echo   python local_agent.py --server-url <서버URL>
echo.
pause
'''
    else:
        return f'''#!/bin/bash
echo "{agent_name} 설치 중..."
echo ""

# 설치 디렉토리 생성
mkdir -p "{install_dir}"
cd "{install_dir}"

# 에이전트 파일 생성
echo "{agent_name} 파일 생성 중..."
cat > local_agent.py << 'EOF'
{agent_code}
EOF

# requirements.txt 생성
cat > requirements.txt << 'EOF'
requests>=2.31.0
psutil>=5.9.0
EOF

# 실행 스크립트 생성
cat > run.sh << 'EOF'
#!/bin/bash
echo "{agent_name} 시작 중..."
echo "사용법: ./run.sh <서버URL>"
echo "예시: ./run.sh http://localhost:8000"
echo ""

if [ $# -eq 0 ]; then
    echo "서버 URL을 입력해주세요."
    echo "사용법: ./run.sh <서버URL>"
    exit 1
fi

SERVER_URL=$1
echo "서버 URL: $SERVER_URL"
echo ""

# Python 설치 확인
if ! command -v python3 &> /dev/null; then
    echo "Python3가 설치되지 않았습니다."
    exit 1
fi

# 가상환경 생성 (선택사항)
if [ ! -d "venv" ]; then
    echo "가상환경 생성 중..."
    python3 -m venv venv
fi

# 가상환경 활성화
source venv/bin/activate

# 의존성 설치
echo "의존성 설치 중..."
pip install -r requirements.txt

# 에이전트 실행
echo "에이전트 실행 중..."
python3 local_agent.py --server-url "$SERVER_URL"
EOF

# 실행 권한 부여
chmod +x run.sh

echo ""
echo "✅ 설치 완료!"
echo ""
echo "실행 방법:"
echo "  cd {install_dir}"
echo "  python3 local_agent.py --server-url <서버URL>"
echo "  또는"
echo "  ./run.sh <서버URL>"
echo ""
'''

@app.tool()
def get_agent_install_guide(platform: str = None) -> str:
    """특정 플랫폼용 에이전트 설치 가이드를 제공합니다."""
    
    try:
        if platform is None:
            platform = "auto"
        
        if platform == "auto":
            platform = get_client_environment_info().get("platform", "linux")
        
        guides = {
            "linux": """
🐧 **Linux 환경 설치 가이드**

1️⃣ **AFL++ 설치:**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install afl++

# CentOS/RHEL
sudo yum install afl-plus-plus

# 소스에서 빌드
git clone https://github.com/AFLplusplus/AFLplusplus.git
cd AFLplusplus
make
sudo make install
```

2️⃣ **Python 의존성 설치:**
```bash
pip3 install requests psutil
```

3️⃣ **에이전트 실행:**
```bash
python3 local_agent.py --server-url <서버URL>
```
""",
            "darwin": """
🍎 **macOS 환경 설치 가이드**

1️⃣ **AFL++ 설치:**
```bash
# Homebrew 사용
brew install afl-plus-plus

# 또는 소스에서 빌드
git clone https://github.com/AFLplusplus/AFLplusplus.git
cd AFLplusplus
make
sudo make install
```

2️⃣ **Python 의존성 설치:**
```bash
pip3 install requests psutil
```

3️⃣ **에이전트 실행:**
```bash
python3 local_agent.py --server-url <서버URL>
```
""",
            "win32": """
🪟 **Windows 환경 설치 가이드**

1️⃣ **AFL++ 설치:**
- [AFL++ Windows 빌드](https://github.com/AFLplusplus/AFLplusplus/releases)에서 다운로드
- 또는 WSL2에서 Linux 버전 사용

2️⃣ **Python 의존성 설치:**
```cmd
pip install requests psutil
```

3️⃣ **에이전트 실행:**
```cmd
python local_agent.py --server-url <서버URL>
```
"""
        }
        
        guide = guides.get(platform, guides["linux"])
        
        return f"""
📚 **{platform.upper()} 플랫폼 설치 가이드**

{guide}

💡 **자동 설치를 원한다면:**
install_local_agent_to_client() 함수를 사용하세요!
        """.strip()
        
    except Exception as e:
        return f"❌ 설치 가이드 생성 실패: {str(e)}"

if __name__ == "__main__":
    app.run()
