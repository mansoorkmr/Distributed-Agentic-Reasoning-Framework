import ChatHistory from "./ChatHistory";
import ChatInput from "./ChatInput";

import { useChat } from "../../hooks/useChat";

function ChatPanel() {

    const {

        messages,

        loading,

        sendMessage,

    } = useChat();

    return (

        <div className="flex h-[500px] flex-col rounded-xl border border-slate-700 bg-slate-800 p-5">

            <h2 className="mb-4 text-xl font-semibold">

                DARF Chat

            </h2>

            <ChatHistory
                messages={messages}
            />

            <ChatInput
                loading={loading}
                onSend={sendMessage}
            />

        </div>

    );

}

export default ChatPanel;