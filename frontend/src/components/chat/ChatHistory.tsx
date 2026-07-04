import ChatMessage from "./ChatMessage";

export interface Message {

    role:
        | "user"
        | "assistant";

    content: string;

}

interface ChatHistoryProps {

    messages: Message[];

}

function ChatHistory({

    messages,

}: ChatHistoryProps) {

    return (

        <div className="flex flex-1 flex-col gap-4 overflow-y-auto">

            {

                messages.map(

                    (message, index) => (

                        <ChatMessage
                            key={index}
                            role={message.role}
                            content={message.content}
                        />

                    ),

                )

            }

        </div>

    );

}

export default ChatHistory;