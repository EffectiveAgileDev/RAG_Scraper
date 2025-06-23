"""Sample code generators for RAG framework integration."""

from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from pathlib import Path

from .integration_config import FRAMEWORK_CONFIGS, VERSION_INFO


class BaseSampleGenerator(ABC):
    """Base class for sample code generators."""
    
    def __init__(self, framework: str, version: str = "1.0.0"):
        self.framework = framework
        self.version = version
        self.config = FRAMEWORK_CONFIGS.get(framework, {})
    
    @abstractmethod
    def generate(self, **kwargs) -> str:
        """Generate sample code."""
        pass
    
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
    
    def _format_class_header(self, class_name: str, description: str) -> str:
        """Format class definition with docstring."""
        return f'''class {class_name}:
    """{description}"""
    
'''


class LangChainSampleGenerator(BaseSampleGenerator):
    """Generator for LangChain integration samples."""
    
    def __init__(self, version: str = "1.0.0"):
        super().__init__("langchain", version)
    
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


class LlamaIndexSampleGenerator(BaseSampleGenerator):
    """Generator for LlamaIndex integration samples."""
    
    def __init__(self, version: str = "1.0.0"):
        super().__init__("llamaindex", version)
    
    def generate(self, **kwargs) -> str:
        """Generate LlamaIndex integration sample."""
        code = self._format_header(
            "LlamaIndex Integration Example for RAG_Scraper Output", 
            "Complete RAG implementation with multi-page relationship awareness and optimized indexing"
        )
        
        code += self._generate_imports()
        code += self._generate_document_loader()
        code += self._generate_index_creation()
        code += self._generate_query_engine()
        code += self._generate_relationship_handler()
        code += self._generate_main_function()
        
        return code
    
    def _generate_imports(self) -> str:
        """Generate import statements."""
        imports = [
            "import json",
            "import yaml", 
            "from pathlib import Path",
            "from typing import List, Dict, Any, Optional",
            "",
            "from llama_index import (",
            "    Document,",
            "    VectorStoreIndex,", 
            "    ServiceContext,",
            "    StorageContext,",
            "    load_index_from_storage",
            ")",
            "from llama_index.node_parser import SimpleNodeParser",
            "from llama_index.embeddings import OpenAIEmbedding", 
            "from llama_index.llms import OpenAI",
            "from llama_index.query_engine import RetrieverQueryEngine",
            "from llama_index.retrievers import VectorIndexRetriever",
            "from llama_index.response_synthesizers import get_response_synthesizer",
            "from llama_index.schema import NodeWithScore, TextNode",
            ""
        ]
        return self._format_imports(imports)
    
    def _generate_document_loader(self) -> str:
        """Generate document loader class."""
        return '''class RestaurantDocumentLoader:
    """Load restaurant data with relationship preservation for LlamaIndex."""
    
    def __init__(self, data_directory: Path):
        self.data_directory = Path(data_directory)
        self.entity_map = {}  # Track entities for relationship queries
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
                        # Track entity for relationship queries
                        restaurant_id = doc.metadata.get('restaurant_id')
                        if restaurant_id:
                            self.entity_map[restaurant_id] = doc
                
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
        """Load individual restaurant document."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract and enhance metadata
        metadata = self._extract_metadata(content)
        metadata.update({
            'cuisine': cuisine,
            'file_path': str(file_path),
            'source_type': 'restaurant_data'
        })
        
        # Add relationship information
        restaurant_id = metadata.get('restaurant_id')
        if restaurant_id and restaurant_id in cuisine_index.get('restaurants', {}):
            rest_info = cuisine_index['restaurants'][restaurant_id]
            metadata['relationships'] = rest_info.get('relationships', [])
            metadata['location'] = rest_info.get('location', {})
        
        # Clean content
        clean_content = self._remove_yaml_frontmatter(content)
        
        return Document(
            text=clean_content,
            metadata=metadata,
            id_=restaurant_id or f"{cuisine}_{file_path.stem}"
        )
    
    def _extract_metadata(self, content: str) -> Dict[str, Any]:
        """Extract metadata from YAML front matter."""
        metadata = {}
        if content.startswith('---'):
            lines = content.split('\\n')
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
    
    def _generate_index_creation(self) -> str:
        """Generate index creation functions.""" 
        return f'''def create_index_with_config(
    documents: List[Document], 
    persist_dir: Optional[Path] = None
) -> VectorStoreIndex:
    """Create LlamaIndex with optimized configuration for restaurant data."""
    
    # Configure embeddings and LLM
    embed_model = OpenAIEmbedding()
    llm = OpenAI(
        temperature=0, 
        model="gpt-3.5-turbo"
    )
    
    # Configure service context with restaurant-optimized settings
    service_context = ServiceContext.from_defaults(
        embed_model=embed_model,
        llm=llm,
        chunk_size={self.config.get('chunk_size', 1000)},
        chunk_overlap={self.config.get('chunk_overlap', 100)}
    )
    
    # Configure node parser for semantic chunking
    node_parser = SimpleNodeParser.from_defaults(
        chunk_size={self.config.get('chunk_size', 1000)},
        chunk_overlap={self.config.get('chunk_overlap', 100)},
        include_metadata=True,
        include_prev_next_rel=True  # Preserve context between chunks
    )
    
    # Create storage context if persisting
    storage_context = None
    if persist_dir:
        storage_context = StorageContext.from_defaults(persist_dir=str(persist_dir))
    
    # Create index
    print("Creating VectorStoreIndex...")
    index = VectorStoreIndex.from_documents(
        documents,
        service_context=service_context,
        storage_context=storage_context,
        node_parser=node_parser,
        show_progress=True
    )
    
    # Persist if directory specified
    if persist_dir:
        index.storage_context.persist(persist_dir=str(persist_dir))
        print(f"Index persisted to {{persist_dir}}")
    
    return index


def load_or_create_index(
    data_directory: Path, 
    persist_dir: Path
) -> tuple[VectorStoreIndex, Dict[str, Document]]:
    """Load existing index or create new one."""
    
    # Load documents
    loader = RestaurantDocumentLoader(data_directory)
    documents = loader.load_documents()
    
    # Try to load existing index
    if persist_dir.exists():
        try:
            print("Loading existing index...")
            storage_context = StorageContext.from_defaults(persist_dir=str(persist_dir))
            
            # Configure service context to match original
            embed_model = OpenAIEmbedding()
            llm = OpenAI(temperature=0, model="gpt-3.5-turbo")
            service_context = ServiceContext.from_defaults(
                embed_model=embed_model,
                llm=llm
            )
            
            index = load_index_from_storage(
                storage_context=storage_context,
                service_context=service_context
            )
            print("Successfully loaded existing index")
            
        except Exception as e:
            print(f"Failed to load existing index: {{e}}")
            print("Creating new index...")
            index = create_index_with_config(documents, persist_dir)
    else:
        print("Creating new index...")
        index = create_index_with_config(documents, persist_dir)
    
    return index, loader.entity_map


'''
    
    def _generate_query_engine(self) -> str:
        """Generate query engine creation."""
        return f'''def create_query_engine(
    index: VectorStoreIndex, 
    entity_map: Dict[str, Document],
    **kwargs
) -> RetrieverQueryEngine:
    """Create query engine with multi-page awareness."""
    
    # Configure retriever with relationship awareness
    retriever = RelationshipAwareRetriever(
        index=index,
        entity_map=entity_map,
        similarity_top_k=kwargs.get('similarity_top_k', 5),
        include_relationships=kwargs.get('include_relationships', True)
    )
    
    # Configure response synthesizer
    response_synthesizer = get_response_synthesizer(
        response_mode=kwargs.get('response_mode', '{self.config.get('response_mode', 'tree_summarize')}'),
        use_async=kwargs.get('use_async', False),
        streaming=kwargs.get('streaming', False)
    )
    
    # Create query engine
    query_engine = RetrieverQueryEngine(
        retriever=retriever,
        response_synthesizer=response_synthesizer
    )
    
    return query_engine


class RelationshipAwareRetriever:
    """Custom retriever that considers entity relationships."""
    
    def __init__(
        self, 
        index: VectorStoreIndex, 
        entity_map: Dict[str, Document],
        similarity_top_k: int = 5,
        include_relationships: bool = True
    ):
        self.index = index
        self.entity_map = entity_map
        self.similarity_top_k = similarity_top_k
        self.include_relationships = include_relationships
        
        # Base retriever
        self.base_retriever = VectorIndexRetriever(
            index=index,
            similarity_top_k=similarity_top_k
        )
    
    def retrieve(self, query_str: str) -> List[NodeWithScore]:
        """Retrieve with optional relationship expansion."""
        # Get initial results
        initial_nodes = self.base_retriever.retrieve(query_str)
        
        if not self.include_relationships:
            return initial_nodes
        
        # Expand with related entities
        expanded_nodes = []
        seen_ids = set()
        
        for node_with_score in initial_nodes:
            node = node_with_score.node
            
            # Add original node
            if node.id_ not in seen_ids:
                expanded_nodes.append(node_with_score)
                seen_ids.add(node.id_)
            
            # Find and add related entities
            relationships = node.metadata.get('relationships', [])
            for rel in relationships:
                if rel.get('type') in ['parent', 'sibling'] and rel.get('entity_id') not in seen_ids:
                    related_node = self._create_node_from_entity(rel.get('entity_id'))
                    if related_node:
                        # Lower score for related entities
                        related_node_with_score = NodeWithScore(
                            node=related_node,
                            score=node_with_score.score * 0.8
                        )
                        expanded_nodes.append(related_node_with_score)
                        seen_ids.add(rel.get('entity_id'))
        
        # Limit total results
        return expanded_nodes[:self.similarity_top_k * 2]
    
    def _create_node_from_entity(self, entity_id: str) -> Optional[TextNode]:
        """Create node from entity in entity map."""
        if entity_id in self.entity_map:
            doc = self.entity_map[entity_id]
            return TextNode(
                text=doc.text,
                metadata=doc.metadata,
                id_=entity_id
            )
        return None


'''
    
    def _generate_relationship_handler(self) -> str:
        """Generate relationship handling functions."""
        return '''def handle_batch_queries(
    query_engine: RetrieverQueryEngine, 
    queries: List[str]
) -> List[Dict[str, Any]]:
    """Handle multiple queries efficiently with relationship context."""
    results = []
    
    for query in queries:
        try:
            print(f"\\nProcessing: {query}")
            response = query_engine.query(query)
            
            # Extract source information with relationships
            sources = []
            relationships = []
            
            for node in response.source_nodes:
                # Source info
                metadata = node.node.metadata
                sources.append({
                    'restaurant': metadata.get('restaurant_name', 'Unknown'),
                    'cuisine': metadata.get('cuisine', 'Unknown'),
                    'location': metadata.get('location', {}),
                    'score': node.score
                })
                
                # Relationship info
                node_relationships = metadata.get('relationships', [])
                for rel in node_relationships:
                    if rel not in relationships:
                        relationships.append({
                            'type': rel.get('type'),
                            'entity_name': rel.get('entity_name'),
                            'entity_type': rel.get('entity_type')
                        })
            
            results.append({
                'query': query,
                'response': str(response),
                'sources': sources,
                'relationships': relationships,
                'source_count': len(response.source_nodes)
            })
            
        except Exception as e:
            print(f"Error processing query '{query}': {e}")
            results.append({
                'query': query,
                'error': str(e)
            })
    
    return results


def analyze_restaurant_relationships(entity_map: Dict[str, Document]) -> Dict[str, Any]:
    """Analyze relationship patterns in the dataset."""
    analysis = {
        'total_restaurants': len(entity_map),
        'relationship_types': {},
        'cuisine_distribution': {},
        'location_distribution': {},
        'restaurants_with_relationships': 0
    }
    
    for restaurant_id, doc in entity_map.items():
        metadata = doc.metadata
        
        # Cuisine analysis
        cuisine = metadata.get('cuisine', 'Unknown')
        analysis['cuisine_distribution'][cuisine] = analysis['cuisine_distribution'].get(cuisine, 0) + 1
        
        # Location analysis
        location = metadata.get('location', {})
        city = location.get('city', 'Unknown')
        analysis['location_distribution'][city] = analysis['location_distribution'].get(city, 0) + 1
        
        # Relationship analysis
        relationships = metadata.get('relationships', [])
        if relationships:
            analysis['restaurants_with_relationships'] += 1
            
            for rel in relationships:
                rel_type = rel.get('type', 'unknown')
                analysis['relationship_types'][rel_type] = analysis['relationship_types'].get(rel_type, 0) + 1
    
    return analysis


'''
    
    def _generate_main_function(self) -> str:
        """Generate main function with usage examples."""
        return '''def main():
    """Example usage of LlamaIndex integration."""
    # Configuration
    config = {
        'data_directory': Path('output/restaurants'),
        'persist_dir': Path('storage/llamaindex_vectorstore'),
        'similarity_top_k': 5,
        'response_mode': 'tree_summarize'
    }
    
    try:
        # Load or create index
        print("Setting up LlamaIndex...")
        index, entity_map = load_or_create_index(
            config['data_directory'], 
            config['persist_dir']
        )
        
        # Analyze dataset
        print("\\nAnalyzing restaurant dataset...")
        analysis = analyze_restaurant_relationships(entity_map)
        print(f"Dataset contains {analysis['total_restaurants']} restaurants")
        print(f"Cuisines: {list(analysis['cuisine_distribution'].keys())}")
        print(f"Restaurants with relationships: {analysis['restaurants_with_relationships']}")
        
        # Create query engine
        print("\\nSetting up query engine...")
        query_engine = create_query_engine(
            index=index,
            entity_map=entity_map,
            similarity_top_k=config['similarity_top_k'],
            response_mode=config['response_mode'],
            include_relationships=True
        )
        
        # Example queries
        queries = [
            "What Italian restaurants serve pizza and pasta?",
            "Find family-friendly restaurants with outdoor seating",
            "Compare menu prices across different cuisines", 
            "Which restaurants have the best reviews in New York?",
            "Show me restaurants that are part of the same directory or chain",
            "What are the most popular dishes across all restaurants?"
        ]
        
        print("\\nExecuting sample queries...")
        results = handle_batch_queries(query_engine, queries)
        
        # Display results
        for result in results:
            print(f"\\n{'='*80}")
            print(f"Query: {result['query']}")
            print('='*80)
            
            if 'error' in result:
                print(f"Error: {result['error']}")
                continue
            
            print(f"Response: {result['response']}")
            
            # Show sources
            sources = result.get('sources', [])
            if sources:
                print(f"\\nSources ({len(sources)} restaurants):")
                for i, source in enumerate(sources[:3], 1):
                    location = source.get('location', {})
                    print(f"  {i}. {source['restaurant']} ({source['cuisine']})")
                    print(f"     Location: {location.get('city', 'Unknown')}, {location.get('state', 'Unknown')}")
                    print(f"     Relevance Score: {source['score']:.3f}")
            
            # Show relationships
            relationships = result.get('relationships', [])
            if relationships:
                print(f"\\nRelated Entities ({len(relationships)}):")
                for rel in relationships[:5]:
                    print(f"  - {rel['entity_name']} ({rel['type']} {rel['entity_type']})")
        
        # Performance metrics
        print(f"\\n{'='*80}")
        print("Performance Summary")
        print('='*80)
        successful_queries = [r for r in results if 'error' not in r]
        print(f"Successful queries: {len(successful_queries)}/{len(queries)}")
        
        avg_sources = sum(r.get('source_count', 0) for r in successful_queries) / len(successful_queries) if successful_queries else 0
        print(f"Average sources per query: {avg_sources:.1f}")
        
        total_relationships = sum(len(r.get('relationships', [])) for r in successful_queries)
        print(f"Total relationships found: {total_relationships}")
    
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


class ValidationScriptGenerator(BaseSampleGenerator):
    """Generator for validation scripts."""
    
    def __init__(self, version: str = "1.0.0"):
        super().__init__("validation", version)
    
    def generate(self, **kwargs) -> str:
        """Generate validation script."""
        code = self._format_header(
            "Schema validation script for RAG_Scraper data",
            "Validates restaurant data against JSON Schema with comprehensive error reporting"
        )
        
        code += self._generate_validation_script()
        return code
    
    def _generate_validation_script(self) -> str:
        """Generate complete validation script."""
        return '''#!/usr/bin/env python3

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import argparse

try:
    from jsonschema import validate, ValidationError, Draft7Validator
    from jsonschema.exceptions import SchemaError
except ImportError:
    print("Error: jsonschema package not found. Install with: pip install jsonschema")
    sys.exit(1)


class RestaurantDataValidator:
    """Comprehensive validator for restaurant data."""
    
    def __init__(self, schema_dir: Path):
        self.schema_dir = Path(schema_dir)
        self.schemas = self._load_schemas()
        self.errors = []
        self.warnings = []
    
    def _load_schemas(self) -> Dict[str, Dict]:
        """Load all validation schemas."""
        schemas = {}
        
        # Load restaurant data schema
        restaurant_schema_path = self.schema_dir / "restaurant_data.schema.json"
        if restaurant_schema_path.exists():
            with open(restaurant_schema_path, 'r') as f:
                schemas['restaurant'] = json.load(f)
        else:
            raise FileNotFoundError(f"Restaurant schema not found: {restaurant_schema_path}")
        
        # Load configuration schema
        config_schema_path = self.schema_dir / "config.schema.json"
        if config_schema_path.exists():
            with open(config_schema_path, 'r') as f:
                schemas['config'] = json.load(f)
        
        return schemas
    
    def validate_file(self, data_path: Path) -> Tuple[bool, List[str], List[str]]:
        """Validate a single data file."""
        self.errors.clear()
        self.warnings.clear()
        
        try:
            with open(data_path, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON: {e}")
            return False, self.errors, self.warnings
        except Exception as e:
            self.errors.append(f"Error reading file: {e}")
            return False, self.errors, self.warnings
        
        # Determine data type and validate
        if self._is_batch_result(data):
            return self._validate_batch_result(data)
        elif self._is_restaurant_list(data):
            return self._validate_restaurant_list(data)
        elif self._is_single_restaurant(data):
            return self._validate_single_restaurant(data)
        elif self._is_config_data(data):
            return self._validate_config(data)
        else:
            self.errors.append("Unable to determine data type")
            return False, self.errors, self.warnings
    
    def _is_batch_result(self, data: Any) -> bool:
        """Check if data is a batch result."""
        return (isinstance(data, dict) and 
                'restaurants' in data and 
                'metadata' in data)
    
    def _is_restaurant_list(self, data: Any) -> bool:
        """Check if data is a list of restaurants."""
        return (isinstance(data, list) and 
                len(data) > 0 and 
                isinstance(data[0], dict) and 
                'restaurant_id' in data[0])
    
    def _is_single_restaurant(self, data: Any) -> bool:
        """Check if data is a single restaurant."""
        return (isinstance(data, dict) and 
                'restaurant_id' in data and 
                'restaurant_name' in data)
    
    def _is_config_data(self, data: Any) -> bool:
        """Check if data is configuration."""
        return (isinstance(data, dict) and 
                'chunk_settings' in data)
    
    def _validate_batch_result(self, data: Dict) -> Tuple[bool, List[str], List[str]]:
        """Validate batch result data."""
        # Validate individual restaurants
        restaurants = data.get('restaurants', [])
        valid_count = 0
        
        for i, restaurant in enumerate(restaurants):
            try:
                validate(instance=restaurant, schema=self.schemas['restaurant'])
                valid_count += 1
                print(f"✓ Restaurant {i+1}: {restaurant.get('restaurant_name', 'Unknown')}")
            except ValidationError as e:
                self.errors.append(f"Restaurant {i+1} ({restaurant.get('restaurant_name', 'Unknown')}): {e.message}")
                print(f"✗ Restaurant {i+1}: {e.message}")
        
        # Check metadata
        metadata = data.get('metadata', {})
        if not isinstance(metadata, dict):
            self.errors.append("Metadata must be an object")
        else:
            # Validate metadata fields
            required_meta_fields = ['extraction_id', 'total_pages', 'successful_pages', 'failed_pages']
            for field in required_meta_fields:
                if field not in metadata:
                    self.warnings.append(f"Missing metadata field: {field}")
        
        # Summary
        total_restaurants = len(restaurants)
        print(f"\\nValidation Summary: {valid_count}/{total_restaurants} restaurants valid")
        
        return len(self.errors) == 0, self.errors, self.warnings
    
    def _validate_restaurant_list(self, data: List) -> Tuple[bool, List[str], List[str]]:
        """Validate list of restaurants."""
        valid_count = 0
        
        for i, restaurant in enumerate(data):
            try:
                validate(instance=restaurant, schema=self.schemas['restaurant'])
                valid_count += 1
                print(f"✓ Restaurant {i+1}: {restaurant.get('restaurant_name', 'Unknown')}")
            except ValidationError as e:
                self.errors.append(f"Restaurant {i+1}: {e.message}")
                print(f"✗ Restaurant {i+1}: {e.message}")
        
        print(f"\\nValidation Summary: {valid_count}/{len(data)} restaurants valid")
        return len(self.errors) == 0, self.errors, self.warnings
    
    def _validate_single_restaurant(self, data: Dict) -> Tuple[bool, List[str], List[str]]:
        """Validate single restaurant."""
        try:
            validate(instance=data, schema=self.schemas['restaurant'])
            print(f"✓ Restaurant valid: {data.get('restaurant_name', 'Unknown')}")
            return True, [], []
        except ValidationError as e:
            self.errors.append(e.message)
            print(f"✗ Restaurant invalid: {e.message}")
            return False, self.errors, self.warnings
    
    def _validate_config(self, data: Dict) -> Tuple[bool, List[str], List[str]]:
        """Validate configuration data."""
        if 'config' not in self.schemas:
            self.warnings.append("No configuration schema available")
            return True, [], self.warnings
        
        try:
            validate(instance=data, schema=self.schemas['config'])
            print("✓ Configuration valid")
            return True, [], []
        except ValidationError as e:
            self.errors.append(f"Configuration invalid: {e.message}")
            print(f"✗ Configuration invalid: {e.message}")
            return False, self.errors, self.warnings
    
    def validate_directory(self, directory: Path) -> Dict[str, Any]:
        """Validate all JSON files in directory."""
        results = {
            'total_files': 0,
            'valid_files': 0,
            'invalid_files': 0,
            'file_results': {}
        }
        
        for json_file in directory.rglob("*.json"):
            results['total_files'] += 1
            print(f"\\nValidating: {json_file}")
            
            is_valid, errors, warnings = self.validate_file(json_file)
            
            results['file_results'][str(json_file)] = {
                'valid': is_valid,
                'errors': errors,
                'warnings': warnings
            }
            
            if is_valid:
                results['valid_files'] += 1
            else:
                results['invalid_files'] += 1
        
        return results


def main():
    """Main validation function."""
    parser = argparse.ArgumentParser(
        description="Validate RAG_Scraper data against JSON schemas"
    )
    parser.add_argument(
        'data_path',
        type=Path,
        help="Path to JSON file or directory to validate"
    )
    parser.add_argument(
        '--schema-dir',
        type=Path,
        default=Path(__file__).parent.parent / "schemas",
        help="Directory containing JSON schemas"
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.data_path.exists():
        print(f"Error: Data path not found: {args.data_path}")
        sys.exit(1)
    
    if not args.schema_dir.exists():
        print(f"Error: Schema directory not found: {args.schema_dir}")
        sys.exit(1)
    
    # Create validator
    try:
        validator = RestaurantDataValidator(args.schema_dir)
    except Exception as e:
        print(f"Error initializing validator: {e}")
        sys.exit(1)
    
    # Validate
    try:
        if args.data_path.is_file():
            # Validate single file
            print(f"Validating file: {args.data_path}")
            is_valid, errors, warnings = validator.validate_file(args.data_path)
            
            if warnings:
                print("\\nWarnings:")
                for warning in warnings:
                    print(f"  - {warning}")
            
            if errors:
                print("\\nErrors:")
                for error in errors:
                    print(f"  - {error}")
            
            if is_valid:
                print("\\n✓ Validation successful!")
                sys.exit(0)
            else:
                print("\\n✗ Validation failed!")
                sys.exit(1)
        
        elif args.data_path.is_dir():
            # Validate directory
            print(f"Validating directory: {args.data_path}")
            results = validator.validate_directory(args.data_path)
            
            print(f"\\n{'='*60}")
            print("VALIDATION SUMMARY")
            print('='*60)
            print(f"Total files: {results['total_files']}")
            print(f"Valid files: {results['valid_files']}")
            print(f"Invalid files: {results['invalid_files']}")
            
            if results['invalid_files'] > 0:
                print("\\nFiles with errors:")
                for file_path, result in results['file_results'].items():
                    if not result['valid']:
                        print(f"  - {file_path}")
                        for error in result['errors'][:3]:  # Show first 3 errors
                            print(f"    {error}")
            
            # Exit code based on results
            if results['invalid_files'] == 0:
                print("\\n✓ All files valid!")
                sys.exit(0)
            else:
                print(f"\\n✗ {results['invalid_files']} files failed validation!")
                sys.exit(1)
        
        else:
            print(f"Error: Path must be a file or directory: {args.data_path}")
            sys.exit(1)
    
    except Exception as e:
        print(f"Validation error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
'''