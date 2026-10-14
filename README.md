# prompt-dress

LLM에게 입히는 프롬프트 옷장. `{MODE:xxx}` 태그 하나로 검증된 한국어 시스템 프롬프트 프리셋을 치환하는 가벼운 래퍼.

**모델은 건드리지 않는다** — 파인튜닝 없이, 프롬프트 레벨에서만 동작. 어떤 OpenAI 호환 서버(omlx, LM Studio, vLLM 등)의 어떤 모델에나 붙는다.

## 유래

HuggingFace의 DavidAU "Turbo-Brilliance" 시리즈(27개 reasoning/instruct 모드를 파인튜닝으로 구운 GGUF 모델)에서 아이디어를 따와, 실용적인 것만 추려 한국어로 재구현했다. 그쪽과의 차이:

| | Turbo-Brilliance | prompt-dress |
|---|---|---|
| 프리셋 저장 위치 | 모델 가중치 내부 (파인튜닝) | `modes.md` 텍스트 파일 |
| 태그 인식 | 모델이 학습 | 스크립트가 치환 |
| 모델 호환 | 해당 GGUF만 | 전부 |
| 프리셋 수정 | 재학습 | 파일 편집 즉시 |

## 설치

```sh
git clone https://github.com/k-park/prompt-dress.git
cd prompt-dress
./install.sh   # ask → ~/bin, modes.md → ~/.config/llm-modes/
```

의존성: zsh, python3, curl. 대상 서버는 OpenAI `/v1/chat/completions` 호환이면 됨.

## 사용

```sh
ask "{MODE:coder} 이 함수 리팩터링해줘"
ask "{MODE:teacher} TCP와 UDP 차이"
ask "{MODE:review} <코드 붙여넣기>"

# 모델 지정
ask -m mlx-community--Qwen3.5-4B-MLX-4bit "{MODE:logic} 왜 이 아키텍처가 맞나?"

# 서버/키 오버라이드 (OpenAI 등 다른 백엔드)
ASK_BASE_URL=https://api.openai.com ASK_API_KEY=sk-... ASK_MODEL=gpt-5.4 ask "{MODE:business} 사업 아이디어 검토해줘"
```

태그 없이 그냥 쓰면 일반 챗 (`ask "안녕"`).

## 모드 카탈로그 (10종)

| 모드 | 용도 | 핵심 규칙 |
|---|---|---|
| `coder` | 코딩 | 요구 재진술 → 완결 코드, 의사코드 금지, 에러 처리 기본 포함 |
| `review` | 코드 리뷰 | 칭찬 생략, 심각도 태그, 수정 코드 조각, 미확정은 "확인 필요" |
| `logic` | 제1원리 분석 | 공리까지 환원 → 재구축, 반례 조건 제시 |
| `hyper` | MECE 구조 분석 | 3~5개 축 분해, 불확실성 표기, 3문장 요약 |
| `socrates` | 소크라테스 문답 | 답 대신 질문 3개, 대화로 좁혀감 |
| `spoon` | 5인 전문가 패널 | 즉석 페르소나 구성, 제안+리스크+수렴 |
| `brainstorm` | 브레인스토밍 | 3턴 진화 (발산→정교화→실행 계획) |
| `business` | 사업 전략 | 4축 분석, 검증 가능한 가설 + 싼 검증법 |
| `teacher` | 학습 설명 | 비유 먼저, 3문단마다 이해 점검 |
| `prompt` | 프롬프트 엔지니어링 | 의도 3해석, 시스템 프롬프트 초안 3개 |

## 모드 추가

`modes.md`에 블록 하나 추가하면 끝:

```markdown
[mynewmode]
당신은 ... (시스템 프롬프트 본문, 여러 줄 가능)
```

규칙: 블록은 `[모드명]` 헤더로 시작, 다음 `[` 헤더 전까지가 본문. `#` 주석과 빈 줄은 무시.

## 파일

- `ask` — 래퍼 스크립트 (태그 파싱 → 시스템 프롬프트 치환 → API 호출)
- `modes.md` — 프리셋 옷장
- `install.sh` — 설치 (심볼릭 링크 방식)

## 라이선스

MIT
