"""LangChain sample code generator for RAG framework integration."""

from typing import Dict, Any, List, Optional
from pathlib import Path

from .integration_config import FRAMEWORK_CONFIGS


def create_restaurant_prompt():
    """Create a custom prompt template for restaurant queries."""
    from langchain.prompts import PromptTemplate
    
    template = """Use the following restaurant information to answer the question. 
    Pay attention to relationships between restaurants and locations mentioned in the context.
    
    Context: {context}
    
    Question: {question}
    
    Answer: Based on the restaurant information provided, """
    
    return PromptTemplate(
        template=template,
        input_variables=["context", "question"]
    )


def query_with_relationships(
    qa_chain, 
    query: str, 
    include_relationships: bool = True
) -> Dict[str, Any]:
    """Query with relationship awareness."""
    # Execute query
    result = qa_chain({"query": query})
    
    # Enhance result with relationship information
    if include_relationships:
        relationships = []
        for doc in result.get('source_documents', []):
            doc_relationships = doc.metadata.get('relationships', [])
            for rel in doc_relationships:
                if rel not in relationships:
                    relationships.append({
                        'type': rel.get('type'),
                        'entity_name': rel.get('entity_name'),
                        'entity_type': rel.get('entity_type')
                    })
        
        result['relationships'] = relationships
        result['relationship_count'] = len(relationships)
    
    return result


class LangChainSampleGenerator:
    """Generator for LangChain integration samples."""
    
    def __init__(self, version: str = "1.0.0"):
        self.framework = "langchain"
        self.version = version
        self.config = FRAMEWORK_CONFIGS.get("langchain", {})
    
    def generate(self, **kwargs) -> str:
        """Generate LangChain integration sample."""
        code = self._format_header(
            "LangChain Integration Example for RAG_Scraper Output",
            "Complete RAG implementation with multi-page relationship awareness"
        )
        
        code += self._generate_imports()
        code += self._generate_document_loader()
        code += self._generate_vectorstore_creation()
        code += self._generate_retrieval_chain()
        code += self._generate_relationship_aware_retrieval()
        code += self._generate_main_function()
        
        return code
    
    def _format_header(self, title: str, description: str) -> str:
        """Generate header comment."""
        return f'''"""
{title}
{description}

Generated for RAG_Scraper version {self.version}
Framework: {self.framework}
"""

'''
    
    def _format_imports(self, imports: List[str]) -> str:
        """Format import statements."""
        return '\n'.join(imports) + '\n\n'
    
    def _generate_imports(self) -> str:
        """Generate import statements."""
        imports = [
            "import json",
            "import yaml",
            "from pathlib import Path",
            "from typing import List, Dict, Any, Optional",
            "",
            "from langchain.document_loaders import TextLoader",
            "from langchain.text_splitter import RecursiveCharacterTextSplitter",
            "from langchain.embeddings import OpenAIEmbeddings",
            "from langchain.vectorstores import Chroma",
            "from langchain.chains import RetrievalQA",
            "from langchain.llms import OpenAI",
            "from langchain.schema import Document",
            ""
        ]
        return self._format_imports(imports)
    
    def _generate_document_loader(self) -> str:
        """Generate document loader class."""
        return '''class RestaurantDocumentLoader:
    """Custom loader for RAG_Scraper restaurant data with metadata preservation."""
    
    def __init__(self, data_directory: Path):
        self.data_directory = Path(data_directory)
        self.master_index = self._load_master_index()
    
    def _load_master_index(self) -> Dict[str, Any]:
        """Load master index for relationship information."""
        master_index_path = self.data_directory / "master_index.json"
        if master_index_path.exists():
            with open(master_index_path, 'r') as f:
                return json.load(f)
        return {}
    
    def load_documents(self) -> List[Document]:
        """Load all restaurant documents with enhanced metadata."""
        documents = []
        
        # Process each cuisine directory
        for cuisine_dir in self.data_directory.iterdir():
            if not cuisine_dir.is_dir():
                continue
            
            # Load cuisine-specific index
            cuisine_index = self._load_cuisine_index(cuisine_dir)
            
            # Process each restaurant file
            for restaurant_file in cuisine_dir.glob("*.txt"):
                try:
                    doc = self._load_restaurant_document(
                        restaurant_file, 
                        cuisine_dir.name,
                        cuisine_index
                    )
                    if doc:
                        documents.append(doc)
                except Exception as e:
                    print(f"Error loading {restaurant_file}: {e}")
                    continue
        
        print(f"Loaded {len(documents)} restaurant documents")
        return documents
    
    def _load_cuisine_index(self, cuisine_dir: Path) -> Dict[str, Any]:
        """Load cuisine-specific index."""
        index_path = cuisine_dir / f"{cuisine_dir.name}_index.json"
        if index_path.exists():
            with open(index_path, 'r') as f:
                return json.load(f)
        return {}
    
    def _load_restaurant_document(
        self, 
        file_path: Path, 
        cuisine: str,
        cuisine_index: Dict[str, Any]
    ) -> Optional[Document]:
        """Load individual restaurant document with metadata."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract YAML front matter
        metadata = self._extract_metadata(content)
        
        # Add cuisine and file information
        metadata.update({
            'cuisine': cuisine,
            'file_path': str(file_path),
            'source_type': 'restaurant_data'
        })
        
        # Add relationship information from index
        restaurant_id = metadata.get('restaurant_id')
        if restaurant_id and restaurant_id in cuisine_index.get('restaurants', {}):
            rest_info = cuisine_index['restaurants'][restaurant_id]
            metadata['relationships'] = rest_info.get('relationships', [])
            metadata['location'] = rest_info.get('location', {})
        
        # Remove YAML front matter from content
        clean_content = self._remove_yaml_frontmatter(content)
        
        return Document(
            page_content=clean_content,
            metadata=metadata
        )
    
    def _extract_metadata(self, content: str) -> Dict[str, Any]:
        """Extract metadata from YAML front matter."""
        metadata = {}
        if content.startswith('---'):
            lines = content.split('\\n')
            in_frontmatter = False
            for line in lines[1:]:
                if line.strip() == '---':
                    break
                if ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip()
        return metadata
    
    def _remove_yaml_frontmatter(self, content: str) -> str:
        """Remove YAML front matter from content."""
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                return parts[2].strip()
        return content


'''
    
    def _generate_vectorstore_creation(self) -> str:
        """Generate vectorstore creation functions."""
        return f'''def create_vectorstore(data_directory: Path, persist_directory: Optional[Path] = None) -> Chroma:
    """Create a vector store from restaurant data with relationship awareness."""
    # Load documents
    loader = RestaurantDocumentLoader(data_directory)
    documents = loader.load_documents()
    
    # Configure text splitter for semantic chunking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size={self.config.get('chunk_size', 1000)},
        chunk_overlap={self.config.get('chunk_overlap', 100)},
        separators=["\\n## ", "\\n### ", "\\n\\n", "\\n", ". ", " ", ""],
        keep_separator=True
    )
    
    # Split documents while preserving metadata
    split_docs = []
    for doc in documents:
        chunks = text_splitter.split_text(doc.page_content)
        for i, chunk in enumerate(chunks):
            # Create enhanced metadata for each chunk
            chunk_metadata = doc.metadata.copy()
            chunk_metadata.update({{
                'chunk_index': i,
                'total_chunks': len(chunks),
                'chunk_id': f"{{doc.metadata.get('restaurant_id', 'unknown')}}_chunk_{{i}}",
                'content_type': 'restaurant_description'
            }})
            
            # Add relationship context to metadata
            relationships = doc.metadata.get('relationships', [])
            if relationships:
                chunk_metadata['has_relationships'] = True
                chunk_metadata['relationship_count'] = len(relationships)
                chunk_metadata['relationship_types'] = list(set(rel.get('type') for rel in relationships))
            
            split_docs.append(Document(
                page_content=chunk,
                metadata=chunk_metadata
            ))
    
    print(f"Created {{len(split_docs)}} chunks from {{len(documents)}} documents")
    
    # Create embeddings
    embeddings = OpenAIEmbeddings()
    
    # Create vector store
    vectorstore_kwargs = {{
        'documents': split_docs,
        'embedding': embeddings,
        'collection_metadata': {{"hnsw:space": "cosine"}}
    }}
    
    if persist_directory:
        vectorstore_kwargs['persist_directory'] = str(persist_directory)
    
    vectorstore = Chroma.from_documents(**vectorstore_kwargs)
    
    if persist_directory:
        vectorstore.persist()
        print(f"Vector store persisted to {{persist_directory}}")
    
    return vectorstore


'''
    
    def _generate_retrieval_chain(self) -> str:
        """Generate retrieval chain creation."""
        return f'''def create_retrieval_chain(vectorstore: Chroma, **kwargs) -> RetrievalQA:
    """Create a retrieval chain with multi-page awareness."""
    # Configure retriever with relationship-aware search
    search_kwargs = {{
        'k': kwargs.get('k', 5),
        'fetch_k': kwargs.get('fetch_k', 10),
        'lambda_mult': kwargs.get('lambda_mult', 0.7)
    }}
    
    # Add metadata filtering if requested
    filter_dict = kwargs.get('filter')
    if filter_dict:
        search_kwargs['filter'] = filter_dict
    
    retriever = vectorstore.as_retriever(
        search_type="{self.config.get('search_type', 'mmr')}",
        search_kwargs=search_kwargs
    )
    
    # Create LLM
    llm = OpenAI(
        temperature=kwargs.get('temperature', 0),
        model_name=kwargs.get('model_name', 'gpt-3.5-turbo')
    )
    
    # Create QA chain with custom prompt for restaurant data
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type=kwargs.get('chain_type', 'stuff'),
        retriever=retriever,
        return_source_documents=True,
        verbose=kwargs.get('verbose', False),
        chain_type_kwargs={{
            'prompt': create_restaurant_prompt()
        }}
    )
    
    return qa_chain


def create_restaurant_prompt():
    """Create a custom prompt template for restaurant queries."""
    from langchain.prompts import PromptTemplate
    
    template = \"\"\"Use the following restaurant information to answer the question. 
    Pay attention to relationships between restaurants and locations mentioned in the context.
    
    Context: {{context}}
    
    Question: {{question}}
    
    Answer: Based on the restaurant information provided, \"\"\"
    
    return PromptTemplate(
        template=template,
        input_variables=["context", "question"]
    )


'''
    
    def _generate_relationship_aware_retrieval(self) -> str:
        """Generate relationship-aware retrieval functions."""
        return '''class RelationshipAwareRetriever:
    """Enhanced retriever that considers entity relationships."""
    
    def __init__(self, vectorstore: Chroma, master_index: Dict[str, Any]):
        self.vectorstore = vectorstore
        self.master_index = master_index
        self.base_retriever = vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={'k': 5, 'fetch_k': 10}
        )
    
    def retrieve_with_relationships(
        self, 
        query: str, 
        include_related: bool = True,
        max_related: int = 3
    ) -> List[Document]:
        """Retrieve documents with optional relationship expansion."""
        # Get initial results
        initial_docs = self.base_retriever.get_relevant_documents(query)
        
        if not include_related:
            return initial_docs
        
        # Expand with related entities
        expanded_docs = []
        seen_restaurant_ids = set()
        
        for doc in initial_docs:
            restaurant_id = doc.metadata.get('restaurant_id')
            if restaurant_id and restaurant_id not in seen_restaurant_ids:
                expanded_docs.append(doc)
                seen_restaurant_ids.add(restaurant_id)
                
                # Find related restaurants
                related_docs = self._find_related_documents(
                    doc, max_related - len(expanded_docs) + len(initial_docs)
                )
                for related_doc in related_docs:
                    related_id = related_doc.metadata.get('restaurant_id')
                    if related_id not in seen_restaurant_ids:
                        expanded_docs.append(related_doc)
                        seen_restaurant_ids.add(related_id)
        
        return expanded_docs[:max_related + len(initial_docs)]
    
    def _find_related_documents(self, doc: Document, max_count: int) -> List[Document]:
        """Find documents related to the given document."""
        related_docs = []
        relationships = doc.metadata.get('relationships', [])
        
        for relationship in relationships[:max_count]:
            if relationship.get('type') in ['parent', 'sibling']:
                # Search for related entity
                related_id = relationship.get('entity_id')
                if related_id:
                    related_doc = self._find_document_by_id(related_id)
                    if related_doc:
                        related_docs.append(related_doc)
        
        return related_docs
    
    def _find_document_by_id(self, entity_id: str) -> Optional[Document]:
        """Find document by entity ID."""
        # This is a simplified implementation
        # In practice, you might want to index documents by ID for faster lookup
        filter_dict = {'restaurant_id': entity_id}
        docs = self.vectorstore.similarity_search("", k=1, filter=filter_dict)
        return docs[0] if docs else None


def query_with_relationships(
    qa_chain: RetrievalQA, 
    query: str, 
    include_relationships: bool = True
) -> Dict[str, Any]:
    """Query with relationship awareness."""
    # Execute query
    result = qa_chain({"query": query})
    
    # Enhance result with relationship information
    if include_relationships:
        relationships = []
        for doc in result.get('source_documents', []):
            doc_relationships = doc.metadata.get('relationships', [])
            for rel in doc_relationships:
                if rel not in relationships:
                    relationships.append({
                        'type': rel.get('type'),
                        'entity_name': rel.get('entity_name'),
                        'entity_type': rel.get('entity_type')
                    })
        
        result['relationships'] = relationships
        result['relationship_count'] = len(relationships)
    
    return result


'''
    
    def _generate_main_function(self) -> str:
        """Generate main function with usage examples."""
        return '''def main():
    """Example usage of the LangChain integration."""
    # Configuration
    config = {
        'data_directory': Path('output/restaurants'),
        'persist_dir': Path('storage/langchain_vectorstore'),
        'chunk_size': 1000,
        'chunk_overlap': 100
    }
    
    try:
        # Create or load vector store
        print("Setting up vector store...")
        if config['persist_dir'].exists():
            print("Loading existing vector store...")
            embeddings = OpenAIEmbeddings()
            vectorstore = Chroma(
                persist_directory=str(config['persist_dir']),
                embedding_function=embeddings
            )
        else:
            print("Creating new vector store...")
            vectorstore = create_vectorstore(
                config['data_directory'], 
                config['persist_dir']
            )
        
        # Create retrieval chain
        print("Setting up retrieval chain...")
        qa_chain = create_retrieval_chain(
            vectorstore,
            temperature=0,
            verbose=True
        )
        
        # Example queries
        queries = [
            "What Italian restaurants are available?",
            "Find restaurants with outdoor seating in New York",
            "What are the menu items and prices at Luigi's?",
            "Show me family-friendly restaurants with good reviews",
            "Compare pasta dishes across different Italian restaurants"
        ]
        
        print("\\nExecuting sample queries...")
        for i, query in enumerate(queries, 1):
            print(f"\\n{'='*60}")
            print(f"Query {i}: {query}")
            print('='*60)
            
            # Execute query with relationships
            result = query_with_relationships(qa_chain, query)
            
            print(f"Answer: {result['result']}")
            
            # Show source information
            source_docs = result.get('source_documents', [])
            if source_docs:
                print(f"\\nSources ({len(source_docs)} documents):")
                for j, doc in enumerate(source_docs[:3], 1):
                    metadata = doc.metadata
                    print(f"  {j}. {metadata.get('restaurant_name', 'Unknown')}")
                    print(f"     Cuisine: {metadata.get('cuisine', 'Unknown')}")
                    print(f"     Location: {metadata.get('location', {}).get('city', 'Unknown')}")
                    print(f"     Source: {metadata.get('source_url', 'Unknown')}")
            
            # Show relationships
            relationships = result.get('relationships', [])
            if relationships:
                print(f"\\nRelated entities ({len(relationships)}):")
                for rel in relationships[:5]:
                    print(f"  - {rel['entity_name']} ({rel['type']} {rel['entity_type']})")
    
    except Exception as e:
        print(f"Error in main: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Set up environment
    import os
    
    # Ensure OpenAI API key is set
    if not os.getenv('OPENAI_API_KEY'):
        print("Warning: OPENAI_API_KEY environment variable not set")
        print("Please set it before running: export OPENAI_API_KEY='your-api-key'")
    
    main()
'''