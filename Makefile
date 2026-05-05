.PHONY: verify export dashboard install-py-deps

install-py-deps:
	pip3 install --user gspread google-auth pytest

verify:
	python3 -m pytest tests/ -q

export:
	python3 rover_export_json.py --out dashboard/public/data

dashboard:
	cd dashboard && npm install && npm run dev
