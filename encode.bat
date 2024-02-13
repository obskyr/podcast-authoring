@REM Encode an episode (from a lossless format) to the formats that Obscuriosities puts out.

@SET SAMPLE_FREQUENCY=44100
@SET BITRATE=96k

@REM Ogg Opus version. Stereo because libopus for *some reason* makes *larger* mono files than stereo files. 
@REM However, stereo Opus files are still smaller than mono AAC files!!! What a codec!
@REM https://gitlab.xiph.org/xiph/opus/-/issues/2341
@REM Worth noting is that Opus does not support 44,100 kHz specifically – but it will correctly round up to 48,000 kHz.
ffmpeg -i "%~1" -i "%~dp1ffmetadata.txt" -r %SAMPLE_FREQUENCY% -b:a %BITRATE% -vbr off -c:a libopus -map_metadata 0 -map_metadata 1 -y "%~dp1%~n1.opus"

@REM M4A version. Mono for file size. `-movflags +faststart` puts metadata at the start of the file (as opposed to the end), so that it can be streamed.
ffmpeg -i "%~1" -i "%~dp1ffmetadata.txt" -ac 1 -r %SAMPLE_FREQUENCY% -b:a %BITRATE% -movflags +faststart -c:a libfdk_aac -map_metadata 0 -map_metadata 1 -y "%~dp1%~n1.m4a"
