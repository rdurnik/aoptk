from transformers import pipeline
from aoptk.chemical import Chemical
from aoptk.relationship import Relationship
from aoptk.effect import Effect
from aoptk.find_relationship import FindRelationships


class ZeroShotClassification(FindRelationships):
    threshold=0.85
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

    def __init__(self, text: str, chemicals: list[Chemical], effects: list[Effect]):
        threshold = self.threshold
        classifier = self.classifier
    
    def classify_relationships(self) -> list[Relationship]:
        for effect in effects:
            for chemical in chemicals:
                candidate_labels = [
                    f"{chemical} causes {effect}",
                    f"{chemical} does not cause {effect}",
                    f"{chemical} prevents {effect}",
                ]
                result = classifier(text, candidate_labels)
                label = result['labels'][0]
                score = result['scores'][0]
                is_true = score >= threshold

                # Data for testing purposes
                row_results_testing.append({
                    'chemical': chemical,
                    'text': text,
                    'label': label,
                    'score': score,
                    'is_true': is_true
                })

                # Data for final result
                if label == f"{chemical} causes {effect}" and is_true == True:
                    relationship = 'positive'
                    row_results.append({
                        'chemical': chemical,
                        'text': text,
                        'effect': effect,
                        'relationship': relationship        
                    })
                    row_final_results.append({
                        'chemical': chemical,
                        'relationship': relationship
                    })
                elif label == f"{chemical} does not cause {effect}" and is_true == True:
                    relationship = 'negative'
                    row_results.append({
                        'chemical': chemical,
                        'text': text,
                        'effect': effect,
                        'relationship': relationship
                    })
                    row_final_results.append({
                        'chemical': chemical,
                        'relationship': relationship
                    })