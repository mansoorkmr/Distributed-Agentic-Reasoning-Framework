import api from "../api/client";

export interface DocumentUploadResponse {
    success: boolean;
    message: string;
    document_id: string;
    filename: string;
    content_type: string;
    size_bytes: number;
    pages: number;
    characters: number;
    chunks: number;
    indexed: boolean;
}

export async function uploadDocument(
    file: File,
): Promise<DocumentUploadResponse> {
    const formData = new FormData();

    formData.append("file", file);

    const response = await api.post<DocumentUploadResponse>(
        "/documents/upload",
        formData,
    );

    return response.data;
}