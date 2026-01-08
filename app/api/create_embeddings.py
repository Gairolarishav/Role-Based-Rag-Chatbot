from fastapi import APIRouter,UploadFile, File,HTTPException
# from app.services.rag.embeddings import create_embeddings


router  = APIRouter(prefix="/embeddings",tags=["Embeddings"])

@router.post("/ingest/")
async def ingest_documents(
    role : str,
    file: UploadFile = File(...)
):
    # Validate file type
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Read file bytes
    file_bytes = await file.read()

    # result  = create_embeddings(role,file_bytes,filename=file.filename)

    return {
        "filename": file.filename,
        # "message": result
    }
