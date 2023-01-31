#!/bin/sh
git ls-remote --tags https://github.com/libjxl/libjxl.git 2>/dev/null |awk '{ print $2; }'  |grep -v '\^{}' |grep 'refs/tags/v' |sed -e 's,refs/tags/v,,' |grep -vE '(snapshot|alpha|beta|rc)' |sort -V |tail -n1
