$ErrorActionPreference = "Stop"

$options = "-b:a", "64k"
$m4a_options = "-codec:a", "libfdk_aac"
$ogg_options = "-codec:a", "libopus"

if ($args[1]) {
    $labels_path = $args[1]
} else {
    $labels_path = $(Split-Path $(Resolve-Path $args[0])) + "\Label Track.txt"
    if (!(Test-Path $labels_path -PathType Leaf)) {
        Clear-Variable labels_path
    }
}

if ($labels_path) {
    Invoke-Expression $("$($PSScriptRoot)\makechapters.py `"$labels_path`"")
    $options = ("-i", ((Split-Path $labels_path) + "\ffmetadata.txt")) + $options
}

ffmpeg -i $args[0] $options $m4a_options "$((Get-Item $args[0]).Directory)\$((Get-Item $args[0]).BaseName).m4a"
ffmpeg -i $args[0] $options $ogg_options "$((Get-Item $args[0]).Directory)\$((Get-Item $args[0]).BaseName).ogg"
