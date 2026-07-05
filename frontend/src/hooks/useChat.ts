import { useState } from "react";
import { chat } from "../services/chat";
import type { Message } from "../components/chat/ChatHistory";

export function useChat() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [loading, setLoading] = useState(false);

    async function sendMessage(prompt: string) {
        const userMessage: Message = {
            role: "user",
            content: prompt,
        };

        setMessages((previous) => [...previous, userMessage]);

        setLoading(true);

        try {
            const response = await chat({
                prompt,
            });

            const assistantMessage: Message = {
                role: "assistant",
                content: response.response,
            };

            setMessages((previous) => [...previous, assistantMessage]);
        } catch (error: any) {
            console.error("===== AXIOS ERROR =====");
            console.error(error);
            console.error("Message:", error?.message);
            console.error("Status:", error?.response?.status);
            console.error("Response:", error?.response?.data);
            console.error("Stack:", error?.stack);

            setMessages((previous) => [
                ...previous,
                {
                    role: "assistant",
                    content: error?.message ?? "Unable to contact DARF backend.",
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