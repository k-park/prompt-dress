#!/usr/bin/env python3
"""prompt-dress 품질 채점 — 각 모드가 프리셋 규칙을 실제로 따르는지 자동 검증.

답변의 '정확성'이 아니라 '프리셋 규칙 준수'를 측정한다:
각 모드에 고정 테스트 프롬프트를 보내고, 규칙에서 요구한 출력
마커(심각도 태그, 이해 점검, 축 분해 등)가 있는지 grep한다.

사용: python3 tests/quality_check.py [--base-url http://localhost:8000]
"""
import json
import re
import sys
import urllib.request

BASE = "http://localhost:8000"
MODEL = "mlx-community--Qwen3.6-35B-A3B-4bit"

# (모드, 테스트 프롬프트, [(마커 정규식, 설명), ...])
CASES = [
    ("review", "def f(x):\n    return eval(x)\n\n이 코드 검토해줘", [
        (r"\[(치명|중요|사소)\]", "심각도 태그"),
        (r"eval", "취약점 언급"),
    ]),
    ("teacher", "도커 컨테이너가 뭔지 설명해줘", [
        (r"이해 점검", "이해 점검 질문"),
        (r"예|비유|같이|처럼|말하면", "비유/구어 표현"),
    ]),
    ("hyper", "팀 채팅 도구를 Slack, Discord, Mattermost 중에 골라야 해", [
        (r"축|기준", "축 기반 분해"),
        (r"요약", "3문장 요약"),
    ]),
    ("logic", "아침마다 이메일 확인을 첫 업무로 하는 게 좋은 습관일까?", [
        (r"가정|전제|공리|제1원리|본질", "환원/전제 분석"),
        (r"결론|따라서|그러므로", "결론 도출"),
    ]),
    ("spoon", "슬로우 피드 서비스 창업 아이디어에 대해 의견줘", [
        (r"전문가|패널", "패널 구성"),
        (r"리스크|위험", "리스크 언급"),
    ]),
    ("brainstorm", "1인 개발자를 위한 새로운 할 일 관리 앱 아이디어", [
        (r"아이디어|아이디어:|\d+\.", "번호/아이디어 목록"),
        (r"새로|차별|독특|novel", "참신성 논의"),
    ]),
    ("translate", "The quick brown fox jumps over the lazy dog. Meeting notes: Synergy-driven deliverables will cascade to stakeholders by EOD.", [
        (r"역주|\(원어\)|\(", "용어 병기/역주"),
        (r"여우|개|이리", "번역 수행"),
    ]),
    ("search", "2026년 현재 가장 대중적인 분산형 SNS는 뭐야?", [
        (r"학습|모름|확인|알 수 없|한정", "불확실성 인정"),
        (r"검색어|검색:", "검색어 제안"),
    ]),
    ("coder", "파이썬으로 디렉토리 안의 중복 파일(같은 내용)을 찾는 함수 만들어줘", [
        (r"```", "코드 블록"),
        (r"def |import ", "완결 코드"),
    ]),
    ("business", "직장인 대상 점심 도시락 구독 서비스 사업성 검토해줘", [
        (r"시장|고객|경쟁|수익", "4축 분석"),
        (r"검증", "검증 방법"),
    ]),
]


def run_mode(mode: str, prompt: str) -> str:
    """ask 스크립트의 치환 로직과 동일하게 modes.md를 읽어 시스템 프롬프트 구성."""
    from pathlib import Path
    modes = Path(__file__).resolve().parent.parent / "modes.md"
    text = modes.read_text(encoding="utf-8")
    m = re.search(rf"^\[{mode}\]\n(.*?)(?=^\[|\Z)", text, re.M | re.S)
    system = "\n".join(
        l for l in m.group(1).splitlines()
        if l.strip() and not l.lstrip().startswith("#")
    ) if m else ""
    body = json.dumps({
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system} if system else None,
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 4000,
        "temperature": 0.6,
    }, ensure_ascii=False).replace(", null", "")
    req = urllib.request.Request(
        f"{BASE}/v1/chat/completions",
        data=body.encode(),
        headers={"Content-Type": "application/json", "Authorization": "Bearer local"},
    )
    d = json.load(urllib.request.urlopen(req, timeout=600))
    return d["choices"][0]["message"].get("content", "")


def main():
    if "--base-url" in sys.argv:
        base = sys.argv[sys.argv.index("--base-url") + 1]
        globals()["BASE"] = base
    total = passed = 0
    print(f"{'모드':<12} {'준수':<6} 마커")
    print("-" * 50)
    for mode, prompt, checks in CASES:
        try:
            out = run_mode(mode, prompt)
        except Exception as e:
            print(f"{mode:<12} ERROR  {e}")
            total += len(checks)
            continue
        results = []
        for pat, desc in checks:
            total += 1
            ok = re.search(pat, out) is not None
            passed += ok
            results.append(f"{'✓' if ok else '✗'}{desc}")
        print(f"{mode:<12} {sum('✓' in r for r in results)}/{len(results):<4} {' '.join(results)}")
    print("-" * 50)
    print(f"총 준수율: {passed}/{total} ({passed/total*100:.0f}%)")


if __name__ == "__main__":
    main()
