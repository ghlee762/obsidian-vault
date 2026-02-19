# run_organizer.ps1 - 매주 실행되어 사용자에게 확인 후 볼트 정리 실행
# Windows Task Scheduler에서 호출됩니다.

Add-Type -AssemblyName System.Windows.Forms

# 확인 팝업 표시
$result = [System.Windows.Forms.MessageBox]::Show(
    "Obsidian 볼트 정리를 실행할까요?`n`nInbox에 있는 파일을 주제별로 자동 분류합니다.",
    "Vault Organizer - 주간 정리",
    [System.Windows.Forms.MessageBoxButtons]::YesNo,
    [System.Windows.Forms.MessageBoxIcon]::Question
)

if ($result -eq [System.Windows.Forms.DialogResult]::Yes) {
    # Git Bash로 정리 스크립트 실행
    $scriptPath = "C:/task/Obsidian_Vault/이근호/퇴직준비세미나_이근호/.claude/scripts/vault_organizer.sh"
    $gitBash = "C:\Program Files\Git\bin\bash.exe"

    if (Test-Path $gitBash) {
        $process = Start-Process -FilePath $gitBash -ArgumentList "-c", "`"$scriptPath`"" -Wait -PassThru -NoNewWindow

        if ($process.ExitCode -eq 0) {
            [System.Windows.Forms.MessageBox]::Show(
                "볼트 정리가 완료되었습니다!`n로그를 확인하려면 .claude/scripts/organizer_log.md를 열어보세요.",
                "Vault Organizer",
                [System.Windows.Forms.MessageBoxButtons]::OK,
                [System.Windows.Forms.MessageBoxIcon]::Information
            )
        }
    } else {
        [System.Windows.Forms.MessageBox]::Show(
            "Git Bash를 찾을 수 없습니다.`nGit이 설치되어 있는지 확인해주세요.",
            "Vault Organizer - 오류",
            [System.Windows.Forms.MessageBoxButtons]::OK,
            [System.Windows.Forms.MessageBoxIcon]::Error
        )
    }
} else {
    # No 선택 시 아무것도 하지 않음
    exit 0
}
