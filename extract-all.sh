#!/bin/sh

# based on script provided by Dmitry Shevkoplyas at http://stackoverflow.com/questions/12850030/git-getting-all-previous-version-of-a-specific-file-folder

set -ex

list_files() {
	git log --diff-filter=d --date-order --reverse --format="%ad %H" --date=iso-strict "$1" | grep -v '^commit'
}

process() {
	file_path="$1"
	file_name="${file_name##*/}"
	if [ "z$file_name" = "z" ]; then
		file_name="$file_path"
	fi
	dot_count=0
	while read commit_date commit_sha rest; do
		printf '.'
		dot_count=$((dot_count + 1))
		if [ $dot_count -eq 70 ]; then
			printf '\n'
			dot_count=0
		fi
		output="$commit_date.$commit_sha.$file_name"
		if ! [ -e "$EXPORT_TO/$output" ]; then
			git cat-file -p "$commit_sha:$file_path" > "$EXPORT_TO/.tmp.$output"
			mv "$EXPORT_TO/.tmp.$output" "$EXPORT_TO/$output"
		fi
	done
	if [ $dot_count -ne 0 ]; then
		printf '\n'
		dot_count=0
	fi
}

if ! git rev-parse --show-toplevel >/dev/null 2>&1 ; then
	echo "Error: you must run this from within a git working directory" >&2
	exit 1
fi

if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
	echo "Usage: $0 <relative path to file> [<output directory>]" >&2
	exit 2
fi

FILE_PATH="$1"
EXPORT_TO="${2-/tmp/all_versions_exported}"

if ! [ -d "$EXPORT_TO" ]; then
	echo "Creating directory '$EXPORT_TO'"
	mkdir -p "$EXPORT_TO"
fi

echo "Writing files to '$EXPORT_TO'"

list_files "$FILE_PATH" | process "$FILE_PATH"

