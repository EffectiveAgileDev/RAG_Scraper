"""LlamaIndex integration sample generator for RAG_Scraper output."""

import json
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    from llama_index import (
        Document,
        VectorStoreIndex,
        ServiceContext,
        StorageContext,
        load_index_from_storage
    )
    from llama_index.node_parser import SimpleNodeParser
    from llama_index.embeddings import OpenAIEmbedding
    from llama_index.llms import OpenAI
    from llama_index.query_engine import RetrieverQueryEngine
    from llama_index.retrievers import VectorIndexRetriever
    from llama_index.response_synthesizers import get_response_synthesizer
    from llama_index.schema import NodeWithScore, TextNode
    LLAMA_INDEX_AVAILABLE = True
except ImportError:
    # Provide stub classes when LlamaIndex is not available
    LLAMA_INDEX_AVAILABLE = False
    Document = object
    VectorStoreIndex = object
    ServiceContext = object
    StorageContext = object
    load_index_from_storage = lambda: None
    SimpleNodeParser = object
    OpenAIEmbedding = object
    OpenAI = object
    RetrieverQueryEngine = object
    VectorIndexRetriever = object
    get_response_synthesizer = lambda: None
    NodeWithScore = object
    TextNode = object

from .integration_config import FRAMEWORK_CONFIGS
from .sample_generator import BaseSampleGenerator


class RestaurantDocumentLoader:
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
            lines = content.split('\n')
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


def create_index_with_config(
    documents: List[Document], 
    persist_dir: Optional[Path] = None
) -> VectorStoreIndex:
    """Create LlamaIndex with optimized configuration for restaurant data."""
    
    if not LLAMA_INDEX_AVAILABLE:
        raise ImportError("LlamaIndex is not installed. Please install it with: pip install llama-index")
    
    # Get configuration
    config = FRAMEWORK_CONFIGS.get('llamaindex', {})
    
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
        chunk_size=config.get('chunk_size', 1000),
        chunk_overlap=config.get('chunk_overlap', 100)
    )
    
    # Configure node parser for semantic chunking
    node_parser = SimpleNodeParser.from_defaults(
        chunk_size=config.get('chunk_size', 1000),
        chunk_overlap=config.get('chunk_overlap', 100),
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
        print(f"Index persisted to {persist_dir}")
    
    return index


def load_or_create_index(
    data_directory: Path, 
    persist_dir: Path
) -> tuple[VectorStoreIndex, Dict[str, Document]]:
    """Load existing index or create new one."""
    
    if not LLAMA_INDEX_AVAILABLE:
        raise ImportError("LlamaIndex is not installed. Please install it with: pip install llama-index")
    
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
            print(f"Failed to load existing index: {e}")
            print("Creating new index...")
            index = create_index_with_config(documents, persist_dir)
    else:
        print("Creating new index...")
        index = create_index_with_config(documents, persist_dir)
    
    return index, loader.entity_map


def create_query_engine(
    index: VectorStoreIndex, 
    entity_map: Dict[str, Document],
    **kwargs
) -> RetrieverQueryEngine:
    """Create query engine with multi-page awareness."""
    
    if not LLAMA_INDEX_AVAILABLE:
        raise ImportError("LlamaIndex is not installed. Please install it with: pip install llama-index")
    
    # Get configuration
    config = FRAMEWORK_CONFIGS.get('llamaindex', {})
    
    # Configure retriever with relationship awareness
    retriever = RelationshipAwareRetriever(
        index=index,
        entity_map=entity_map,
        similarity_top_k=kwargs.get('similarity_top_k', 5),
        include_relationships=kwargs.get('include_relationships', True)
    )
    
    # Configure response synthesizer
    response_synthesizer = get_response_synthesizer(
        response_mode=kwargs.get('response_mode', config.get('response_mode', 'tree_summarize')),
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
        if not LLAMA_INDEX_AVAILABLE:
            raise ImportError("LlamaIndex is not installed. Please install it with: pip install llama-index")
        
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


def handle_batch_queries(
    query_engine: RetrieverQueryEngine, 
    queries: List[str]
) -> List[Dict[str, Any]]:
    """Handle multiple queries efficiently with relationship context."""
    results = []
    
    for query in queries:
        try:
            print(f"\nProcessing: {query}")
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
    
    if not LLAMA_INDEX_AVAILABLE:
        raise ImportError("LlamaIndex is not installed. Please install it with: pip install llama-index")
    
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
        if not LLAMA_INDEX_AVAILABLE:
            raise ImportError("LlamaIndex is not installed. Please install it with: pip install llama-index")
        
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