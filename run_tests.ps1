# Setze den Python Path
$env:PYTHONPATH = "$PSScriptRoot;$env:PYTHONPATH"

# Führe pytest aus
pytest $args 