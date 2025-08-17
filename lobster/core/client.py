"""
Clean Agent Client Interface for LangGraph Multi-Agent System.
Provides a simple, extensible interface for both CLI and future UI implementations.
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Generator
from datetime import datetime
import json

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langgraph.checkpoint.memory import InMemorySaver

from lobster.core.data_manager import DataManager
from lobster.agents.graph import create_bioinformatics_graph

# Configure logging
logger = logging.getLogger(__name__)


class AgentClient:
    def __init__(
        self,
        data_manager: Optional[DataManager] = None,
        session_id: str = None,
        enable_reasoning: bool = True,
        enable_langfuse: bool = False,
        workspace_path: Optional[Path] = None,
        custom_callbacks: Optional[List] = None,  # Changed from List[Callable]
        manual_model_params: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the agent client.
        
        Args:
            data_manager: Data manager instance (creates new if None)
            session_id: Unique session identifier
            enable_reasoning: Show agent reasoning/thinking process
            enable_langfuse: Enable Langfuse debugging callback
            workspace_path: Path to workspace for file operations
            custom_callbacks: Additional callback handlers
        """
        # Set up session
        self.session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.enable_reasoning = enable_reasoning
        
        # Set up workspace
        self.workspace_path = workspace_path or Path.cwd()
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize data manager
        self.data_manager = data_manager or DataManager()
        
        # Set up callbacks
        self.callbacks = []
        if enable_langfuse and os.getenv("LANGFUSE_PUBLIC_KEY"):
            from langfuse.langchain import CallbackHandler as LangfuseCallback
            self.callbacks.append(LangfuseCallback())
        if custom_callbacks:
            self.callbacks.extend(custom_callbacks)
        
        self.checkpointer = InMemorySaver()
        # Initialize graph - pass all callbacks
        self.graph = create_bioinformatics_graph(
            data_manager=self.data_manager,
            checkpointer=self.checkpointer,
            callback_handler=self.callbacks,  # Pass the list of callbacks
            manual_model_params=manual_model_params  # Placeholder for future manual model params
        )        
        
        # Conversation state
        self.messages: List[BaseMessage] = []
        self.metadata: Dict[str, Any] = {
            "created_at": datetime.now().isoformat(),
            "session_id": self.session_id,
            "workspace": str(self.workspace_path)
        }
    
    def query(self, user_input: str, stream: bool = False) -> Dict[str, Any]:
        """
        Process a user query through the agent system.
        
        Args:
            user_input: User's input text
            stream: Whether to stream the response
            
        Returns:
            Dictionary with response and metadata
        """
        # Add user message
        self.messages.append(HumanMessage(content=user_input))
        
        # Prepare graph input
        graph_input = {
            "messages": [HumanMessage(content=user_input)]
        }
        
        config = {
            "configurable": {"thread_id": self.session_id},
            "callbacks": self.callbacks
        }
        
        if stream:
            return self._stream_query(graph_input, config)
        else:
            return self._run_query(graph_input, config)
    
    def _run_query(self, graph_input: Dict, config: Dict) -> Dict[str, Any]:
        """Run a query and return the complete response."""
        try:
            # Track execution
            start_time = datetime.now()
            events = []
            
            # Execute graph
            for event in self.graph.stream(
                input=graph_input, 
                config=config,
                stream_mode='debug'
                ):
                events.append(event)
            
            # Extract final response from the last event
            final_response = self._extract_response(events)
            
            # Update messages with the final response (not the raw events)
            if final_response:
                self.messages.append(AIMessage(content=final_response))
            
            return {
                "success": True,
                "response": final_response,
                "duration": (datetime.now() - start_time).total_seconds(),
                "events_count": len(events),
                "session_id": self.session_id,
                "has_data": self.data_manager.has_data(),
                "plots": self.data_manager.get_latest_plots(5) if self.data_manager.has_data() else []
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": f"I encountered an error: {str(e)}",
                "session_id": self.session_id
            }
    
    def _stream_query(self, graph_input: Dict, config: Dict) -> Generator[Dict[str, Any], None, None]:
        """Stream query execution with intermediate results."""
        try:
            start_time = datetime.now()
            
            for event in self.graph.stream(graph_input, config):
                # Process each event
                for node_name, node_output in event.items():
                    # Extract meaningful content
                    content = self._extract_event_content(node_output)
                    
                    if content:
                        yield {
                            "type": "stream",
                            "node": node_name,
                            "content": content,
                            "timestamp": datetime.now().isoformat()
                        }
            
            # Final response
            yield {
                "type": "complete",
                "duration": (datetime.now() - start_time).total_seconds(),
                "session_id": self.session_id
            }
            
        except Exception as e:
            yield {
                "type": "error",
                "error": str(e),
                "session_id": self.session_id
            }
    
    def _extract_response(self, events: List[Dict]) -> str:
        """Extract the final response from ChatBedrockConverse format events."""
        if not events:
            return "No response generated."
        
        # Process events in reverse chronological order to find the last AI response
        for event in reversed(events):
            # Look for task_result events which contain the actual results
            if event.get("type") == "task_result":
                payload = event.get("payload", {})
                result = payload.get("result", [])
                
                # Result is a list of tuples like [("messages", [HumanMessage, AIMessage, ...])]
                for item in result:
                    if isinstance(item, tuple) and len(item) == 2:
                        key, value = item
                        if key == "messages" and isinstance(value, list):
                            # Find the last AIMessage in this result
                            for msg in reversed(value):
                                if isinstance(msg, AIMessage) and hasattr(msg, 'content'):
                                    content = msg.content.strip() if msg.content else ""
                                    # Return the content, even if it's empty
                                    if content or msg.content == "":
                                        return content
            
            # Fallback: check checkpoint events with values.messages
            elif event.get("type") == "checkpoint":
                payload = event.get("payload", {})
                values = payload.get("values", {})
                messages = values.get("messages", [])
                
                if messages:
                    # Find the last AIMessage in checkpoint messages
                    for msg in reversed(messages):
                        if isinstance(msg, AIMessage) and hasattr(msg, 'content'):
                            content = msg.content.strip() if msg.content else ""
                            if content or msg.content == "":
                                return content
        
        return "No response generated."
    
    def _extract_event_content(self, node_output: Dict) -> Optional[str]:
        """Extract displayable content from a node output."""
        if not isinstance(node_output, dict):
            return None
        
        # Check for messages - only return content from AI messages
        if "messages" in node_output and node_output["messages"]:
            # Look for the last AI message in this event
            for msg in reversed(node_output["messages"]):
                if isinstance(msg, AIMessage) and hasattr(msg, 'content') and msg.content:
                    return msg.content
        
        # Check for other relevant fields
        for key in ["analysis_results", "next", "data_context"]:
            if key in node_output and node_output[key]:
                return f"{key}: {node_output[key]}"
        
        return None
    
    # Workspace operations
    def list_workspace_files(self, pattern: str = "*") -> List[Dict[str, Any]]:
        """List files in the workspace."""
        files = []
        for path in self.workspace_path.glob(pattern):
            if path.is_file():
                files.append({
                    "name": path.name,
                    "path": str(path),
                    "size": path.stat().st_size,
                    "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat()
                })
        return files
    
    def read_file(self, filename: str) -> Optional[str]:
        """
        Read a file from the workspace or absolute path.
        
        Args:
            filename: Either a relative filename (searched in workspace) or absolute path
            
        Returns:
            File content as string, or None if not found
        """
        logger.info(f"🔍 Attempting to read file: '{filename}'")
        
        # Convert to Path object
        file_path = Path(filename)
        logger.info(f"🔎 Current filepath: {file_path}")
        logger.info(f"🔎 Is absolut: {file_path.is_absolute()}")
        
        # If it's an absolute path, try to read directly
        if file_path.is_absolute():
            logger.info(f"📁 Detected absolute path: {file_path}")
            if file_path.exists() and file_path.is_file():
                logger.info(f"✅ Found absolute file: {file_path}")
                try:
                    content = file_path.read_text()
                    logger.info(f"📖 Successfully read {len(content)} characters from {file_path}")
                    return content
                except Exception as e:
                    logger.error(f"❌ Error reading absolute file {file_path}: {e}")
                    return f"Error reading file {file_path}: {e}"
            else:
                logger.warning(f"❌ Absolute file not found: {file_path}")
                return f"File not found: {file_path}"
        
        # For relative paths, search in workspace and subdirectories
        logger.info(f"🔍 Searching for relative file: '{filename}'")
        logger.info(f"📂 Workspace path: {self.workspace_path}")
        
        # First try the root workspace directory
        file_path = self.workspace_path / filename
        logger.info(f"🔎 Checking workspace root: {file_path}")
        if file_path.exists() and file_path.is_file():
            logger.info(f"✅ Found in workspace root: {file_path}")
            try:
                content = file_path.read_text()
                logger.info(f"📖 Successfully read {len(content)} characters from workspace root")
                return content
            except Exception as e:
                logger.error(f"❌ Error reading from workspace root: {e}")
                return f"Error reading file: {e}"
        else:
            logger.info(f"❌ Not found in workspace root: {file_path}")
        
        # If not found in root, search in organized subdirectories
        search_dirs = [
            self.data_manager.data_dir,
            self.data_manager.plots_dir, 
            self.data_manager.exports_dir
        ]
        
        logger.info(f"🔍 Searching in {len(search_dirs)} subdirectories:")
        for i, search_dir in enumerate(search_dirs):
            logger.info(f"  {i+1}. {search_dir}")
        
        for search_dir in search_dirs:
            file_path = search_dir / filename
            logger.info(f"🔎 Checking: {file_path}")
            if file_path.exists() and file_path.is_file():
                logger.info(f"✅ Found in subdirectory: {file_path}")
                try:
                    content = file_path.read_text()
                    logger.info(f"📖 Successfully read {len(content)} characters from subdirectory")
                    return content
                except Exception as e:
                    logger.error(f"❌ Error reading from subdirectory: {e}")
                    return f"Error reading file: {e}"
            else:
                logger.debug(f"❌ Not found: {file_path}")
        
        # If still not found, try case-insensitive search in all subdirectories
        logger.info(f"🔍 Starting case-insensitive search for '{filename}'")
        filename_lower = filename.lower()
        
        for search_dir in search_dirs:
            logger.info(f"🔎 Case-insensitive search in: {search_dir}")
            if not search_dir.exists():
                logger.warning(f"⚠️  Directory doesn't exist: {search_dir}")
                continue
                
            try:
                files_in_dir = list(search_dir.glob("*"))
                logger.info(f"📁 Found {len(files_in_dir)} items in {search_dir.name}/")
                
                for existing_file in files_in_dir:
                    if existing_file.is_file():
                        logger.debug(f"  📄 Checking: {existing_file.name}")
                        if existing_file.name.lower() == filename_lower:
                            logger.info(f"✅ Case-insensitive match found: {existing_file}")
                            try:
                                content = existing_file.read_text()
                                logger.info(f"📖 Successfully read {len(content)} characters (case-insensitive match)")
                                return content
                            except Exception as e:
                                logger.error(f"❌ Error reading case-insensitive match: {e}")
                                return f"Error reading file: {e}"
            except Exception as e:
                logger.error(f"❌ Error during case-insensitive search in {search_dir}: {e}")
        
        # Final logging before giving up
        logger.warning(f"❌ File '{filename}' not found in any location")
        logger.info("📋 Search summary:")
        logger.info(f"  - Workspace root: {self.workspace_path}")
        for search_dir in search_dirs:
            logger.info(f"  - {search_dir.name}/: {search_dir}")
        
        return f"File not found in workspace: {filename}"
    
    def write_file(self, filename: str, content: str) -> bool:
        """Write a file to the workspace."""
        try:
            file_path = self.workspace_path / filename
            file_path.write_text(content)
            return True
        except Exception:
            return False
    
    # State management
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get formatted conversation history."""
        history = []
        for msg in self.messages:
            if isinstance(msg, HumanMessage):
                role = "user"
            elif isinstance(msg, AIMessage):
                role = "assistant"
            else:
                role = "system"
            
            history.append({
                "role": role,
                "content": msg.content if hasattr(msg, 'content') else str(msg)
            })
        return history
    
    def get_status(self) -> Dict[str, Any]:
        """Get current client status."""
        return {
            "session_id": self.session_id,
            "message_count": len(self.messages),
            "has_data": self.data_manager.has_data(),
            "data_summary": self.data_manager.get_data_summary() if self.data_manager.has_data() else None,
            "workspace": str(self.workspace_path),
            "reasoning_enabled": self.enable_reasoning,
            "callbacks_count": len(self.callbacks)
        }
    
    def reset(self):
        """Reset the conversation state."""
        self.messages = []
        self.metadata["reset_at"] = datetime.now().isoformat()
    
    def export_session(self, export_path: Optional[Path] = None) -> Path:
        """Export the current session data using data_manager's comprehensive export."""
        try:
            # Try to use data_manager's comprehensive export if data is available
            if self.data_manager.has_data():
                export_path = self.data_manager.create_data_package(
                    output_dir=str(self.data_manager.exports_dir)
                )
                return Path(export_path)
            else:
                # Fallback to basic session export
                export_path = export_path or self.workspace_path / f"session_{self.session_id}.json"
                
                session_data = {
                    "session_id": self.session_id,
                    "metadata": self.metadata,
                    "conversation": self.get_conversation_history(),
                    "status": self.get_status(),
                    "workspace_status": self.data_manager.get_workspace_status(),
                    "exported_at": datetime.now().isoformat()
                }
                
                with open(export_path, 'w') as f:
                    json.dump(session_data, f, indent=2, default=str)
                
                return export_path
        except Exception as e:
            # Final fallback
            export_path = export_path or self.workspace_path / f"session_{self.session_id}_basic.json"
            basic_data = {
                "session_id": self.session_id,
                "error": str(e),
                "conversation": self.get_conversation_history(),
                "exported_at": datetime.now().isoformat()
            }
            
            with open(export_path, 'w') as f:
                json.dump(basic_data, f, indent=2, default=str)
            
            return export_path
