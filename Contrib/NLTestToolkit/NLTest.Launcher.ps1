# This script opens PS console to execute NLedger test interactively.
[CmdletBinding()]
Param()

[string]$Script:ScriptPath = Split-Path $MyInvocation.MyCommand.Path
Import-Module "$Script:ScriptPath/../NLManagement/NLCommon.psm1" -Force

[string]$nlTestPath = [System.IO.Path]::GetFullPath("$Script:ScriptPath/NLTest.ps1")
if (!(Test-Path -LiteralPath $nlTestPath -PathType Leaf)) {throw "Cannot find '$nlTestPath'"}

$nlBinInfo = Get-PreferredNLedgerBinaryInfo
if (!$nlBinInfo) { throw "NLedger binary file not found. Please, check your deployment structure and verify that binary files are presented. Use -verbose switch to troubleshoot the problem." }
$env:nledgerExePath = $nlBinInfo.NLedgerExecutable

function run {
[CmdletBinding()]
Param(
    [Parameter(Mandatory=$False)][AllowEmptyString()][string]$filterRegex = ""
)
    if ([string]::IsNullOrWhiteSpace($filterRegex)) {
        $null = (& $nlTestPath -showReport)
    } else {
        $null = (& $nlTestPath -showReport -filterRegex $filterRegex)
    }
}

function xrun {
[CmdletBinding()]
Param(
    [Parameter(Mandatory=$False)][AllowEmptyString()][string]$filterRegex = ""
)
    if ([string]::IsNullOrWhiteSpace($filterRegex)) {
        $null = (& $nlTestPath)
    } else {
        $null = (& $nlTestPath -filterRegex $filterRegex)
    }
}

function all {
[CmdletBinding()]
Param(
    [Parameter(Mandatory=$False)][AllowEmptyString()][string]$filterRegex = ""
)
    if ([string]::IsNullOrWhiteSpace($filterRegex)) {
        $null = (& $nlTestPath -disableIgnoreList)
    } else {
        $null = (& $nlTestPath -disableIgnoreList -filterRegex $filterRegex)
    }
}

function status {
    [CmdletBinding()]
    Param()
    
    "NLedger binary file: $env:nledgerExePath"
    (Out-NLedgerBinaryInfos -currentNLedgerExecutable $env:nledgerExePath) | Out-AnsiString
}

function platform {
[CmdletBinding()]
Param(
    [Parameter(Mandatory=$True)][string]$tfmCode,
    [Switch][bool]$debugMode = $false)

    $nlBinInfo = Get-NLedgerBinaryInfo -tfmCode $tfmCode -isDebug $debugMode
    if ($nlBinInfo) {
        $env:nledgerExePath = $nlBinInfo.NLedgerExecutable
    } else {
        Write-Error "NLedger binary for [$tfmCode|$(if($debugMode){"Debug"}else{"Release"})] not found."
    }

}


function help {
[CmdletBinding()]
Param()
     write-host "Interactive testing console helps you execute NLedger test files that are available on the disk.`r`n"
     write-host -NoNewline "It supports several short commands that perform typical activities:`r`n PS>"
     write-host -NoNewline -ForegroundColor Yellow "run"
     write-host -NoNewline "              execute all test files and show a report in the browser;`r`n PS>"
     write-host -NoNewline -ForegroundColor Yellow "run CRITERIA"
     write-host -NoNewline "     execute tests that match the criteria and show a report;`r`n PS>"
     write-host -NoNewline -ForegroundColor Yellow "xrun"
     write-host -NoNewline "             execute all test files and show a summary in the console;`r`n PS>"
     write-host -NoNewline -ForegroundColor Yellow "xrun CRITERIA"
     write-host -NoNewline "    execute matched test files and show a summary in the console;`r`n PS>"
     write-host -NoNewline -ForegroundColor Yellow "all"
     write-host -NoNewline "              execute all test including disabled by the ignore list; the summary is in the console;`r`n PS>"
     write-host -NoNewline -ForegroundColor Yellow "all CRITERIA"
     write-host -NoNewline "     execute matched test files including disabled; the summary is in the console;`r`n PS>"
     write-host -NoNewline -ForegroundColor Yellow "platform [-core]"
     write-host -NoNewline " select .Net platform to execute tests; .Net Framework by default or .Net Core with '-core' switch;`r`n PS>"
     write-host -NoNewline -ForegroundColor Yellow "help"
     write-host -NoNewline "             show help page again.`r`n"
     write-host -NoNewline "`r`nTesting script can be called directly:`r`n PS>"
     write-host -ForegroundColor Yellow ".\nltest.ps1 OPTIONAL ARGUMENTS"
     write-host -NoNewline "Use 'get-help' to get detail information about testing script arguments:`r`n PS>"
     write-host -ForegroundColor Yellow "get-help .\nltest.ps1"
     write-host -NoNewline "`r`nType '"
     write-host -NoNewline -ForegroundColor Yellow "exit"
     write-host "' or close the console window when you finish.`r`n"
}


write-host -ForegroundColor White "NLedger Testing Toolkit - Interactive console"
write-host ""
help
status

