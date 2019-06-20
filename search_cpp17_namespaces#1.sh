#! /bin/bash

REPO_ROOT=${REPO_ROOT:=~/Perforce/AUDI_CL32}

function convert_files_in {
    local ROOT="$1"
    local FILE_LIST=$(find "$ROOT" -name "*.h" -or -name "*.hpp" -or -name "*.c" -or -name "*.cpp")
    for f in $FILE_LIST; do        
        local res=$(grep -E "^namespace.*::.*{" "$f")
        if [ -n "$res" ]; then
            echo "CONVERTING $f..."
            python3 convert_namespace_declaration.py "$f"
            echo "CONVERTION DONE for $f"
        fi
    done

}

convert_files_in "$REPO_ROOT"
