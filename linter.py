from cuda_lint import Linter, util
from cudatext import *
import os

script = """
Import-Module PSScriptAnalyzer;
if (Test-Path PSScriptAnalyzerSettings.psd1)
{
    "\\$FullResult" = Invoke-ScriptAnalyzer ${temp_file} -Setting PSScriptAnalyzerSettings.psd1
}
else
{
    if ("\\$GlobalPSScriptAnalyzerSettingsPath")
    {
        "\\$FullResult" = Invoke-ScriptAnalyzer ${temp_file} -Setting "\\$GlobalPSScriptAnalyzerSettingsPath"
    }
    else
    {
        "\\$FullResult" = Invoke-ScriptAnalyzer -Path ${temp_file}
    }
};

foreach ("\\$Result" in "\\$FullResult")
{
    "\\$Line"       =   "\\$Result.Line" ;
    "\\$Message"    =   "\\$Result.Message" ;
    "\\$RuleName"   =   "\\$Result.RuleName" ;
    "\\$Severity"   =   "\\$Result.Severity" ;
    "\\$Column"     =   "\\$Result.column" ;
    "\\$Extent"     =   "\\$Result.Extent.Text.trim()" ;
    "\\$Suggestion" =   "\\$Result.SuggestedCorrections.description" ;

    if ("\\$Extent")
    {
        Write-Host '"Line:\\$Line RuleName:\\$RuleName Severity:\\$Severity Extent:\\$Extent Message:\\$Message \\$Suggestion"'
    }
    else
    {
        Write-Host '"Line:\\$Line RuleName:\\$RuleName Severity:\\$Severity Column:\\$Column Message:\\$Message \\$Suggestion"'
    }
}"""

if os.name == 'nt':
    bcmd = 'powershell.exe -nol -c {}; '
else:
    bcmd = 'pwsh -nol -c {}; '


class PSLint(Linter):
    cmd = bcmd.format(script)

    regex = (
        r'Line:(?P<line>\d+)\sRuleName:(?P<code>\w+)\sSeverity:((?P<error>\S*?Error)|'
        r'(?P<warning>Warning|Information))\s(Column:(?P<col>\d+)|Extent:(?P<near>.*?))\sMessage:(?P<message>.*)'
    )

    tempfile_suffix = 'ps'
    multiline = False
    syntax='PowerShell'
    word_re = r'^([-\S]+|\s+$)'
    
    defaults = {
        "selector": "source.powershell"
    }
    def split_match(self, match):
        """Return the match with ` quotes transformed to '."""
        match, line, col, error, warning, message, near = super().split_match(match)

        if message == 'no PowerShell code found at all':
            match = None
        else:
            message = message.replace('`', '\'')

            # If the message contains a complaint about a function
            # and near looks like a function reference, remove the trailing
            # () so it can be found.
            if 'function \'' in message and near and near.endswith('()'):
                near = near[:-2]

        return match, line, col, error, warning, message, near
