'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  ChatBubbleLeftRightIcon, 
  Cog6ToothIcon, 
  ServerIcon,
  ChartBarIcon,
  CloudIcon,
  SparklesIcon
} from '@heroicons/react/24/outline'
import Header from '@/components/Header'
import Sidebar from '@/components/Sidebar'
import ChatInterface from '@/components/ChatInterface'
import Dashboard from '@/components/Dashboard'
import Resources from '@/components/Resources'
import Settings from '@/components/Settings'
import { useWebSocket } from '@/contexts/WebSocketContext'

export default function Home() {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const { isConnected } = useWebSocket()

  const tabs = [
    { id: 'dashboard', name: 'Dashboard', icon: ChartBarIcon },
    { id: 'chat', name: 'AI Chat', icon: ChatBubbleLeftRightIcon },
    { id: 'resources', name: 'Resources', icon: ServerIcon },
    { id: 'settings', name: 'Settings', icon: Cog6ToothIcon },
  ]

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />
      case 'chat':
        return <ChatInterface />
      case 'resources':
        return <Resources />
      case 'settings':
        return <Settings />
      default:
        return <Dashboard />
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <Header 
        sidebarOpen={sidebarOpen}
        setSidebarOpen={setSidebarOpen}
        isConnected={isConnected}
      />

      <div className="flex">
        {/* Sidebar */}
        <Sidebar
          tabs={tabs}
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          sidebarOpen={sidebarOpen}
          setSidebarOpen={setSidebarOpen}
        />

        {/* Main Content */}
        <main className="flex-1 lg:pl-64">
          <div className="px-4 sm:px-6 lg:px-8 py-8">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              {renderContent()}
            </motion.div>
          </div>
        </main>
      </div>

      {/* Connection Status Banner */}
      {!isConnected && (
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          className="fixed bottom-4 right-4 bg-error-500 text-white px-4 py-2 rounded-lg shadow-lg flex items-center space-x-2"
        >
          <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
          <span className="text-sm font-medium">Disconnected from server</span>
        </motion.div>
      )}
    </div>
  )
}