FOR %%X IN (%*) DO (
    magick convert %%X -crop 480x432+240+56 -scale 33.3333%% -scale 200%% %%X
)
