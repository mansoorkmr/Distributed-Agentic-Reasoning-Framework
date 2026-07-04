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

        setMessages(previous => [
            ...previous,
            userMessage,
        ]);

        setLoading(true);

        try {

            const response = await chat({
                prompt,
            });

            const assistantMessage: Message = {
                role: "assistant",
                content: response.response,
            };

            setMessages(previous => [
                ...previous,
                assistantMessage,
            ]);

        } catch {

            setMessages(previous => [

                ...previous,

                {
                    role: "assistant",
                    content:
                        "Unable to contact DARF backend.",
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