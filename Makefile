# Define default output directory
OUTPUT_DIR := ./out
BINARY_NAME := SpiderINMET

publish: check-pyinstaller create-output-dir
	pyinstaller --onefile \
		--distpath $(OUTPUT_DIR) \
		--name $(BINARY_NAME) \
		SpiderINMET.py
	@echo "Copying config file to output directory..."
	cp config.json $(OUTPUT_DIR)/

check-pyinstaller:
	@which pyinstaller > /dev/null 2>&1 || $(MAKE) install-pyinstaller

install-pyinstaller:
	@echo "PyInstaller not found. Installing..."
	pip install pyinstaller

create-output-dir:
	@mkdir -p $(OUTPUT_DIR)

clean:
	@echo "Cleaning up build files..."
	rm -rf build/
	rm -rf __pycache__/
	rm -rf *.spec
	rm -rf $(OUTPUT_DIR)/

.PHONY: publish check-pyinstaller install-pyinstaller create-output-dir clean