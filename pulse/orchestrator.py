import time
import uuid
import json
import os
from pulse.logger import get_run_logger
from pulse.ingestion.scraper import fetch_reviews
from pulse.reasoning.scrubber import scrub_reviews
from pulse.reasoning.embedder import generate_embeddings
from pulse.reasoning.clusterer import cluster_embeddings, group_by_cluster
from pulse.reasoning.summarizer import summarize_all_clusters
from pulse.reasoning.validator import validate_all_summaries
from pulse.output.formatter import generate_docs_report, generate_email_teaser
from pulse.delivery.mcp_client import send_to_google_docs, send_email_draft

PRODUCT_TO_PACKAGE = {
    "Groww": "com.nextbillion.groww",
    # Add other mappings if needed
}

def run_pulse(product: str, week: str):
    """
    Main job runner that will eventually tie all phases together.
    """
    run_id = str(uuid.uuid4())
    logger = get_run_logger(run_id, product, week)
    
    logger.info("Starting Automated Weekly App Review Pulse")
    
    try:
        # Phase 2: Data Ingestion
        app_package = PRODUCT_TO_PACKAGE.get(product)
        if not app_package:
            raise ValueError(f"Unknown product mapping for: {product}")
            
        logger.info("Starting data ingestion")
        # Defaulting to 10 weeks back as per requirements window
        scraped_data, raw_data = fetch_reviews(app_package, weeks=10, logger=logger)
        
        # Dump to JSON files
        os.makedirs("data", exist_ok=True)
        with open("data/raw_reviews.json", "w", encoding="utf-8") as f:
            json.dump(raw_data, f, ensure_ascii=False, indent=2, default=str)
            
        with open("data/normalized_reviews.json", "w", encoding="utf-8") as f:
            json.dump(scraped_data, f, ensure_ascii=False, indent=2, default=str)
            
        logger.info(f"Ingestion complete. {len(scraped_data)} reviews saved to data/raw_reviews.json and data/normalized_reviews.json")
        
        # Phase 3: Reasoning & Analysis Engine
        logger.info("Starting reasoning and analysis: PII Scrubbing")
        scrubbed_reviews = scrub_reviews(scraped_data)
        
        logger.info("Starting reasoning and analysis: Generating Embeddings")
        embeddings = generate_embeddings(scrubbed_reviews)
        
        logger.info("Starting reasoning and analysis: Clustering")
        clustered_reviews = cluster_embeddings(embeddings, scrubbed_reviews)
        clusters = group_by_cluster(clustered_reviews)
        logger.info(f"Generated {len(clusters)} clusters.")
        
        logger.info("Starting reasoning and analysis: LLM Summarization")
        raw_summaries = summarize_all_clusters(clusters, logger)
        
        logger.info("Starting reasoning and analysis: Quote Validation")
        validated_summaries = validate_all_summaries(raw_summaries, clusters)
        
        # Save insights
        with open("data/insights.json", "w", encoding="utf-8") as f:
            json.dump(validated_summaries, f, ensure_ascii=False, indent=2)
            
        logger.info(f"Reasoning complete. Insights saved to data/insights.json")
        
        # Phase 4: Output Generation
        logger.info("Starting output generation")
        docs_report = generate_docs_report(validated_summaries, product, week)
        doc_id = os.environ.get("GOOGLE_DOC_ID", "")
        doc_link = f"https://docs.google.com/document/d/{doc_id}/edit" if doc_id else "https://docs.google.com/"
        email_teaser = generate_email_teaser(validated_summaries, product, week, doc_link)
        
        # Save formatted outputs for testing/audit
        with open("data/report.md", "w", encoding="utf-8") as f:
            f.write(docs_report)
            
        with open("data/email_teaser.txt", "w", encoding="utf-8") as f:
            f.write(email_teaser)
            
        logger.info("Output generation complete. Saved to data/report.md and data/email_teaser.txt")
        
        # Phase 5/6: MCP Delivery
        logger.info("Starting delivery via MCP servers")
        docs_success = send_to_google_docs(docs_report, logger)
        email_success = send_email_draft(f"{product} \u2014 App Review Pulse ({week})", email_teaser, logger)
        
        if docs_success and email_success:
            logger.info("Automated Weekly App Review Pulse completed and delivered successfully")
        else:
            logger.warning("Pulse completed but some MCP deliveries failed or were skipped due to missing environment variables.")
        
    except Exception as e:
        logger.error(f"Pulse execution failed: {str(e)}")
        raise
