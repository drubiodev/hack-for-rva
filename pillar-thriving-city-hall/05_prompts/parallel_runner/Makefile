PROMPTS_DIR ?= 05_prompts/research
RUNNER      := 05_prompts/parallel_runner
OUTPUT_DIR  ?= research

# Run a single prompt: make run-one PROMPT=05_prompts/research/A1_problem_landscape_foo.txt
run-one:
	python $(RUNNER)/run_one.py $(PROMPT) --output-dir $(OUTPUT_DIR)

# Run all pending prompts (skips existing outputs)
run-all:
	python $(RUNNER)/run_all.py $(PROMPTS_DIR) --output-dir $(OUTPUT_DIR)

# Run all prompts, overwriting existing outputs
run-all-overwrite:
	python $(RUNNER)/run_all.py $(PROMPTS_DIR) --output-dir $(OUTPUT_DIR) --overwrite

# List all prompt files
list:
	ls -1 $(PROMPTS_DIR)/*.txt 2>/dev/null || echo "No .txt prompts found in $(PROMPTS_DIR)"

# Remove all research outputs
clean:
	rm -f $(OUTPUT_DIR)/*.md $(OUTPUT_DIR)/*.json

.PHONY: run-one run-all run-all-overwrite list clean
