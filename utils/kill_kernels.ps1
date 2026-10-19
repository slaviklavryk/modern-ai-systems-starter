<#
.SYNOPSIS
    List Jupyter kernels, and kill the ones that will not restart.

.DESCRIPTION
    A Jupyter kernel is a python.exe process whose command line contains
    "ipykernel_launcher". VS Code and Jupyter normally stop it when you restart or
    close the notebook; this script is for the kernel that does not stop.

    Without options the script lists the running kernels and asks before killing
    them. A kernel started from a virtual environment appears twice: the environment's
    python.exe starts the real interpreter as a second process, its child, with the same
    command line. -Id kills both processes of a kernel when given either of them.

    After a kernel is killed, VS Code reports that it died; choose Restart.

.EXAMPLE
    .\utils\kill_kernels.ps1              # list, then ask before killing all
.EXAMPLE
    .\utils\kill_kernels.ps1 -List        # list only
.EXAMPLE
    .\utils\kill_kernels.ps1 -Id 12345    # kill one kernel, after asking
.EXAMPLE
    .\utils\kill_kernels.ps1 -Force       # kill every kernel without asking

.NOTES
    If PowerShell refuses to run scripts, run it as:
        powershell -ExecutionPolicy Bypass -File .\utils\kill_kernels.ps1
#>
param(
    [switch]$List,
    [switch]$Force,
    [int[]]$Id
)

$kernels = @(Get-CimInstance Win32_Process -Filter "Name = 'python.exe' OR Name = 'pythonw.exe'" |
    Where-Object { $_.CommandLine -match 'ipykernel_launcher' })

if ($kernels.Count -eq 0) {
    Write-Host "No Jupyter kernels are running."
    exit 0
}

$kernels |
    Sort-Object CreationDate |
    Select-Object @{ Name = 'Id';       Expression = { $_.ProcessId } },
                  @{ Name = 'Parent';   Expression = { $_.ParentProcessId } },
                  @{ Name = 'Started';  Expression = { $_.CreationDate.ToString('yyyy-MM-dd HH:mm') } },
                  @{ Name = 'MemoryMB'; Expression = { [math]::Round($_.WorkingSetSize / 1MB) } },
                  @{ Name = 'Python';   Expression = { $_.ExecutablePath } } |
    Format-Table -AutoSize | Out-Host

if ($List) { exit 0 }

$targets = @($kernels)
if ($Id) {
    # One kernel can be two processes (see the description): take the partner of each Id,
    # its kernel parent or its kernel child, as well.
    $related = @($Id) +
        @($kernels | Where-Object { $Id -contains $_.ProcessId } | ForEach-Object { $_.ParentProcessId }) +
        @($kernels | Where-Object { $Id -contains $_.ParentProcessId } | ForEach-Object { $_.ProcessId })
    $targets = @($kernels | Where-Object { $related -contains $_.ProcessId })
    if ($targets.Count -eq 0) {
        Write-Host "No kernel has Id $($Id -join ', ')."
        exit 1
    }
}

if (-not $Force) {
    $answer = Read-Host "Kill $($targets.Count) kernel process(es)? [y/N]"
    if ($answer -notmatch '^(y|yes)$') {
        Write-Host "Nothing killed."
        exit 0
    }
}

foreach ($kernel in $targets) {
    try {
        Stop-Process -Id $kernel.ProcessId -Force -ErrorAction Stop
        Write-Host "Killed $($kernel.ProcessId)"
    }
    catch [Microsoft.PowerShell.Commands.ProcessCommandException] {
        Write-Host "$($kernel.ProcessId) had already stopped"
    }
    catch {
        Write-Host "Could not kill $($kernel.ProcessId): $($_.Exception.Message)"
    }
}
