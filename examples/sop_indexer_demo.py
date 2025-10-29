#!/usr/bin/env python3
"""
SOP Indexer Demo Script

This script demonstrates how to use the SOP Indexer for RAG + Guidance Mapping.
It shows how to:
1. Load and index SOP documents
2. Search for relevant SOP clauses
3. Generate reason-to-SOP mappings
4. Use both ChromaDB and FAISS backends

Usage:
    python examples/sop_indexer_demo.py
"""

import os
import sys
import tempfile
import yaml
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from utils.sop_indexer import SOPIndexer, RawDoc


def create_mock_documents():
    """Create mock SOP documents for demonstration"""
    return [
        RawDoc(
            filepath="/mock/sop_029014.pdf",
            title="029014 - Periodic Technical Complaints Review",
            content="""
            4.1.3 Monthly quality content review
            The review is limited to the evaluation of the following fields:
            - Error Code should be the most appropriate IMDRF code
            - Product information must be accurate and complete
            - Sampling plan must follow golden rules
            - UDI-DI must be properly populated
            
            4.2.1 Error Code Validation
            Error codes must be validated against IMDRF taxonomy.
            Incorrect error codes lead to regulatory non-compliance.
            The following error codes are commonly used:
            - A.1: Manufacturing issue
            - A.2: Design issue
            - A.3: Material issue
            
            4.3.1 Sampling Plan Requirements
            Sampling plans must be statistically valid and meet regulatory requirements.
            Golden rules for sampling plan determination:
            1. Sample size must be adequate
            2. Sampling must be representative
            3. Justification must be documented
            """,
            doc_type="pdf",
            checksum="mock_checksum_1",
            rev="15.A",
            effective_date="2024-10-01",
        ),
        RawDoc(
            filepath="/mock/attachment2.docx",
            title="Attachment 2 - Golden Rules for Determination of Sampling Plan",
            content="""
            Golden Rules for Sampling Plan
            
            1. Sampling must be statistically valid
            - Minimum sample size: 30 units
            - Confidence level: 95%
            - Margin of error: 5%
            
            2. Sample size must meet regulatory requirements
            - FDA requirements: 100 units minimum
            - EU MDR requirements: 50 units minimum
            - ISO 13485: 30 units minimum
            
            3. Sampling plan errors must be corrected immediately
            - Insufficient sample size
            - Non-representative sampling
            - Missing sampling justification
            - Incorrect statistical methods
            """,
            doc_type="docx",
            checksum="mock_checksum_2",
            rev="2.0",
            effective_date="2024-09-15",
        ),
        RawDoc(
            filepath="/mock/attachment3.pdf",
            title="Attachment 3 - TC Self-Review Dashboard User Guide",
            content="""
            Dashboard Error Types and Fixes
            
            PRE Not Escalated:
            - Error: PRE cases not properly escalated to regulatory team
            - Root cause: Missing escalation criteria or process failure
            - Fix: Ensure escalation criteria are met and process is followed
            - Prevention: Regular training on escalation procedures
            
            UDI-DI Missing:
            - Error: UDI-DI field is empty or contains invalid identifier
            - Root cause: Data entry error or missing UDI assignment
            - Fix: Populate UDI-DI with correct device identifier
            - Prevention: Automated UDI validation
            
            Misleading Product Info:
            - Error: Product information is misleading or inaccurate
            - Root cause: Outdated product data or copy-paste errors
            - Fix: Update product description to be accurate and current
            - Prevention: Regular data validation and review
            """,
            doc_type="pdf",
            checksum="mock_checksum_3",
            rev="1.5",
            effective_date="2024-08-20",
        ),
    ]


def create_mock_taxonomy():
    """Create mock taxonomy for demonstration"""
    return [
        {
            "id": "R_ERRCODE",
            "label": "Incorrect Error Code",
            "synonyms": [
                "wrong IMDRF A-code",
                "mis-coded error",
                "invalid error code",
                "incorrect classification",
            ],
        },
        {
            "id": "R_SAMPLING",
            "label": "Sampling Plan Error",
            "synonyms": [
                "insufficient sample",
                "sampling error",
                "sample size issue",
                "statistical sampling problem",
            ],
        },
        {
            "id": "R_PRE_NOT_ESCALATED",
            "label": "PRE Not Escalated",
            "synonyms": [
                "PRE escalation missing",
                "not escalated PRE",
                "escalation failure",
            ],
        },
        {
            "id": "R_UDI_MISSING",
            "label": "UDI-DI Missing",
            "synonyms": [
                "missing UDI",
                "UDI not populated",
                "device identifier missing",
            ],
        },
        {
            "id": "R_PRODUCT_INFO",
            "label": "Misleading Product Info",
            "synonyms": [
                "inaccurate product info",
                "misleading description",
                "wrong product data",
            ],
        },
    ]


def demo_chromadb():
    """Demonstrate ChromaDB backend"""
    print("🔍 ChromaDB Demo")
    print("=" * 50)

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create indexer with ChromaDB
        indexer = SOPIndexer(
            embeddings_dir=os.path.join(temp_dir, "chroma_embeddings"),
            model_name="all-MiniLM-L6-v2",
            use_faiss=False,
        )

        # Load mock documents
        docs = create_mock_documents()
        print(f"📄 Loaded {len(docs)} documents")

        # Chunk and index
        chunks = indexer.chunk_and_clean(docs)
        print(f"📝 Created {len(chunks)} chunks")

        indexer.embed_and_index(chunks)
        print("✅ Index built successfully")

        # Test searches
        test_queries = [
            "sampling plan error",
            "incorrect error code",
            "PRE not escalated",
            "UDI-DI missing",
        ]

        for query in test_queries:
            print(f"\n🔍 Query: '{query}'")
            results = indexer.find_relevant_sop(query, top_k=2)

            for i, result in enumerate(results, 1):
                print(f"  {i}. {result.sop_ref} (similarity: {result.score:.3f})")
                print(f"     {result.excerpt[:100]}...")


def demo_faiss():
    """Demonstrate FAISS backend"""
    print("\n🔍 FAISS Demo")
    print("=" * 50)

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create indexer with FAISS
        indexer = SOPIndexer(
            embeddings_dir=os.path.join(temp_dir, "faiss_embeddings"),
            model_name="all-MiniLM-L6-v2",
            use_faiss=True,
        )

        # Load mock documents
        docs = create_mock_documents()
        print(f"📄 Loaded {len(docs)} documents")

        # Chunk and index
        chunks = indexer.chunk_and_clean(docs)
        print(f"📝 Created {len(chunks)} chunks")

        indexer.embed_and_index(chunks)
        print("✅ Index built successfully")

        # Test searches
        test_queries = [
            "statistical sampling problem",
            "wrong IMDRF A-code",
            "escalation failure",
        ]

        for query in test_queries:
            print(f"\n🔍 Query: '{query}'")
            results = indexer.find_relevant_sop(query, top_k=2)

            for i, result in enumerate(results, 1):
                print(f"  {i}. {result.sop_ref} (similarity: {result.score:.3f})")
                print(f"     {result.excerpt[:100]}...")


def demo_mapping():
    """Demonstrate reason-to-SOP mapping generation"""
    print("\n🗺️  Reason-to-SOP Mapping Demo")
    print("=" * 50)

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create indexer
        indexer = SOPIndexer(
            embeddings_dir=os.path.join(temp_dir, "mapping_embeddings"),
            model_name="all-MiniLM-L6-v2",
            use_faiss=False,
        )

        # Load and index documents
        docs = create_mock_documents()
        chunks = indexer.chunk_and_clean(docs)
        indexer.embed_and_index(chunks)

        # Create mock taxonomy
        taxonomy = create_mock_taxonomy()
        taxonomy_path = os.path.join(temp_dir, "reasons.yml")
        with open(taxonomy_path, "w", encoding="utf-8") as f:
            yaml.dump(taxonomy, f, default_flow_style=False)

        # Generate mappings
        output_path = os.path.join(temp_dir, "reason_to_sop.yml")
        log_path = os.path.join(temp_dir, "rag_mapping.jsonl")

        print("🔄 Generating reason mappings...")
        indexer.generate_reason_mapping(
            taxonomy_yaml=taxonomy_path,
            output_path=output_path,
            log_path=log_path,
            top_k=3,
        )

        # Display results
        print("\n📊 Generated Mappings:")
        with open(output_path, "r", encoding="utf-8") as f:
            mappings = yaml.safe_load(f)

        for mapping in mappings:
            print(f"\n• {mapping['reason']}")
            print(f"  → {mapping['sop_ref']} (similarity: {mapping['similarity']:.3f})")
            print(f"  📝 {mapping['excerpt'][:150]}...")

        print(f"\n📈 Generated {len(mappings)} mappings")
        print(f"📋 Logs saved to: {log_path}")


def main():
    """Main demonstration function"""
    print("🚀 SOP Indexer (RAG + Guidance Mapping) Demo")
    print("=" * 60)

    try:
        # Demo ChromaDB
        demo_chromadb()

        # Demo FAISS
        demo_faiss()

        # Demo mapping generation
        demo_mapping()

        print("\n✅ Demo completed successfully!")
        print("\n💡 Key Features Demonstrated:")
        print("  • Document loading and chunking")
        print("  • Vector indexing with ChromaDB and FAISS")
        print("  • Semantic search with similarity scores")
        print("  • Reason-to-SOP mapping generation")
        print("  • Comprehensive logging and audit trails")

    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
