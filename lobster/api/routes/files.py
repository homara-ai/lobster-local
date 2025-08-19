"""
Lobster AI - File Management Routes
File upload, download, and management endpoints.
"""

import os
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Request, UploadFile, File, Form, Query
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path

from lobster.api.models import (
    FileUploadResponse,
    FileListResponse,
    FileInfo,
    BaseResponse,
    DatasetInfo,
    DatasetStatus,
    FileType
)
from lobster.api.session_manager import SessionManager
from lobster.core.api_client import APIAgentClient
from lobster.utils.logger import get_logger

logger = get_logger(__name__)

# Create router instance
router = APIRouter()

# Supported file extensions and their types
SUPPORTED_EXTENSIONS = {
    '.csv': FileType.CSV,
    '.tsv': FileType.TSV,
    '.txt': FileType.TSV,  # Assume tab-separated for .txt files
    '.h5': FileType.H5,
    '.h5ad': FileType.H5AD,
    '.mtx': FileType.MTX,
}

# Maximum file size: 500MB
MAX_FILE_SIZE = 500 * 1024 * 1024


def get_session_manager(request: Request) -> SessionManager:
    """Dependency to get the session manager from app state."""
    return request.app.state.session_manager


def get_file_type(filename: str) -> Optional[FileType]:
    """Determine file type from filename extension."""
    file_path = Path(filename)
    extension = ''.join(file_path.suffixes).lower()
    
    # Try exact match first
    if extension in SUPPORTED_EXTENSIONS:
        return SUPPORTED_EXTENSIONS[extension]
    
    # Try single extension
    single_ext = file_path.suffix.lower()
    return SUPPORTED_EXTENSIONS.get(single_ext)


@router.post("/sessions/{session_id}/files/upload", response_model=FileUploadResponse)
async def upload_file(
    session_id: UUID,
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    session_manager: SessionManager = Depends(get_session_manager)
):
    """
    Upload a file to the session workspace.
    
    Supports various bioinformatics file formats including:
    - CSV/TSV data files
    - H5/H5AD single-cell data
    - MTX matrix files
    """
    try:
        # Get the session
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=404,
                detail="Session not found or expired"
            )
        
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="No filename provided"
            )
        
        # Check file size
        file_content = await file.read()
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE / (1024*1024):.0f}MB"
            )
        
        # Determine file type
        file_type = get_file_type(file.filename)
        if not file_type:
            logger.warning(f"Unsupported file type for {file.filename}, proceeding anyway")
        
        # Get or create API agent client for file handling
        if not hasattr(session, '_api_client') or session._api_client is None:
            session._api_client = APIAgentClient(
                session_id=session_id,
                session_manager=session_manager,
                workspace_path=session.workspace_path
            )
        
        # Upload file using API client
        upload_result = await session._api_client.upload_file(
            file_path=file.filename,
            file_content=file_content
        )
        
        # Update session activity
        session.update_activity()
        
        # Create dataset info if file was loaded as data
        dataset = None
        if upload_result.get("data_loaded"):
            dataset = DatasetInfo(
                name=file.filename,
                path=upload_result["file_path"],
                file_type=file_type or FileType.CSV,
                size_bytes=upload_result["file_size"],
                status=DatasetStatus.READY,
                created_at=datetime.utcnow(),
                metadata={
                    "description": description,
                    "original_filename": file.filename,
                    "upload_session": str(session_id)
                }
            )
            
            # Update session datasets list
            if file.filename not in session.datasets:
                session.datasets.append(file.filename)
        
        # Create response
        response = FileUploadResponse(
            success=upload_result["success"],
            message=upload_result["message"],
            file_path=upload_result["file_path"],
            file_size=upload_result["file_size"],
            dataset=dataset
        )
        
        logger.info(f"File uploaded successfully for session {session_id}: {file.filename}")
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file for session {session_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload file: {str(e)}"
        )


@router.get("/sessions/{session_id}/files", response_model=FileListResponse)
async def list_files(
    session_id: UUID,
    directory: Optional[str] = Query(None, description="Directory to list (data, plots, exports, or None for all)"),
    session_manager: SessionManager = Depends(get_session_manager)
):
    """
    List files in the session workspace.
    
    Args:
        session_id: Session UUID
        directory: Optional directory filter (data, plots, exports)
    """
    try:
        # Get the session
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=404,
                detail="Session not found or expired"
            )
        
        # Get or create API agent client for file listing
        if not hasattr(session, '_api_client') or session._api_client is None:
            session._api_client = APIAgentClient(
                session_id=session_id,
                session_manager=session_manager,
                workspace_path=session.workspace_path
            )
        
        # List workspace files
        files_data = session._api_client.list_workspace_files(directory=directory)
        
        # Convert to FileInfo objects
        file_infos = []
        total_size = 0
        
        for file_data in files_data:
            file_info = FileInfo(
                name=file_data["name"],
                path=file_data["path"],
                size_bytes=file_data["size"],
                created_at=datetime.fromisoformat(file_data["modified"]),
                modified_at=datetime.fromisoformat(file_data["modified"]),
                file_type=file_data.get("directory", "unknown")
            )
            file_infos.append(file_info)
            total_size += file_data["size"]
        
        # Update session activity
        session.update_activity()
        
        # Create response
        response = FileListResponse(
            success=True,
            message=f"Retrieved {len(file_infos)} files",
            files=file_infos,
            total=len(file_infos),
            total_size_bytes=total_size
        )
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing files for session {session_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list files: {str(e)}"
        )


@router.get("/sessions/{session_id}/files/{file_path:path}/download")
async def download_file(
    session_id: UUID,
    file_path: str,
    session_manager: SessionManager = Depends(get_session_manager)
):
    """
    Download a file from the session workspace.
    
    Args:
        session_id: Session UUID
        file_path: Relative path to the file within the workspace
    """
    try:
        # Get the session
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=404,
                detail="Session not found or expired"
            )
        
        # Construct full file path
        full_path = session.workspace_path / file_path
        
        # Security check: ensure the file is within the workspace
        try:
            full_path.resolve().relative_to(session.workspace_path.resolve())
        except ValueError:
            raise HTTPException(
                status_code=403,
                detail="Access denied: File path outside workspace"
            )
        
        # Check if file exists
        if not full_path.exists() or not full_path.is_file():
            raise HTTPException(
                status_code=404,
                detail="File not found"
            )
        
        # Update session activity
        session.update_activity()
        
        # Return file response
        return FileResponse(
            path=str(full_path),
            filename=full_path.name,
            media_type='application/octet-stream'
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file for session {session_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to download file: {str(e)}"
        )


@router.delete("/sessions/{session_id}/files/{file_path:path}", response_model=BaseResponse)
async def delete_file(
    session_id: UUID,
    file_path: str,
    session_manager: SessionManager = Depends(get_session_manager)
):
    """
    Delete a file from the session workspace.
    
    Args:
        session_id: Session UUID
        file_path: Relative path to the file within the workspace
    """
    try:
        # Get the session
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=404,
                detail="Session not found or expired"
            )
        
        # Construct full file path
        full_path = session.workspace_path / file_path
        
        # Security check: ensure the file is within the workspace
        try:
            full_path.resolve().relative_to(session.workspace_path.resolve())
        except ValueError:
            raise HTTPException(
                status_code=403,
                detail="Access denied: File path outside workspace"
            )
        
        # Check if file exists
        if not full_path.exists():
            raise HTTPException(
                status_code=404,
                detail="File not found"
            )
        
        # Delete the file
        if full_path.is_file():
            full_path.unlink()
            logger.info(f"Deleted file {file_path} from session {session_id}")
        elif full_path.is_dir():
            import shutil
            shutil.rmtree(full_path)
            logger.info(f"Deleted directory {file_path} from session {session_id}")
        
        # Update session activity
        session.update_activity()
        
        # Remove from datasets list if it was a dataset
        filename = Path(file_path).name
        if filename in session.datasets:
            session.datasets.remove(filename)
        
        return BaseResponse(
            success=True,
            message=f"File {file_path} deleted successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file for session {session_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete file: {str(e)}"
        )


@router.get("/sessions/{session_id}/files/{file_path:path}/info")
async def get_file_info(
    session_id: UUID,
    file_path: str,
    session_manager: SessionManager = Depends(get_session_manager)
):
    """
    Get detailed information about a specific file.
    
    Args:
        session_id: Session UUID
        file_path: Relative path to the file within the workspace
    """
    try:
        # Get the session
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=404,
                detail="Session not found or expired"
            )
        
        # Construct full file path
        full_path = session.workspace_path / file_path
        
        # Security check: ensure the file is within the workspace
        try:
            full_path.resolve().relative_to(session.workspace_path.resolve())
        except ValueError:
            raise HTTPException(
                status_code=403,
                detail="Access denied: File path outside workspace"
            )
        
        # Check if file exists
        if not full_path.exists():
            raise HTTPException(
                status_code=404,
                detail="File not found"
            )
        
        # Get file stats
        stat = full_path.stat()
        file_type = get_file_type(full_path.name)
        
        # Create file info
        file_info = FileInfo(
            name=full_path.name,
            path=file_path,
            size_bytes=stat.st_size,
            created_at=datetime.fromtimestamp(stat.st_ctime),
            modified_at=datetime.fromtimestamp(stat.st_mtime),
            file_type=file_type.value if file_type else "unknown"
        )
        
        # Update session activity
        session.update_activity()
        
        return {
            "success": True,
            "message": "File information retrieved successfully",
            "file": file_info.dict()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting file info for session {session_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get file information: {str(e)}"
        )
