#!/bin/bash
# vault_organizer.sh - 옵시디언 볼트 자동 정리 스크립트
# Inbox 파일을 키워드 기반으로 주제별 폴더로 이동하고 프론트매터를 추가합니다.

VAULT_DIR="/c/task/Obsidian_Vault/이근호/퇴직준비세미나_이근호"
INBOX="$VAULT_DIR/Inbox"
LOG_FILE="$VAULT_DIR/.claude/scripts/organizer_log.md"
TODAY=$(date +%Y-%m-%d)
MOVED_COUNT=0

# 로그 시작
echo "---" >> "$LOG_FILE"
echo "## 정리 실행: $TODAY $(date +%H:%M)" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Inbox에 파일이 있는지 확인
INBOX_FILES=$(find "$INBOX" -maxdepth 1 -type f -name "*.md" 2>/dev/null)
if [ -z "$INBOX_FILES" ]; then
    echo "- Inbox가 비어있습니다. 정리할 파일이 없습니다." >> "$LOG_FILE"
    echo ""
    echo "Inbox가 비어있습니다. 정리할 파일이 없습니다."
    exit 0
fi

# 분류 함수: 파일 내용을 읽고 키워드로 분류
classify_file() {
    local file="$1"
    local filename=$(basename "$file")
    local content=$(cat "$file" | tr '[:upper:]' '[:lower:]')
    local combined="$filename $content"

    # 키워드 매칭 (우선순위 순)
    if echo "$combined" | grep -qiE "기어박스|agma|kisssoft|감속기|하모닉|gear|기어설계"; then
        echo "Projects/기어박스_설계"
    elif echo "$combined" | grep -qiE "회전익기|동력전달|헬리콥터|helicopter|drivetrain"; then
        echo "Projects/회전익기_동력전달"
    elif echo "$combined" | grep -qiE "투자|포트폴리오|재무|연금|etf|주식|채권|smr|원자로"; then
        echo "Projects/투자_재무설계"
    elif echo "$combined" | grep -qiE "세미나|회차|과제|homework|공지"; then
        # 세미나 하위 분류
        if echo "$combined" | grep -qiE "과제|homework|제출"; then
            echo "Seminars/Homework"
        elif echo "$combined" | grep -qiE "공지|안내|일정"; then
            echo "Seminars/공지사항"
        else
            echo "Seminars"
        fi
    elif echo "$combined" | grep -qiE "가이드|사용법|설정|튜토리얼|guide|설치"; then
        echo "Guides"
    elif echo "$filename" | grep -qE "^[0-9]{4}-[0-9]{2}-[0-9]{2}"; then
        echo "Daily Notes"
    elif echo "$combined" | grep -qiE "번역_|요약_|논문|paper|참고문헌"; then
        echo "References"
    else
        echo "SKIP"  # 분류 불가 - Inbox에 유지
    fi
}

# 프론트매터 추가 함수
add_frontmatter() {
    local file="$1"
    local category="$2"
    local tags="$3"

    # 이미 프론트매터가 있는지 확인
    if head -1 "$file" | grep -q "^---"; then
        return  # 이미 있으면 스킵
    fi

    # 프론트매터 생성
    local temp_file=$(mktemp)
    cat > "$temp_file" << FRONTMATTER
---
created: $TODAY
tags: [$tags]
category: $category
status: 진행중
---

FRONTMATTER
    cat "$file" >> "$temp_file"
    mv "$temp_file" "$file"
}

# 카테고리별 태그 결정
get_tags() {
    local dest="$1"
    case "$dest" in
        Projects/기어박스_설계) echo "기어박스, 설계" ;;
        Projects/회전익기_동력전달) echo "회전익기, 동력전달" ;;
        Projects/투자_재무설계) echo "투자, 재무설계" ;;
        Seminars*) echo "세미나, 학습" ;;
        Guides) echo "가이드" ;;
        References) echo "참고자료" ;;
        "Daily Notes") echo "일일메모" ;;
        *) echo "미분류" ;;
    esac
}

get_category() {
    local dest="$1"
    case "$dest" in
        Projects/*) echo "프로젝트" ;;
        Seminars*) echo "세미나" ;;
        Guides) echo "가이드" ;;
        References) echo "참고자료" ;;
        "Daily Notes") echo "일일메모" ;;
        *) echo "기타" ;;
    esac
}

# 메인 처리: Inbox의 각 md 파일을 분류
echo "### 이동한 파일" >> "$LOG_FILE"
for file in $INBOX_FILES; do
    filename=$(basename "$file")
    dest=$(classify_file "$file")

    if [ "$dest" = "SKIP" ]; then
        echo "- \`$filename\` : 분류 불가 → Inbox에 유지" >> "$LOG_FILE"
        continue
    fi

    # 대상 폴더 확인/생성
    mkdir -p "$VAULT_DIR/$dest"

    # 프론트매터 추가
    tags=$(get_tags "$dest")
    category=$(get_category "$dest")
    add_frontmatter "$file" "$category" "$tags"

    # 파일 이동
    mv "$file" "$VAULT_DIR/$dest/"
    echo "- \`$filename\` : Inbox → \`$dest/\`" >> "$LOG_FILE"
    MOVED_COUNT=$((MOVED_COUNT + 1))
done

# 첨부파일 정리 (Inbox 내 이미지 등)
ATTACHMENT_FILES=$(find "$INBOX" -maxdepth 1 -type f \( -name "*.png" -o -name "*.jpg" -o -name "*.pdf" -o -name "*.canvas" \) 2>/dev/null)
if [ -n "$ATTACHMENT_FILES" ]; then
    echo "" >> "$LOG_FILE"
    echo "### 첨부파일 이동" >> "$LOG_FILE"
    for file in $ATTACHMENT_FILES; do
        filename=$(basename "$file")
        mv "$file" "$VAULT_DIR/Attachments/"
        echo "- \`$filename\` → \`Attachments/\`" >> "$LOG_FILE"
        MOVED_COUNT=$((MOVED_COUNT + 1))
    done
fi

# 결과 요약
echo "" >> "$LOG_FILE"
echo "**결과: ${MOVED_COUNT}개 파일 정리 완료**" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# 잔여 파일 확인
REMAINING=$(find "$INBOX" -maxdepth 1 -type f 2>/dev/null | wc -l)
if [ "$REMAINING" -gt 0 ]; then
    echo "### Inbox 잔여 파일 (수동 분류 필요)" >> "$LOG_FILE"
    find "$INBOX" -maxdepth 1 -type f -exec basename {} \; >> "$LOG_FILE"
fi

echo ""
echo "=== 볼트 정리 완료 ==="
echo "정리된 파일: ${MOVED_COUNT}개"
echo "Inbox 잔여: ${REMAINING}개"
echo "로그: $LOG_FILE"
