from aoptk.sentence import Sentence
from aoptk.slide import Slide
from aoptk.slide_generator import SlideGenerator


class GenerateSlides(SlideGenerator):
    """Generate slides from sentences."""

    def generate_slides(self, sentences: list[Sentence], number_of_sentences: int = 3) -> list[Slide]:
        """Generate slides from a list of sentences.

        Args:
            sentences: A list of Sentence objects to generate slides from.
            number_of_sentences: The number of sentences to include in each slide.

        Returns:
            A list of Slide objects generated from the input sentences.
        """
        slides = []
        if len(sentences) < number_of_sentences:
            slide = Slide(sentences)
            slides.append(slide)
            return slides

        for i in range(len(sentences) - number_of_sentences + 1):
            slide_sentences = sentences[i : i + number_of_sentences]
            slide = Slide(slide_sentences)
            slides.append(slide)
        return slides
