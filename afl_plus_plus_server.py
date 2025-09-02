#!/usr/bin/env python3
"""
AFL++ 퍼징을 위한 FastMCP 서버
"""

from fastmcp import FastMCP
import subprocess
import os
import json
import time
import psutil
from datetime import datetime
from pathlib import Path

app = FastMCP("afl-plus-plus-server")

@app.tool()
def start_afl_fuzzing(target_binary: str, input_dir: str, output_dir: str = None) -> str:
    """AFL++ 퍼징을 시작합니다."""
    
    if output_dir is None:
        output_dir = f"afl_output_{int(time.time())}"
    
    try:
        # 입력 디렉토리 존재 확인
        if not os.path.exists(input_dir):
            return f"❌ 입력 디렉토리를 찾을 수 없습니다: {input_dir}"
        
        # 타겟 바이너리 존재 확인
        if not os.path.exists(target_binary):
            return f"❌ 타겟 바이너리를 찾을 수 없습니다: {target_binary}"
        
        # AFL++ 명령어 구성
        cmd = [
            "afl-fuzz",
            "-i", input_dir,
            "-o", output_dir,
            "--", target_binary
        ]
        
        # 백그라운드에서 실행
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        return f"""
🚀 AFL++ 퍼징 시작됨 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})

🎯 타겟 바이너리: {target_binary}
📂 입력 디렉토리: {input_dir}
📂 출력 디렉토리: {output_dir}
🆔 프로세스 ID: {process.pid}

💡 퍼징 상태 확인: get_fuzzing_status() 함수 사용
🔍 결과 확인: analyze_fuzzing_results() 함수 사용
⏹️ 퍼징 중지: stop_fuzzing() 함수 사용
        """.strip()
        
    except Exception as e:
        return f"❌ AFL++ 퍼징 시작 실패: {str(e)}"

@app.tool()
def get_fuzzing_status(output_dir: str) -> str:
    """현재 퍼징 상태를 확인합니다."""
    
    try:
        # AFL++ 상태 파일 읽기
        stats_file = os.path.join(output_dir, "fuzzer_stats")
        
        if not os.path.exists(stats_file):
            return f"❌ 퍼징 상태 파일을 찾을 수 없습니다: {stats_file}"
        
        stats = {}
        with open(stats_file, 'r') as f:
            for line in f:
                if ':' in line:
                    key, value = line.strip().split(':', 1)
                    stats[key.strip()] = value.strip()
        
        # 주요 통계 추출
        execs_done = stats.get('execs_done', 'N/A')
        execs_per_sec = stats.get('execs_per_sec', 'N/A')
        paths_total = stats.get('paths_total', 'N/A')
        paths_found = stats.get('paths_found', 'N/A')
        crashes = stats.get('crashes', 'N/A')
        hangs = stats.get('hangs', 'N/A')
        start_time = stats.get('start_time', 'N/A')
        
        # 실행 시간 계산
        if start_time != 'N/A':
            try:
                start_timestamp = int(start_time)
                elapsed_time = int(time.time()) - start_timestamp
                hours = elapsed_time // 3600
                minutes = (elapsed_time % 3600) // 60
                seconds = elapsed_time % 60
                elapsed_str = f"{hours}시간 {minutes}분 {seconds}초"
            except:
                elapsed_str = "N/A"
        else:
            elapsed_str = "N/A"
        
        return f"""
📊 AFL++ 퍼징 상태 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})

📂 출력 디렉토리: {output_dir}
⏱️ 실행 시간: {elapsed_str}

📈 실행 통계:
- 총 실행 횟수: {execs_done}
- 초당 실행 횟수: {execs_per_sec}
- 총 경로 수: {paths_total}
- 발견된 경로: {paths_found}

🚨 발견된 문제:
- 크래시: {crashes}
- 행: {hangs}

🔍 상세 분석: analyze_fuzzing_results() 함수 사용
        """.strip()
        
    except Exception as e:
        return f"❌ 상태 확인 실패: {str(e)}"

@app.tool()
def analyze_fuzzing_results(output_dir: str) -> str:
    """퍼징 결과를 분석합니다."""
    
    try:
        crashes_dir = os.path.join(output_dir, "crashes")
        hangs_dir = os.path.join(output_dir, "hangs")
        queue_dir = os.path.join(output_dir, "queue")
        
        # 크래시 파일 분석
        crashes = []
        if os.path.exists(crashes_dir):
            for file in os.listdir(crashes_dir):
                if file.startswith("id:"):
                    crashes.append(file)
        
        # 행 파일 분석
        hangs = []
        if os.path.exists(hangs_dir):
            for file in os.listdir(hangs_dir):
                if file.startswith("id:"):
                    hangs.append(file)
        
        # 큐 파일 분석
        queue_files = []
        if os.path.exists(queue_dir):
            for file in os.listdir(queue_dir):
                if file.startswith("id:"):
                    queue_files.append(file)
        
        # 플롯 파일 확인
        plot_file = os.path.join(output_dir, "plot_data")
        plot_data = []
        if os.path.exists(plot_file):
            with open(plot_file, 'r') as f:
                lines = f.readlines()
                if len(lines) > 1:
                    # 마지막 5개 데이터 포인트
                    for line in lines[-5:]:
                        parts = line.strip().split(',')
                        if len(parts) >= 4:
                            plot_data.append({
                                'time': parts[0],
                                'execs': parts[1],
                                'paths': parts[2],
                                'crashes': parts[3]
                            })
        
        return f"""
🔍 AFL++ 퍼징 결과 분석 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})

📂 출력 디렉토리: {output_dir}

📊 발견된 파일들:
- 크래시 파일: {len(crashes)}개
- 행 파일: {len(hangs)}개
- 큐 파일: {len(queue_files)}개

📈 최근 실행 통계:
{chr(10).join([f"- 시간: {data['time']}, 실행: {data['execs']}, 경로: {data['paths']}, 크래시: {data['crashes']}" for data in plot_data])}

💡 크래시 분석: analyze_crash_file() 함수 사용
🔄 바이너리 재현: reproduce_crash() 함수 사용
        """.strip()
        
    except Exception as e:
        return f"❌ 결과 분석 실패: {str(e)}"

@app.tool()
def analyze_crash_file(output_dir: str, crash_id: str) -> str:
    """특정 크래시 파일을 분석합니다."""
    
    try:
        crash_file = os.path.join(output_dir, "crashes", crash_id)
        
        if not os.path.exists(crash_file):
            return f"❌ 크래시 파일을 찾을 수 없습니다: {crash_file}"
        
        # 파일 크기 확인
        file_size = os.path.getsize(crash_file)
        
        # 파일 내용 분석 (바이너리 파일이므로 처음 100바이트만)
        with open(crash_file, 'rb') as f:
            content = f.read(100)
        
        # 바이너리 패턴 분석
        printable_chars = sum(1 for byte in content if 32 <= byte <= 126)
        null_bytes = content.count(0)
        
        # 파일 타입 추정
        if printable_chars > 80:
            file_type = "텍스트 파일"
        elif null_bytes > 50:
            file_type = "바이너리 파일 (널 바이트 많음)"
        else:
            file_type = "바이너리 파일"
        
        return f"""
🔍 크래시 파일 분석 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})

📁 크래시 파일: {crash_id}
📂 경로: {crash_file}
📏 파일 크기: {file_size} 바이트
📋 파일 타입: {file_type}

🔬 내용 분석:
- 처음 100바이트 중 출력 가능한 문자: {printable_chars}개
- 널 바이트: {null_bytes}개
- 바이너리 데이터 비율: {100 - printable_chars}%

💡 재현 테스트: reproduce_crash() 함수 사용
        """.strip()
        
    except Exception as e:
        return f"❌ 크래시 분석 실패: {str(e)}"

@app.tool()
def reproduce_crash(target_binary: str, crash_file: str) -> str:
    """크래시를 재현합니다."""
    
    try:
        # 타겟 바이너리 존재 확인
        if not os.path.exists(target_binary):
            return f"❌ 타겟 바이너리를 찾을 수 없습니다: {target_binary}"
        
        # 크래시 파일 존재 확인
        if not os.path.exists(crash_file):
            return f"❌ 크래시 파일을 찾을 수 없습니다: {crash_file}"
        
        # 크래시 재현 명령어
        cmd = [target_binary, crash_file]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # 시그널 정보 추가
        signal_info = ""
        if result.returncode < 0:
            signal_info = f" (시그널: {abs(result.returncode)})"
        
        return f"""
🔄 크래시 재현 결과 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})

🎯 타겟 바이너리: {target_binary}
📂 크래시 파일: {crash_file}

📊 실행 결과:
- 반환 코드: {result.returncode}{signal_info}
- 표준 출력: {len(result.stdout)} 문자
- 표준 오류: {len(result.stderr)} 문자

📝 표준 출력:
{result.stdout[:500] if result.stdout else '없음'}

📝 표준 오류:
{result.stderr[:500] if result.stderr else '없음'}

💡 크래시가 성공적으로 재현되었습니다!
        """.strip()
        
    except subprocess.TimeoutExpired:
        return f"""
⏰ 크래시 재현 타임아웃 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})

🎯 타겟 바이너리: {target_binary}
📂 크래시 파일: {crash_file}

💡 10초 타임아웃으로 인해 실행이 중단되었습니다.
이는 행(hang) 또는 무한 루프일 가능성이 있습니다.
        """.strip()
        
    except Exception as e:
        return f"❌ 크래시 재현 실패: {str(e)}"

@app.tool()
def stop_fuzzing(process_id: int = None) -> str:
    """퍼징을 중지합니다."""
    
    try:
        if process_id:
            # 특정 프로세스 종료
            try:
                process = psutil.Process(process_id)
                process.terminate()
                return f"✅ 프로세스 {process_id} 종료됨"
            except psutil.NoSuchProcess:
                return f"❌ 프로세스 {process_id}를 찾을 수 없습니다"
        else:
            # 모든 AFL++ 프로세스 종료
            killed_count = 0
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] == 'afl-fuzz' or (proc.info['cmdline'] and 'afl-fuzz' in proc.info['cmdline']):
                        proc.terminate()
                        killed_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            return f"✅ {killed_count}개의 AFL++ 퍼징 프로세스 종료됨"
            
    except Exception as e:
        return f"❌ 퍼징 중지 실패: {str(e)}"

@app.tool()
def list_fuzzing_processes() -> str:
    """현재 실행 중인 AFL++ 프로세스를 나열합니다."""
    
    try:
        afl_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
            try:
                if proc.info['name'] == 'afl-fuzz' or (proc.info['cmdline'] and 'afl-fuzz' in proc.info['cmdline']):
                    # 실행 시간 계산
                    create_time = datetime.fromtimestamp(proc.info['create_time'])
                    elapsed = datetime.now() - create_time
                    
                    afl_processes.append({
                        'pid': proc.info['pid'],
                        'cmdline': ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else 'N/A',
                        'elapsed': str(elapsed).split('.')[0]  # 마이크로초 제거
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if not afl_processes:
            return "📋 현재 실행 중인 AFL++ 프로세스가 없습니다."
        
        result = f"""
📋 실행 중인 AFL++ 프로세스 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})

"""
        
        for i, proc in enumerate(afl_processes, 1):
            result += f"""
{i}. 프로세스 ID: {proc['pid']}
   실행 시간: {proc['elapsed']}
   명령어: {proc['cmdline']}
"""
        
        return result.strip()
        
    except Exception as e:
        return f"❌ 프로세스 목록 조회 실패: {str(e)}"

if __name__ == "__main__":
    print("AFL++ MCP 서버를 시작합니다...")
    app.run()
