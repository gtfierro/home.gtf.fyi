#!/bin/bash
set -e
git add -u .
git commit -m 'update'
git push
# hugo && rsync -Phavz --delete public/ webserver:/opt/home.gtf.fyi/
