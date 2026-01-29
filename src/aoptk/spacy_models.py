"""Singleton access to spaCy models."""

from __future__ import annotations

import spacy


class SingletonMeta(type):
    """Singleton metaclass for shared service objects."""

    _instances: dict[type, object] = {}

    def __call__(cls, *args, **kwargs):
        """Return a single instance per class.
        
        Args:
            *args: Positional arguments for the class constructor
            **kwargs: Keyword arguments for the class constructor
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class SpacyModels(metaclass=SingletonMeta):
    """Provide shared spaCy models across the codebase."""

    def __init__(self) -> None:
        self._models: dict[str, object] = {}

    def get_model(self, model: str) -> object:
        """Return a loaded spaCy model, cached by name.
        
        Args:
            model (str): The name of the spaCy model to load.
        """
        if model not in self._models:
            self._models[model] = spacy.load(model)
        return self._models[model]

    def get_blank(self, language: str) -> object:
        """Return a blank spaCy model, cached by language.
        
        Args:
            language (str): The language code for the blank spaCy model.
        """
        key = f"blank:{language}"
        if key not in self._models:
            self._models[key] = spacy.blank(language)
        return self._models[key]

    def ensure_pipe(self, model: object, pipe_name: str, config: dict | None = None) -> object:
        """Ensure a pipeline component exists, returning the model.
        
        Args:
            model (object): The spaCy model to modify.
            pipe_name (str): The name of the pipeline component to ensure.
            config (dict | None): Optional configuration for the pipeline component.
        """
        if pipe_name not in model.pipe_names:
            model.add_pipe(pipe_name, config=config or {})
        return model