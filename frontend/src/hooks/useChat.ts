import { useState } from "react";

import { chat } from "../services/chat";
import { uploadDocument } from "../services/documents";

import type { Message } from "../components/chat/ChatHistory";


export function useChat() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [loading, setLoading] = useState(false);

    async function sendMessage(
        prompt: string,
        file?: File | null,
    ) {
        const userMessage: Message = {
            role: "user",
            content: file
                ? `${prompt}\n\n📄 ${file.name}`
                : prompt,
        };

        setMessages((previous) => [
            ...previous,
            userMessage,
        ]);

        setLoading(true);

        try {
            let documentId: string | undefined;

            // ==================================================
            // PDF UPLOAD
            // ==================================================

            if (file) {
                const uploadResponse = await uploadDocument(file);

                if (!uploadResponse.success) {
                    throw new Error(
                        uploadResponse.message ||
                        "PDF upload failed.",
                    );
                }

                documentId = uploadResponse.document_id;
            }

            // ==================================================
            // CHAT
            // ==================================================

            const response = await chat({
                prompt,
                document_id: documentId,
            });

            const assistantMessage: Message = {
                role: "assistant",
                content: response.response,
            };

            setMessages((previous) => [
                ...previous,
                assistantMessage,
            ]);

        } catch (error: any) {
            console.error("===== DARF CHAT ERROR =====");
            console.error(error);
            console.error("Message:", error?.message);
            console.error("Status:", error?.response?.status);
            console.error("Response:", error?.response?.data);

            const backendMessage =
                error?.response?.data?.detail ??
                error?.response?.data?.message ??
                error?.message ??
                "Unable to contact DARF backend.";

            setMessages((previous) => [
                ...previous,
                {
                    role: "assistant",
                    content: backendMessage,
                },
            ]);

        } finally {
            setLoading(false);
        }
    }

    return {
        messages,
        loading,
        sendMessage,
    };
}