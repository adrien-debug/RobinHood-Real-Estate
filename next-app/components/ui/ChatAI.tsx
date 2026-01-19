'use client'

import { useState, useRef, useEffect } from 'react'
import { MessageCircle, X, Send, Bot, User, Loader2 } from 'lucide-react'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

const PREDEFINED_QUESTIONS = [
  'Quelle zone a le meilleur yield?',
  'Top 3 opportunités du jour?',
  'Tendance du marché cette semaine?',
  'Zones avec le plus de volume?',
  'Alertes critiques actives?'
]

export function ChatAI() {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Bonjour! Je suis Robin AI. Posez-moi vos questions sur le marché immobilier de Dubai.',
      timestamp: new Date()
    }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async (question?: string) => {
    const text = question || input.trim()
    if (!text || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      // Call AI endpoint
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: text })
      })
      
      const json = await res.json()
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: json.answer || 'Désolé, je n\'ai pas pu traiter votre demande.',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, assistantMessage])
    } catch (err) {
      console.error('Chat error:', err)
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Erreur de connexion. Veuillez réessayer.',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <>
      {/* Floating Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full shadow-lg flex items-center justify-center transition-all duration-300 ${
          isOpen 
            ? 'bg-danger hover:bg-danger/90 rotate-90' 
            : 'bg-accent hover:bg-accent/90'
        }`}
      >
        {isOpen ? (
          <X className="w-6 h-6 text-white" />
        ) : (
          <MessageCircle className="w-6 h-6 text-white" />
        )}
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div className="fixed bottom-24 right-6 z-50 w-96 max-w-[calc(100vw-48px)] bg-background border border-border rounded-2xl shadow-2xl flex flex-col overflow-hidden">
          {/* Header */}
          <div className="bg-accent px-4 py-3 flex items-center gap-3">
            <Bot className="w-6 h-6 text-white" />
            <div>
              <h3 className="font-semibold text-white">Robin AI</h3>
              <p className="text-xs text-white/70">Assistant marché Dubai</p>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 max-h-80 min-h-48">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex gap-2 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
              >
                <div className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 ${
                  msg.role === 'user' ? 'bg-info/20' : 'bg-accent/20'
                }`}>
                  {msg.role === 'user' ? (
                    <User className="w-4 h-4 text-info" />
                  ) : (
                    <Bot className="w-4 h-4 text-accent" />
                  )}
                </div>
                <div className={`max-w-[75%] px-3 py-2 rounded-2xl text-sm ${
                  msg.role === 'user' 
                    ? 'bg-info text-white rounded-tr-sm' 
                    : 'bg-background-secondary text-text-primary rounded-tl-sm'
                }`}>
                  {msg.content}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex gap-2">
                <div className="w-7 h-7 rounded-full bg-accent/20 flex items-center justify-center">
                  <Bot className="w-4 h-4 text-accent" />
                </div>
                <div className="bg-background-secondary px-3 py-2 rounded-2xl rounded-tl-sm">
                  <Loader2 className="w-4 h-4 animate-spin text-text-muted" />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Quick Questions */}
          <div className="px-4 pb-2">
            <div className="flex flex-wrap gap-1">
              {PREDEFINED_QUESTIONS.slice(0, 3).map((q, i) => (
                <button
                  key={i}
                  onClick={() => handleSend(q)}
                  disabled={isLoading}
                  className="text-xs px-2 py-1 rounded-full bg-background-secondary text-text-secondary hover:bg-accent/10 hover:text-accent transition-colors truncate max-w-[45%]"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>

          {/* Input */}
          <div className="p-3 border-t border-border">
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Posez votre question..."
                className="flex-1 bg-background-secondary border border-border rounded-xl px-4 py-2 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:border-accent"
                disabled={isLoading}
              />
              <button
                onClick={() => handleSend()}
                disabled={!input.trim() || isLoading}
                className="w-10 h-10 rounded-xl bg-accent text-white flex items-center justify-center hover:bg-accent/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
