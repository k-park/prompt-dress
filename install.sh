#!/bin/zsh
# prompt-dress 설치 — 심볼릭 링크 방식 (repo pull 시 자동 갱신)
set -e
SCRIPT_DIR="${0:A:h}"
mkdir -p "$HOME/bin" "$HOME/.config/llm-modes"

ln -sfn "$SCRIPT_DIR/ask" "$HOME/bin/ask"
ln -sfn "$SCRIPT_DIR/modes.md" "$HOME/.config/llm-modes/modes.md"

echo "설치 완료:"
echo "  ~/bin/ask → $SCRIPT_DIR/ask"
echo "  ~/.config/llm-modes/modes.md → $SCRIPT_DIR/modes.md"
echo ""
echo "테스트: ask \"{MODE:teacher} TCP와 UDP 차이\""
