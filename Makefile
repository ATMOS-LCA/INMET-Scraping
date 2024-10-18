publish: check-pyinstaller
	pyinstaller --onefile SpiderINMET.py

check-pyinstaller:
	@which pyinstaller > /dev/null 2>&1 || $(MAKE) install-pyinstaller

install-pyinstaller:
	@echo "PyInstaller not found. Installing..."
	pip install pyinstaller