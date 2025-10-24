import os
import pandas as pd
from pathlib import Path
import traceback
import time
import spacy
from Perplexity_Methods import setup_logging
from Visualization_Methods_ISM import (
    read_markdown_files,
    preprocess_text,
    perform_tfidf_and_dim_reduction,
    plot_dimension_reduction,
    plot_word_importance,
    plot_pca_eigen_terms,
    create_word_cloud,
    plot_topic_modeling,
    plot_heatmap,
    plot_term_network,
    plot_pca_3d,
    plot_pca_scree,
    plot_pca_cumulative_variance,
    plot_pca_loadings_heatmap,
    save_pca_top_features
)

# Define collections with specific patterns and paths
COLLECTIONS = {
    'research_profiles': {
        'path': Path('outputs/participants'),
        'pattern': '*/*_profile.md',
        'description': 'Research Profiles',
        'label_type': 'participant'
    },
    'fieldshift_analyses': {
        'path': Path('outputs/participants'),
        'pattern': '*/fieldshift/*_fieldshift.md',
        'description': 'FieldSHIFT Analyses',
        'label_type': 'participant_domain'
    },
    'catechism_proposals': {
        'path': Path('outputs/participants'),
        'pattern': '*/catechisms/*_catechism.md',
        'description': 'Domain-Specific Catechisms',
        'label_type': 'participant_domain'
    },
    'collaborative_proposals': {
        'path': Path('outputs/collaborative_proposals'),
        'pattern': '*_proposal.md',
        'description': 'Collaborative Proposals',
        'label_type': 'collaboration'
    }
}

def analyze_document_collection(base_path, output_folder, collection_name, nlp):
    """Analyze and visualize a collection of documents"""
    logger = setup_logging("visualization")
    
    try:
        # Create visualization output directory
        vis_path = Path('Visualizations') / collection_name
        vis_path.mkdir(parents=True, exist_ok=True)
        
        # Get collection info
        collection_info = COLLECTIONS[collection_name]
        
        # Read and preprocess documents
        documents, filenames, labels = read_markdown_files(
            collection_info['path'],
            collection_info['pattern']
        )
        
        if not documents:
            logger.warning(f"⚠️ No documents found for {collection_info['description']}")
            return
            
        logger.info(f"📚 Processing {len(documents)} {collection_info['description']}")
        
        # Preprocess texts
        preprocessed_docs = [preprocess_text(doc, nlp) for doc in documents]
        logger.info("✅ Completed text preprocessing")
        
        # Perform dimensionality reduction with adaptive n_components
        results = perform_tfidf_and_dim_reduction(preprocessed_docs)
        
        if results[0] is None:
            logger.error("❌ Dimensionality reduction failed")
            return
            
        pca_result, lsa_result, tsne_result, vectorizer, pca, lsa, tsne = results
        
        # Generate visualizations only if we have valid results
        if pca_result is not None:
            plot_dimension_reduction(
                pca_result, filenames, labels,
                f"{collection_name} PCA Visualization",
                f"{collection_name}_pca_plot.png",
                "PCA", vectorizer, pca, vis_path
            )
        
        if lsa_result is not None:
            plot_dimension_reduction(
                lsa_result, filenames, labels,
                f"{collection_name} LSA Visualization",
                f"{collection_name}_lsa_plot.png",
                "LSA", vectorizer, lsa, vis_path
            )
        
        # Only try t-SNE if we have enough samples and it was successful
        if tsne_result is not None:
            plot_dimension_reduction(
                tsne_result, filenames, labels,
                f"{collection_name} t-SNE Visualization",
                f"{collection_name}_tsne_plot.png",
                "t-SNE", vectorizer, tsne, vis_path
            )
        else:
            logger.info(f"Skipping t-SNE visualization for {collection_name} due to sample size")
        
        # Continue with other visualizations only if we have valid data
        if vectorizer is not None and pca is not None:
            # Word Importance Analysis
            plot_word_importance(
                vectorizer, pca,
                f"{collection_name} Word Importance Analysis",
                f"{collection_name}_word_importance.png",
                vis_path
            )
            
            # PCA Analysis
            plot_pca_eigen_terms(
                vectorizer, pca,
                f"{collection_name} PCA Eigenterm Analysis",
                f"{collection_name}_pca_eigenterms.png",
                vis_path
            )
            
            # Word Cloud
            create_word_cloud(
                preprocessed_docs,
                f"{collection_name} Word Cloud",
                f"{collection_name}_wordcloud.png",
                vis_path
            )
            
            # Topic Modeling
            plot_topic_modeling(
                vectorizer, vectorizer.fit_transform(preprocessed_docs),
                f"{collection_name} Topic Analysis",
                f"{collection_name}_topics.png",
                vis_path
            )
            
            # Term Network
            plot_term_network(
                vectorizer, vectorizer.fit_transform(preprocessed_docs),
                f"{collection_name} Term Network",
                f"{collection_name}_term_network.png",
                vis_path
            )
            
            # 3D PCA Visualization if we have enough components
            if pca_result.shape[1] >= 3:
                plot_pca_3d(
                    pca_result, labels,
                    vis_path
                )
            
            # Additional PCA Analysis
            plot_pca_scree(pca, vis_path)
            plot_pca_cumulative_variance(pca, vis_path)
            plot_pca_loadings_heatmap(pca, vectorizer, vis_path)
            save_pca_top_features(pca, vectorizer, vis_path)
            
            # Create heatmap of term frequencies
            plot_heatmap(
                vectorizer, vectorizer.fit_transform(preprocessed_docs),
                filenames,
                f"{collection_name} Term Frequency Heatmap",
                f"{collection_name}_term_heatmap.png",
                vis_path
            )
            
            logger.info(f"✅ Generated all visualizations for {collection_name}")
        else:
            logger.warning(f"⚠️ Skipping additional visualizations for {collection_name} due to invalid data")
        
        logger.info(f"✅ Completed visualization generation for {collection_name}")
        
    except Exception as e:
        logger.error(f"❌ Error analyzing {collection_name}: {e}")
        logger.error(traceback.format_exc())

def main():
    """Main function to orchestrate visualization generation."""
    logger = setup_logging("visualization")
    total_start_time = time.time()
    
    try:
        logger.info("🚀 Starting ISM visualization generation...")
        
        # Load spaCy model
        nlp = spacy.load('en_core_web_sm')
        
        # Create main visualization directory
        vis_base_path = Path('Visualizations')
        vis_base_path.mkdir(exist_ok=True)
        
        # Process each collection
        for collection_name, collection_info in COLLECTIONS.items():
            logger.info(f"\n📊 Processing {collection_info['description']}...")
            
            try:
                # Find all matching files for this collection
                base_path = Path(collection_info['path'])
                matching_files = list(base_path.glob(collection_info['pattern']))
                
                if not matching_files:
                    logger.warning(f"⚠️ No {collection_info['description']} found in {base_path}")
                    continue
                    
                logger.info(f"📚 Found {len(matching_files)} {collection_info['description']}")
                
                # Process the collection
                analyze_document_collection(
                    base_path,
                    vis_base_path,
                    collection_name,
                    nlp
                )
                
            except Exception as e:
                logger.error(f"❌ Error processing {collection_info['description']}: {e}")
                continue
        
        # Generate cross-collection visualizations
        logger.info("\n🔄 Generating cross-collection analyses...")
        
        # TODO: Add cross-collection visualization logic here
        
        total_time = time.time() - total_start_time
        logger.info(f"\n🎉 Visualization generation complete! Total time: {total_time:.2f} seconds")
        logger.info(f"📁 Visualizations saved in Visualizations/")
        
    except Exception as e:
        logger.error(f"❌ Fatal error in visualization generation: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
