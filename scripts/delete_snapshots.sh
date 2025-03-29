#!/bin/bash

# Extracting Snapshot IDs
snapshot_ids=$(uv run morphcloud snapshot list | awk 'NR>2 {print $1}')

# Loop through and delete each snapshot
for id in $snapshot_ids; do
    echo "Deleting snapshot: $id"
    uv run morphcloud snapshot delete "$id"
done
