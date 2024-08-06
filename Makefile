#!/usr/bin/make -f

include $(CURDIR)/.env

wget := wget -q -O - --header "AS-Key: $(AS_KEY)"

CUSTOM := 0

iwwc-now-%.json iwwc-custom-%.json iwwc-info-%.json refresh-% fetch-%: YEAR=$*
fetch-%: CUSTOM=1

iwwc-custom-%.json: iwwc-info-%.json
	$(wget) 'https://api.agent-stats.com/groups/$(AS_GROUP_ID_$(YEAR))/custom' > ".tmp.$@"
	mv ".tmp.$@" "$@"

iwwc-now-%.json: iwwc-info-%.json
	$(wget) 'https://api.agent-stats.com/groups/$(AS_GROUP_ID_$(YEAR))/now' > ".tmp.$@"
	mv ".tmp.$@" "$@"

iwwc-info-%.json:
	$(wget) 'https://api.agent-stats.com/groups/$(AS_GROUP_ID_$(YEAR))/info' > ".tmp.$@"
	if ! [ -e "$@" ] || ! cmp -s "$@" ".tmp.$@"; then mv ".tmp.$@" "$@"; fi

fetch-%:
	$(MAKE) -s -B iwwc-info-$*.json
	if [ $(CUSTOM) -eq 1 ]; then $(MAKE) -s iwwc-custom-$*.json; fi
	$(MAKE) -s iwwc-now-$*.json
	git add iwwc-*-$*.json
	git diff-index --quiet HEAD iwwc-*-$*.json || git commit --quiet -m 'Auto-commit($(YEAR)).'
	#git push --quiet

refresh-%:
	echo "YEAR=$(YEAR)"
	$(wget) -O /dev/null --method post 'https://api.agent-stats.com/groups/$(AS_GROUP_ID_$(YEAR))/refresh'

.PHONY: refresh
