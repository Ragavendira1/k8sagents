'use client'

import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  PaperAirplaneIcon, 
  UserIcon, 
  SparklesIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline'
import { useWebSocket } from '@/contexts/WebSocketContext'
import toast from 'react-hot-toast'

interface Message {
  id: string
  type: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  status?: 'sending' | 'sent' | 'error'
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'assistant',
      content: 'Hello! I\'m your Kubernetes AI Assistant. I can help you manage your cluster with natural language commands. Try asking me to create a deployment, list resources, or scale your applications.',
      timestamp: new Date()
    }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const { sendMessage, lastMessage, isConnected } = useWebSocket()

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    if (lastMessage && lastMessage.type === 'response') {
      setMessages(prev => prev.map(msg => 
        msg.status === 'sending' 
          ? { ...msg, content: lastMessage.message, status: 'sent' }
          : msg
      ))
      setIsLoading(false)
    }
  }, [lastMessage])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input.trim(),
      timestamp: new Date(),
      status: 'sending'
    }

    const assistantMessage: Message = {
      id: (Date.now() + 1).toString(),
      type: 'assistant',
      content: '',
      timestamp: new Date(),
      status: 'sending'
    }

    setMessages(prev => [...prev, userMessage, assistantMessage])
    setInput('')
    setIsLoading(true)

    try {
      if (isConnected) {
        sendMessage(input.trim())
      } else {
        // Fallback to HTTP API
        const response = await fetch('/api/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ message: input.trim() }),
        })

        if (!response.ok) {
          throw new Error('Failed to send message')
        }

        const data = await response.json()
        
        setMessages(prev => prev.map(msg => 
          msg.id === assistantMessage.id 
            ? { ...msg, content: data.response, status: 'sent' }
            : msg
        ))
        setIsLoading(false)
      }
    } catch (error) {
      console.error('Error sending message:', error)
      toast.error('Failed to send message. Please try again.')
      
      setMessages(prev => prev.map(msg => 
        msg.status === 'sending' 
          ? { ...msg, content: 'Sorry, I encountered an error. Please try again.', status: 'error' }
          : msg
      ))
      setIsLoading(false)
    }
  }

  const quickActions = [
    'Create a deployment named "webapp" with nginx image',
    'List all pods in the cluster',
    'Scale the webapp deployment to 3 replicas',
    'Create a service for the webapp deployment',
    'Show me the cluster status'
  ]

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-white">
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <SparklesIcon className="h-6 w-6 text-primary-600" />
            <h2 className="text-lg font-semibold text-gray-900">AI Chat</h2>
          </div>
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${
              isConnected ? 'bg-success-500' : 'bg-error-500'
            }`} />
            <span className="text-sm text-gray-500">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <AnimatePresence>
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`flex max-w-xs lg:max-w-md ${
                message.type === 'user' ? 'flex-row-reverse' : 'flex-row'
              }`}>
                <div className={`flex-shrink-0 ${
                  message.type === 'user' ? 'ml-3' : 'mr-3'
                }`}>
                  <div className={`h-8 w-8 rounded-full flex items-center justify-center ${
                    message.type === 'user' 
                      ? 'bg-primary-600' 
                      : 'bg-gray-200'
                  }`}>
                    {message.type === 'user' ? (
                      <UserIcon className="h-5 w-5 text-white" />
                    ) : (
                      <SparklesIcon className="h-5 w-5 text-gray-600" />
                    )}
                  </div>
                </div>
                
                <div className={`px-4 py-2 rounded-lg ${
                  message.type === 'user'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-900'
                }`}>
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                  
                  {message.status === 'sending' && (
                    <div className="flex items-center mt-2">
                      <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-gray-400"></div>
                      <span className="ml-2 text-xs text-gray-500">Sending...</span>
                    </div>
                  )}
                  
                  {message.status === 'error' && (
                    <div className="flex items-center mt-2">
                      <ExclamationTriangleIcon className="h-3 w-3 text-red-500" />
                      <span className="ml-2 text-xs text-red-500">Error</span>
                    </div>
                  )}
                  
                  {message.status === 'sent' && (
                    <div className="flex items-center mt-2">
                      <CheckCircleIcon className="h-3 w-3 text-green-500" />
                      <span className="ml-2 text-xs text-gray-500">Sent</span>
                    </div>
                  )}
                  
                  <p className="text-xs text-gray-400 mt-1">
                    {message.timestamp.toLocaleTimeString()}
                  </p>
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Actions */}
      {messages.length === 1 && (
        <div className="p-4 border-t border-gray-200 bg-gray-50">
          <p className="text-sm text-gray-600 mb-3">Try these quick actions:</p>
          <div className="grid grid-cols-1 gap-2">
            {quickActions.map((action, index) => (
              <button
                key={index}
                onClick={() => setInput(action)}
                className="text-left p-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md transition-colors duration-200"
              >
                {action}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="p-4 border-t border-gray-200 bg-white">
        <div className="flex space-x-4">
          <div className="flex-1">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask me anything about your Kubernetes cluster..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              disabled={isLoading}
            />
          </div>
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <PaperAirplaneIcon className="h-5 w-5" />
          </button>
        </div>
      </form>
    </div>
  )
}