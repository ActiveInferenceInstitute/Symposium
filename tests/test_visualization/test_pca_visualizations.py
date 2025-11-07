#!/usr/bin/env python3
"""
Test script for enhanced PCA analysis visualizations.

This script demonstrates the comprehensive PCA analysis capabilities
added to the Symposium visualization module.
"""

import sys
from pathlib import Path
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA

# Add symposium to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from symposium.visualization.pca_analysis import PCAAnalyzer


def create_sample_documents():
    """Create sample documents for testing."""
    documents = [
        # Active Inference themed documents
        "Active inference is a theoretical framework explaining perception action and learning based on free energy principle",
        "The free energy principle suggests that biological systems minimize surprise through predictive processing",
        "Bayesian brain hypothesis proposes that the brain implements probabilistic inference for perception",
        "Predictive coding is a neural theory where the brain constantly predicts sensory input",
        "Markov blankets define boundaries between systems and their environment in active inference",
        
        # Neuroscience themed
        "Neural networks in the brain process information through synaptic connections and firing patterns",
        "Neuroscience research investigates brain structure function and cognitive processes",
        "Computational neuroscience models neural systems using mathematical and computational methods",
        
        # Machine Learning themed  
        "Machine learning algorithms learn patterns from data without explicit programming",
        "Deep learning uses artificial neural networks with multiple layers for complex pattern recognition",
        "Reinforcement learning trains agents through reward feedback in dynamic environments",
        
        # Cognitive Science themed
        "Cognitive science studies mental processes including attention memory and decision making",
        "Embodied cognition emphasizes the role of bodily experience in cognitive processes",
        "Consciousness and awareness remain fundamental questions in cognitive science research",
    ]
    
    labels = [
        "Active Inference", "Active Inference", "Active Inference", "Active Inference", "Active Inference",
        "Neuroscience", "Neuroscience", "Neuroscience",
        "Machine Learning", "Machine Learning", "Machine Learning",
        "Cognitive Science", "Cognitive Science", "Cognitive Science"
    ]
    
    return documents, labels


def main():
    """Run PCA analysis demonstration."""
    print("=" * 80)
    print("PCA Analysis Visualization Test")
    print("=" * 80)
    print()
    
    # Create output directory
    output_dir = Path("test_pca_output")
    output_dir.mkdir(exist_ok=True)
    
    # Generate sample data
    print("📄 Creating sample documents...")
    documents, labels = create_sample_documents()
    print(f"   Generated {len(documents)} documents")
    print()
    
    # TF-IDF vectorization
    print("🔢 Performing TF-IDF vectorization...")
    vectorizer = TfidfVectorizer(
        max_features=100,
        stop_words='english',
        min_df=1,
        ngram_range=(1, 2)
    )
    tfidf_matrix = vectorizer.fit_transform(documents)
    print(f"   TF-IDF shape: {tfidf_matrix.shape}")
    print()
    
    # PCA transformation
    print("📊 Performing PCA analysis...")
    n_components = min(10, len(documents) - 1)
    pca = PCA(n_components=n_components, random_state=42, whiten=True)
    reduced_matrix = pca.fit_transform(tfidf_matrix.toarray())
    print(f"   Reduced to {n_components} components")
    print(f"   Variance explained (first 3): {pca.explained_variance_ratio_[:3]}")
    print()
    
    # Create PCA analyzer
    print("🎨 Creating comprehensive PCA visualizations...")
    analyzer = PCAAnalyzer()
    
    # Generate all visualizations
    results = analyzer.create_comprehensive_pca_report(
        pca=pca,
        reduced_matrix=reduced_matrix,
        vectorizer=vectorizer,
        labels=labels,
        output_dir=output_dir,
        prefix="test_pca"
    )
    
    print()
    print("📋 Results Summary:")
    print("-" * 80)
    for viz_name, success in results.items():
        status = "✅" if success else "❌"
        print(f"   {status} {viz_name}")
    
    successful = sum(results.values())
    total = len(results)
    print()
    print(f"🎉 Completed: {successful}/{total} visualizations created successfully")
    print(f"📁 Output directory: {output_dir.absolute()}")
    print()
    
    # Display detailed analysis
    print("=" * 80)
    print("Detailed PCA Analysis")
    print("=" * 80)
    print()
    
    print("📊 Variance Explained by Each Component:")
    for i, var in enumerate(pca.explained_variance_ratio_[:5]):
        cumvar = np.sum(pca.explained_variance_ratio_[:i+1])
        print(f"   PC{i+1}: {var:6.2%} (cumulative: {cumvar:6.2%})")
    print()
    
    print("🔤 Top Terms for First 3 Components:")
    feature_names = vectorizer.get_feature_names_out()
    for i in range(min(3, n_components)):
        loadings = pca.components_[i]
        top_pos_idx = loadings.argsort()[-5:][::-1]
        top_neg_idx = loadings.argsort()[:5]
        
        print(f"\n   PC{i+1} ({pca.explained_variance_ratio_[i]:.2%} variance):")
        print(f"   Positive: {', '.join(feature_names[top_pos_idx])}")
        print(f"   Negative: {', '.join(feature_names[top_neg_idx])}")
    
    print()
    print("=" * 80)
    print("Test Complete!")
    print("=" * 80)
    print()
    print("To view the visualizations:")
    print(f"   open {output_dir.absolute()}")
    print()
    print("Generated files:")
    for file in sorted(output_dir.glob("*.png")):
        print(f"   - {file.name}")
    for file in sorted(output_dir.glob("*.csv")):
        print(f"   - {file.name}")
    print()


if __name__ == "__main__":
    main()

