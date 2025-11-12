!/bin/bash

set -xeuo pipefail

launcher_opts=(--etc-dir /usr/lib/trino-server-418/etc)
if ! grep -s -q 'node.id' /usr/lib/trino-server-418/etc/node.properties; then
    launcher_opts+=("-Dnode.id=${HOSTNAME}")
fi

exec /usr/lib/trino-server-418/bin/launcher run "${launcher_opts[@]}" "$@"
