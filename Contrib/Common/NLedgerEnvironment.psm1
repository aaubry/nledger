 <#
.SYNOPSIS
Helper functions for interacting with the NLedger binaries

.DESCRIPTION
Provides information about the current structure of NLedger deployment
#> 

[string]$Script:ScriptPath = Split-Path $MyInvocation.MyCommand.Path
Import-Module $Script:ScriptPath/SysPlatform.psm1 -Force
Import-Module $Script:ScriptPath/SysDotnet.psm1 -Force

<#
.SYNOPSIS
    Returns a fully qualified path and name to NLedger executable file
.DESCRIPTION
    Checks whether given folder contains NLedger executable file and returns a full path and name.
    It works on any OS (Windows, Linux, OSX) so it either returns NLedger-cli.exe or NLedger-cli.
    If folder or file does not exist, it returns an empty value.
#>
function Get-NLedgerExecutableFile {
  [CmdletBinding()]
  Param([Parameter(Mandatory=$True)][string]$folderName)
  
  $folderName = [System.IO.Path]::GetFullPath($folderName)
  if (Test-Path -LiteralPath $folderName -PathType Container) {
    [string]$nledgerFile = [System.IO.Path]::GetFullPath("$folderName/NLedger-cli.exe")
    if (Test-Path -LiteralPath $nledgerFile -PathType Leaf) { $nledgerFile }
    else {
      $nledgerFile = [System.IO.Path]::GetFullPath("$tfmFolder/NLedger-cli")
      if (Test-Path -LiteralPath $nledgerFile -PathType Leaf) { $nledgerFile }
    }
  }
}

<#
.SYNOPSIS
    Returns a collection of NLedger binaries found in a package folder.
.DESCRIPTION
    Looks for NLedger binaries in all sub-folders of a given folder.
    Sub-folders should match TFM names or ignored otherwise.
    Returns a collection of objects containing a full path, TFM code and other flags.
    Note: isDebug is a declarative flag indicating wether folder contains Release or Debug binaries.
#>
function Find-NLedgerBinaries {
  [CmdletBinding()]
  Param(
    [Parameter(Mandatory=$True)][string]$folderName,
    [Parameter(Mandatory=$True)][bool]$isDebug
  )

  if (Test-Path -LiteralPath $folderName -PathType Container) {
    Write-Verbose "Find-NLedgerBinaries - collecting info from $folderName folder."
    foreach($targetFolder in (Get-ChildItem -LiteralPath $folderName -Directory) | Where-Object { Test-IsTfmCode $_.Name }) {
      [string]$tfmCode = $targetFolder.Name
      [string]$tfmFolder = $targetFolder.FullName
      [bool]$isOsxRuntime = $false

      if (Test-Path -LiteralPath "$tfmFolder/osx-x64" -PathType Container) { 
        $tfmFolder = "$tfmFolder/osx-x64"
        $isOsxRuntime = $true
      }

      [string]$nledgerFile = Get-NLedgerExecutableFile $tfmFolder
      if (!$nledgerFile) { continue }

      Write-Verbose "Found executable NLedger: $nledgerFile (TFM: $tfmCode; Debug: $isDebug; OSX: $isOsxRuntime)"
      [PSCustomObject]@{
        NLedgerExecutable = $nledgerFile
        TfmCode = $tfmCode
        IsDebug = $isDebug
        IsOsxRuntme = $isOsxRuntime
      }
    }
  } else {
    Write-Verbose "Find-NLedgerBinaries - folder $folderName does not exist."
  }
}
  
<#
.SYNOPSIS
    Returns a collection of all available NLedger binaries located in the current deployment structure.
.DESCRIPTION
    Looks for NLedger binaries in expected locations in the current deployment structure (where the script is located).
    It properly recognizes development structures (and looks for binaries in Source/NLedger.CLI/bin folder)
    or deployment packages (with /bin/ folder).
#>
function Find-CurrentNLedgerBinaries {
  [CmdletBinding()]
  Param()

  [string]$devDebugBin = [System.IO.Path]::GetFullPath("$Script:ScriptPath/../../Source/NLedger.CLI/bin/Debug")
  [string]$devReleaseBin = [System.IO.Path]::GetFullPath("$Script:ScriptPath/../../Source/NLedger.CLI/bin/Release")
  [string]$publicBin = [System.IO.Path]::GetFullPath("$Script:ScriptPath/../../bin")

  return  @() +
          (Find-NLedgerBinaries -folderName $devDebugBin -isDebug $true) +
          (Find-NLedgerBinaries -folderName $devReleaseBin -isDebug $false) +
          (Find-NLedgerBinaries -folderName $publicBin -isDebug $false)
}

<#
.SYNOPSIS
    Returns a collection of all installed NLedger binaries on the current machine.
.DESCRIPTION
    NLedger is considered to be installed if it is available by PATH variable.
    This function returns all NLedger binary files found by any path listed in PATH variable.
    Of course, only the first path is effective.
#>
function Find-InstalledNLedgerBinaries {
  [CmdletBinding()]
  Param()

  Get-Paths | ForEach-Object { Get-NLedgerExecutableFile $_ } | Where-Object { $_ }
}

function Get-NLedgerDeploymentInfo {
  [CmdletBinding()]
  Param()

  $runtimes = Get-AllRuntimeTargets

  $binaries = Find-CurrentNLedgerBinaries

  $installed = Find-InstalledNLedgerBinaries
  [string]$effectiveInstalled = $installed | Select-Object -First 1
  [bool]$isExternalInstall = $effectiveInstalled -and ($binaries | Where-Object {$_.NLedgerExecutable -eq $effectiveInstalled} | Measure-Object).Count -eq 0


  [PSCustomObject]@{
    Binaries = $binaries
    Installed = $installed
    EffectiveInstalled = $effectiveInstalled
    IsExternalInstall = $isExternalInstall
    Runtimes = $runtimes

  }

}




  <#
  .SYNOPSIS
      Provides information about a specific NLedger binary file
  .DESCRIPTION
      Looks for a specific NLedger instance in a collection of available local binaries
      using specified TFM code and Debug/Release flag
  #>
  function Get-NLedgerBinaryInfo {
    [CmdletBinding()]
    Param(
      [Parameter(Mandatory=$True)][string]$tfmCode,
      [Parameter(Mandatory=$True)][bool]$isDebug
    )
  
    return  Get-NLedgerBinaryInfos | Where-Object { $_.TfmCode -eq $tfmCode -and $_.IsDebug -eq $isDebug }
  }
  
  
  
  <#
  .SYNOPSIS
      Provides information about preferred ready-to-use NLedger binary file
  .DESCRIPTION
      Returns a NLedger instance that belongs to the current deployment structure.
      If the current structure contains more than one binary file, it returns the installed one.
      If NLedger is not installed (or installed NLedger belongs to another deployment structure), 
      it returns the instance with the highest TFM code.
      If the current deployment structure does not have any NLedger binary file, the function returns null.
  #>
  function Get-PreferredNLedgerBinaryInfo {
    [CmdletBinding()]
    Param()
  
    # TODO
    return  Get-NLedgerBinaryInfos | Sort-Object {$_.VersionOrder} | Select-Object -Last 1
  }
  
# For internal usage
function Out-NLedgerBinaryInfo {
  [CmdletBinding()]
  Param([Parameter(Mandatory=$True)]$info)

  $text = "[$($info.TfmCode)|$(if($($info.IsDebug)){"Debug"}else{"Release"}$(if($($info.IsOsxRuntme)){"(OSX)"}))]"
  if ($currentNLedgerExecutable -eq $info.NLedgerExecutable) {$text="{c:Yellow}$text{f:Normal}"}
  $text
}


  <#
  .SYNOPSIS
      Provides information about available NLedger binaries in a well-formatted user-friendly way
  .DESCRIPTION
      Returns a comma separated string containing TFM code and debug/release flag for every available binary.
      If the parameter currentNLedgerExecutable is provided, the corresponded code is highlighted
  #>
  
  function Out-NLedgerBinaryInfos {
    [CmdletBinding()]
    Param(
      [Parameter(Mandatory=$False)][string]$currentNLedgerExecutable
    )
  
    return  (Get-NLedgerBinaryInfos | Sort-Object {$_.VersionOrder} | ForEach-Object { (Out-NLedgerBinaryInfo $_) }) -join ","
  }
  
  Export-ModuleMember -function * -alias *