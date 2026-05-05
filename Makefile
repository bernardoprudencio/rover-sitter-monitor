.PHONY: verify export dashboard install-py-deps confluence-dump confluence-retag confluence-full

install-py-deps:
	pip3 install --user gspread google-auth pytest requests beautifulsoup4

verify:
	python3 -m pytest tests/ -q

export:
	python3 rover_export_json.py --out dashboard/public/data

dashboard:
	cd dashboard && npm install && npm run dev

confluence-dump:
	python3 rover_confluence_dump.py

confluence-retag:
	python3 rover_confluence_dump.py --retag

confluence-full:
	python3 rover_confluence_dump.py --full
