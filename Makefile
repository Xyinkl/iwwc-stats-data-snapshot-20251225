#!/usr/bin/make -f

include $(CURDIR)/.env

wget := wget -q -O - --header "AS-Key: $(AS_KEY)"

iwwc-custom.json: iwwc-info.json
	$(wget) 'https://api.agent-stats.com/groups/$(AS_GROUP_ID)/custom' > ".tmp.$@"
	mv ".tmp.$@" "$@"

iwwc-info.json:
	$(wget) 'https://api.agent-stats.com/groups/$(AS_GROUP_ID)/info' > ".tmp.$@"
	if ! [ -e "$@" ] || ! cmp -s "$@" ".tmp.$@"; then mv ".tmp.$@" "$@"; fi

check:
	$(MAKE) -s -B iwwc-info.json
	$(MAKE) -s iwwc-custom.json
	git add iwwc-info.json iwwc-custom.json
	git diff-index --quiet HEAD iwwc-info.json iwwc-custom.json || git commit --quiet -m 'Auto-commit.'
	git push --quiet

refresh:
	$(wget) -O /dev/null --method post 'https://api.agent-stats.com/groups/$(AS_GROUP_ID)/refresh'

.PHONY: refresh
