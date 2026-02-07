<#
.SYNOPSIS
    Install GSD-Docs Industrial plugin for Claude Code.

.DESCRIPTION
    Creates directory junctions from this repository to ~/.claude/ so the
    plugin is available as /doc:* slash commands in Claude Code.

    Junctions mean changes in the repo are immediately active — no
    reinstall needed after edits or git pull. No admin rights required.

.EXAMPLE
    .\install.ps1

    # Reinstall (recreate junctions):
    .\install.ps1 -Force

    # Uninstall:
    .\install.ps1 -Uninstall
#>

param(
    [switch]$Uninstall,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$ClaudeDir = Join-Path $env:USERPROFILE ".claude"
$RepoRoot = $PSScriptRoot

# What we link: source (in repo) -> target (in ~/.claude/)
$Links = @(
    @{
        Source = Join-Path $RepoRoot "gsd-docs-industrial"
        Target = Join-Path $ClaudeDir "gsd-docs-industrial"
        Description = "Plugin directory (references, templates, workflows)"
    },
    @{
        Source = Join-Path $RepoRoot "commands\doc"
        Target = Join-Path $ClaudeDir "commands\doc"
        Description = "Slash commands (/doc:*)"
    }
)

function Write-Status($icon, $msg) {
    Write-Host "$icon $msg"
}

function Is-Junction($path) {
    if (-not (Test-Path $path)) { return $false }
    $item = Get-Item $path -Force
    return ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint)
}

# --- Uninstall ---
if ($Uninstall) {
    Write-Host ""
    Write-Host "Uninstalling GSD-Docs Industrial..." -ForegroundColor Yellow
    Write-Host ""

    foreach ($link in $Links) {
        if (Is-Junction $link.Target) {
            cmd /c "rmdir `"$($link.Target)`"" 2>$null
            Write-Status "  Removed" $link.Target
        } elseif (Test-Path $link.Target) {
            Write-Status "  Skipped" "$($link.Target) (not a junction — won't delete)"
        } else {
            Write-Status "  Skipped" "$($link.Target) (not found)"
        }
    }

    Write-Host ""
    Write-Status "Done." "GSD-Docs Industrial uninstalled."
    Write-Host ""
    exit 0
}

# --- Install ---
Write-Host ""
Write-Host "Installing GSD-Docs Industrial..." -ForegroundColor Cyan
Write-Host ""

# Verify repo structure
foreach ($link in $Links) {
    if (-not (Test-Path $link.Source)) {
        Write-Error "Source not found: $($link.Source). Run this script from the repo root."
    }
}

# Ensure ~/.claude/commands/ exists
$commandsDir = Join-Path $ClaudeDir "commands"
if (-not (Test-Path $commandsDir)) {
    New-Item -ItemType Directory -Path $commandsDir -Force | Out-Null
    Write-Status "  Created" $commandsDir
}

# Create junctions
foreach ($link in $Links) {
    if (Test-Path $link.Target) {
        if (Is-Junction $link.Target) {
            if ($Force) {
                cmd /c "rmdir `"$($link.Target)`"" 2>$null
                Write-Status "  Removed" "existing junction at $($link.Target)"
            } else {
                Write-Status "  Exists" "$($link.Target) (use -Force to recreate)"
                continue
            }
        } else {
            if ($Force) {
                Remove-Item $link.Target -Recurse -Force
                Write-Status "  Removed" "existing directory at $($link.Target)"
            } else {
                Write-Warning "$($link.Target) exists and is NOT a junction. Use -Force to replace."
                continue
            }
        }
    }

    cmd /c "mklink /J `"$($link.Target)`" `"$($link.Source)`"" | Out-Null
    Write-Status "  Linked" "$($link.Target)"
    Write-Status "     ->" "$($link.Source)"
    Write-Status "        " $link.Description
}

Write-Host ""
Write-Status "Done." "GSD-Docs Industrial installed."
Write-Host ""
Write-Host "  Available commands:" -ForegroundColor Green
Write-Host "    /doc:new-fds    Create a new FDS project"
Write-Host ""
Write-Host "  To uninstall:  .\install.ps1 -Uninstall"
Write-Host ""
