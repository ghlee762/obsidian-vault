Add-Type -AssemblyName System.Windows.Forms

$result = [System.Windows.Forms.MessageBox]::Show(
    "Run Obsidian Vault Organizer?`n`nFiles in Inbox will be auto-sorted by topic.",
    "Vault Organizer - Weekly",
    [System.Windows.Forms.MessageBoxButtons]::YesNo,
    [System.Windows.Forms.MessageBoxIcon]::Question
)

if ($result -eq [System.Windows.Forms.DialogResult]::Yes) {
    $batFile = Join-Path $PSScriptRoot "run_bash.bat"

    if (Test-Path $batFile) {
        $process = Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "`"$batFile`"" -Wait -PassThru -NoNewWindow

        if ($process.ExitCode -eq 0) {
            [System.Windows.Forms.MessageBox]::Show(
                "Vault organizing complete!`n`nCheck log: .claude/scripts/organizer_log.md",
                "Vault Organizer",
                [System.Windows.Forms.MessageBoxButtons]::OK,
                [System.Windows.Forms.MessageBoxIcon]::Information
            )
        } else {
            [System.Windows.Forms.MessageBox]::Show(
                "Script finished with errors.`nExit code: $($process.ExitCode)",
                "Vault Organizer - Warning",
                [System.Windows.Forms.MessageBoxButtons]::OK,
                [System.Windows.Forms.MessageBoxIcon]::Warning
            )
        }
    } else {
        [System.Windows.Forms.MessageBox]::Show(
            "run_bash.bat not found at:`n$batFile",
            "Vault Organizer - Error",
            [System.Windows.Forms.MessageBoxButtons]::OK,
            [System.Windows.Forms.MessageBoxIcon]::Error
        )
    }
} else {
    exit 0
}
