Add-Type -AssemblyName System.Windows.Forms

$result = [System.Windows.Forms.MessageBox]::Show(
    "Run Obsidian Vault Organizer?`n`nFiles in Inbox will be auto-sorted by topic.",
    "Vault Organizer - Weekly",
    [System.Windows.Forms.MessageBoxButtons]::YesNo,
    [System.Windows.Forms.MessageBoxIcon]::Question
)

if ($result -eq [System.Windows.Forms.DialogResult]::Yes) {
    $scriptPath = "C:/task/Obsidian_Vault/이근호/퇴직준비세미나_이근호/.claude/scripts/vault_organizer.sh"
    $gitBash = "C:\Program Files\Git\bin\bash.exe"

    if (Test-Path $gitBash) {
        $process = Start-Process -FilePath $gitBash -ArgumentList "-c", "`"$scriptPath`"" -Wait -PassThru -NoNewWindow

        if ($process.ExitCode -eq 0) {
            [System.Windows.Forms.MessageBox]::Show(
                "Vault organizing complete!`n`nCheck log: .claude/scripts/organizer_log.md",
                "Vault Organizer",
                [System.Windows.Forms.MessageBoxButtons]::OK,
                [System.Windows.Forms.MessageBoxIcon]::Information
            )
        }
    } else {
        [System.Windows.Forms.MessageBox]::Show(
            "Git Bash not found.`nPlease check if Git is installed.",
            "Vault Organizer - Error",
            [System.Windows.Forms.MessageBoxButtons]::OK,
            [System.Windows.Forms.MessageBoxIcon]::Error
        )
    }
} else {
    exit 0
}
