import math
from collections import defaultdict
from typing import List, Dict, Tuple, Any

# 1. Classe de Constantes (Données de Classe)
"""Ici, on définit les indices des colonnes CoNLL-U pour une lecture plus claire.
"""
class ConlluConstants:
    ID = 0
    FORM = 1
    LEMMA = 2
    UPOS = 3
    XPOS = 4
    FEATS = 5
    HEAD = 6
    DEPREL = 7
    DEPS = 8
    MISC = 9

    
# 2. Classe de Chargement (Encapsulation/SRP)

class CorpusLoader:
    """
    Encapsule la logique de lecture et de parsage des fichiers CoNLL-U.
    """
    
    def __init__(self, token_fields: List[int] = None):
        """
        Initialise le chargeur. Peut spécifier les champs à extraire si nécessaire.
        """
        # Utiliser les constantes de la classe ConlluConstants
        self.LEMMA_INDEX = ConlluConstants.LEMMA
        
    def __repr__(self):
        """Représentation formelle de l'objet """
        return f"CorpusLoader(LEMMA_INDEX={self.LEMMA_INDEX})"

    def load(self, filepath: str) -> List[List[List[str]]]:
        """
        On charge le fichier CoNLL-U et retourne une liste de phrases parsées.
        Chaque phrase est une liste de tokens.
        """
        sentences = []
        current_sentence = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    
                    if not line:
                        # Fin de phrase
                        if current_sentence:
                            sentences.append(current_sentence)
                            current_sentence = []
                        continue
    
                    if line.startswith('#'):
                        # Ligne de commentaire/métadonnée, ignorée.
                        continue
    
                    # Traitement des lignes de token
                    fields = line.split('\t')
                    # Validation du token
                    if len(fields) >= self.LEMMA_INDEX + 1 and fields[ConlluConstants.ID].isdigit():
                        current_sentence.append(fields)

            if current_sentence:
                sentences.append(current_sentence)
                
            return sentences

        except FileNotFoundError as e:
            # On réutilise l'exception standard, conforme au LSP
            # Ne pas introduire d'exception personnalisée inutile
            raise FileNotFoundError(f"Erreur: Le fichier spécifié est introuvable: {filepath}") from e

# 3. Classe d'Analyse (Encapsulation/SRP)

class BigramExtractor:
    """
    L'extraction des bigrammes de lemmes.
    """
    
    def __init__(self):
        self.LEMMA_INDEX = ConlluConstants.LEMMA

    def extract(self, sentences: List[List[List[str]]]) -> Dict[Tuple[str, str], int]:
        """
        On extrait les bigrammes de lemmes de toutes les phrases.
        """
        bigrams = defaultdict(int)
        for sentence in sentences:
            # Extraction des lemmes
            lemmas = [token[self.LEMMA_INDEX] for token in sentence if len(token) > self.LEMMA_INDEX]
            
            # Extraction des bigrammes
            for i in range(len(lemmas) - 1):
                bigram = (lemmas[i], lemmas[i+1])
                bigrams[bigram] += 1
                
        return bigrams

# 4. Classe Principale (Composition/Pipeline)

class ConlluAnalyzer:
    """
    C'est la classe principale pour s'occuper du chargement, l'analyse et l'affichage des résultats.
    On intègre un loader et un extractor.
    """
    
    def __init__(self, filepath: str, loader: CorpusLoader, extractor: BigramExtractor):
        """
        Constructeur pour les dépendances.
        """
        self.filepath = filepath
        self.loader = loader
        self.extractor = extractor
        self.corpus_sentences = None
        self.analysis_results = None
        
    def __str__(self):
        """Représentation lisible."""
        if self.corpus_sentences is None:
            return f"ConlluAnalyzer (Fichier: {self.filepath}) - Non analysé"
        return f"ConlluAnalyzer (Fichier: {self.filepath}) - {len(self.corpus_sentences)} phrases chargées."

    def run_analysis(self):
        """
        Exécute le pipeline d'analyse: charge, puis extrait.
        """
        # 1. Chargement
        print(f"1. Chargement du fichier: {self.filepath}...")
        self.corpus_sentences = self.loader.load(self.filepath)
        print(f"Chargement terminé. Nombre de phrases: {len(self.corpus_sentences)}")

        # 2. Extraction
        print(f"2. Exécution de l'extracteur {self.extractor.__class__.__name__}...")
        self.analysis_results = self.extractor.extract(self.corpus_sentences)
        print(f"Extraction terminée. Nombre de résultats uniques: {len(self.analysis_results)}")

    def get_top_results(self, n: int) -> List[Tuple[Any, int]]:
        """
        Les N éléments les plus fréquents des résultats d'analyse.
        (Même logique que l'ancienne fonction get_top_n, maintenant une méthode d'instance)
        """
        if self.analysis_results is None:
            raise ValueError("L'analyse doit être exécutée avant de récupérer les résultats.")
            
        # Triez les éléments par valeur (comptage)
        sorted_data = sorted(self.analysis_results.items(), key=lambda item: item[1], reverse=True)
        return sorted_data[:n]


# Script Principal

if __name__ == "__main__":
    
    FILEPATH = "fr_parisstories-ud-dev.conllu"

    try:
        # Instanciation des composants
        loader = CorpusLoader()
        extractor = BigramExtractor()
        
        # Composition des objets pour créer le pipeline
        analyzer = ConlluAnalyzer(FILEPATH, loader, extractor)
        
        # Exécution de l'analyse
        analyzer.run_analysis()

        # Affichage du top 10
        top_n = 10
        top_results = analyzer.get_top_results(top_n)
        
        print(f"\nTop {top_n} des résultats ({extractor.__class__.__name__}):")
        for bigram, count in top_results:
            # Formatage spécifique pour les bigrammes
            print(f"('{bigram[0]}', '{bigram[1]}'): {count}")
            
    except FileNotFoundError as e:
        # Exceptions
        print(f"\n[ERREUR FATALE] {e}")
    except ValueError as e:
        print(f"\n[ERREUR] {e}")
