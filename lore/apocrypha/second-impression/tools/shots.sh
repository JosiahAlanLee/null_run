#!/bin/bash
# shots.sh out.png res page [page...]  -> montage of the given PDF pages
S=/tmp/claude-0/-home-user-null-run/b5c08984-496b-52c5-b337-3ecebe9ada65/scratchpad
PDF=$S/book/out/null-run-uncollected-editions-second-impression.pdf
out=$1; res=$2; shift 2; rm -f $S/sh-*.png; files=""
for p in "$@"; do pdftoppm -r $res -f $p -l $p -png $PDF $S/sh-$p 2>/dev/null; files="$files $(ls $S/sh-$p-*.png)"; done
convert $files +append $S/$out
