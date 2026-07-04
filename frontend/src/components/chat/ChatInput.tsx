/**
 * DARF Frontend
 * Chat Input Component
 */
import { useState, type KeyboardEvent, type ChangeEvent } from "react";

interface ChatInputProps {
    /** Callback triggered when the user submits a message */
    onSend: (prompt: string) => void;
    /** Indicates if the system is currently processing a request */
    loading: boolean;
}

const ChatInput = ({ onSend, loading }: ChatInputProps) => {
    const [prompt, setPrompt] = useState<string>("");

    const submit = () => {
        const trimmedPrompt = prompt.trim();
        if (!trimmedPrompt || loading) return;

        onSend(trimmedPrompt);
        setPrompt("");
    };

    const handleKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
        // Submit on Enter, but allow Shift+Enter if you eventually convert this to a textarea
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            submit();
        }
    };

    const handleChange = (event: ChangeEvent<HTMLInputElement>) => {
        setPrompt(event.target.value);
    };

    const isSendDisabled = loading || !prompt.trim();

    return (
        <div className="mt-4 flex gap-3">
            <input
                type="text"
                className="flex-1 rounded-lg border border-slate-700 bg-slate-800 p-3 text-slate-100 placeholder-slate-400 outline-none transition-colors focus:border-blue-500 focus:ring-1 focus:ring-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
                placeholder="Ask DARF..."
                value={prompt}
                onChange={handleChange}
                onKeyDown={handleKeyDown}
                disabled={loading}
                aria-label="Chat input"
            />
            
            <button
                type="button"
                className="rounded-lg bg-blue-600 px-6 font-medium text-white transition-colors hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-slate-900 disabled:cursor-not-allowed disabled:opacity-50"
                onClick={submit}
                disabled={isSendDisabled}
                aria-busy={loading}
            >
                {loading ? "Sending..." : "Send"}
            </button>
        </div>
    );
};

export default ChatInput;