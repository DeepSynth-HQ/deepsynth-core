agent:
	export PYTHONPATH=$$PYTHONPATH:. && \
	python agents/base.py

prompt:
	export PYTHONPATH=$$PYTHONPATH:. && \
	python prompt_engineering/deepsynth.py
