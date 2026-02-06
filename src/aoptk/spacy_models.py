"""Singleton access to spaCy models."""

from __future__ import annotations
from typing import ClassVar
import spacy


class SingletonMeta(type):
    """Singleton metaclass for shared service objects."""

    _instances: ClassVar[dict[type, object]] = {}

    def __call__(cls, *args: object, **kwargs: object) -> object:
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
        """Return a loaded or blank spaCy model, cached by name.

        Args:
            model (str): The name of the spaCy model to load,
            or "blank:<language>" for a blank model.
        """
        if model not in self._models:
            if model.startswith("blank:"):
                language = model.split(":", 1)[1]
                self._models[model] = spacy.blank(language)
            else:
                self._models[model] = spacy.load(model)
        return self._models[model]

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
