/**
 * DARF Frontend
 * Chat Input Component
 */

import {
    useRef,
    useState,
    type ChangeEvent,
    type KeyboardEvent,
} from "react";

interface ChatInputProps {
    /** Callback triggered when the user submits a message */
    onSend: (
        prompt: string,
        file?: File | null,
    ) => void;

    /** Indicates if the system is currently processing a request */
    loading: boolean;
}

const ChatInput = ({ onSend, loading }: ChatInputProps) => {
    const [prompt, setPrompt] = useState<string>("");
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [fileError, setFileError] = useState<string>("");

    const fileInputRef = useRef<HTMLInputElement | null>(null);

    const submit = () => {
        const trimmedPrompt = prompt.trim();

        if (!trimmedPrompt || loading) {
            return;
        }

        onSend(trimmedPrompt, selectedFile);
        setPrompt("");
        setSelectedFile(null);
        setFileError("");
        if (fileInputRef.current) {
            fileInputRef.current.value = "";
        }
    };

    const handleKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            submit();
        }
    };

    const handleChange = (event: ChangeEvent<HTMLInputElement>) => {
        setPrompt(event.target.value);
    };

    const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];

        setFileError("");

        if (!file) {
            return;
        }

        if (file.type !== "application/pdf") {
            setSelectedFile(null);
            setFileError("Only PDF files are supported.");
            event.target.value = "";
            return;
        }

        const maxSize = 20 * 1024 * 1024;

        if (file.size > maxSize) {
            setSelectedFile(null);
            setFileError("PDF must be 20 MB or smaller.");
            event.target.value = "";
            return;
        }

        setSelectedFile(file);
    };

    const removeFile = () => {
        setSelectedFile(null);
        setFileError("");

        if (fileInputRef.current) {
            fileInputRef.current.value = "";
        }
    };

    const isSendDisabled = loading || !prompt.trim();

    return (
        <div className="mt-4">
            {selectedFile && (
                <div className="mb-2 flex items-center justify-between rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-200">
                    <div className="min-w-0">
                        <span className="mr-2">📄</span>
                        <span className="truncate">{selectedFile.name}</span>
                    </div>

                    <button
                        type="button"
                        onClick={removeFile}
                        disabled={loading}
                        className="ml-3 text-slate-400 transition-colors hover:text-red-400 disabled:cursor-not-allowed disabled:opacity-50"
                        aria-label="Remove PDF"
                    >
                        Remove
                    </button>
                </div>
            )}

            {fileError && (
                <div className="mb-2 text-sm text-red-400">
                    {fileError}
                </div>
            )}

            <div className="flex gap-3">
                <input
                    ref={fileInputRef}
                    type="file"
                    accept="application/pdf,.pdf"
                    onChange={handleFileChange}
                    className="hidden"
                    disabled={loading}
                    aria-label="Upload PDF"
                />

                <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    disabled={loading}
                    className="rounded-lg border border-slate-700 bg-slate-800 px-4 text-slate-200 transition-colors hover:border-slate-600 hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
                    aria-label="Attach PDF"
                    title="Attach PDF"
                >
                    📎
                </button>

                <input
                    type="text"
                    className="flex-1 rounded-lg border border-slate-700 bg-slate-800 p-3 text-slate-100 placeholder-slate-400 outline-none transition-colors focus:border-blue-500 focus:ring-1 focus:ring-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
                    placeholder={
                        selectedFile
                            ? "Ask DARF about this PDF..."
                            : "Ask DARF..."
                    }
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
        </div>
    );
};

export default ChatInput;