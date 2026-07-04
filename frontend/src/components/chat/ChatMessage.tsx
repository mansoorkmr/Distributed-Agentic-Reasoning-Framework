interface ChatMessageProps {
    role: "user" | "assistant";
    content: string;
}

function ChatMessage({
    role,
    content,
}: ChatMessageProps) {

    const isUser = role === "user";

    return (

        <div
            className={`flex ${
                isUser
                    ? "justify-end"
                    : "justify-start"
            }`}
        >

            <div
                className={`max-w-[80%] rounded-xl p-3 ${
                    isUser
                        ? "bg-blue-600"
                        : "bg-slate-700"
                }`}
            >
                {content}
            </div>

        </div>

    );

}

export default ChatMessage;