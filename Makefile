agent:
	export PYTHONPATH=$$PYTHONPATH:. && \
	export ENV=development && \
	python agents/base.py

prompt:
	export PYTHONPATH=$$PYTHONPATH:. && \
	python prompt_engineering/deepsynth.py
