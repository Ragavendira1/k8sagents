'use client'

import { Fragment } from 'react'
import { Dialog, Transition } from '@headlessui/react'
import { 
  Bars3Icon, 
  XMarkIcon,
  CloudIcon,
  WifiIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'
import { motion } from 'framer-motion'

interface HeaderProps {
  sidebarOpen: boolean
  setSidebarOpen: (open: boolean) => void
  isConnected: boolean
}

export default function Header({ sidebarOpen, setSidebarOpen, isConnected }: HeaderProps) {
  return (
    <div className="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-4 border-b border-gray-200 bg-white px-4 shadow-sm sm:gap-x-6 sm:px-6 lg:px-8">
      <button
        type="button"
        className="-m-2.5 p-2.5 text-gray-700 lg:hidden"
        onClick={() => setSidebarOpen(true)}
      >
        <span className="sr-only">Open sidebar</span>
        <Bars3Icon className="h-6 w-6" aria-hidden="true" />
      </button>

      {/* Separator */}
      <div className="h-6 w-px bg-gray-200 lg:hidden" aria-hidden="true" />

      <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
        <div className="flex flex-1 items-center">
          <div className="flex items-center space-x-3">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2 }}
              className="flex items-center space-x-2"
            >
              <CloudIcon className="h-8 w-8 text-primary-600" />
              <div>
                <h1 className="text-xl font-bold text-gray-900">Kubernetes AI Agent</h1>
                <p className="text-sm text-gray-500">Powered by LangChain & Google Gemini</p>
              </div>
            </motion.div>
          </div>
        </div>

        <div className="flex items-center gap-x-4 lg:gap-x-6">
          {/* Connection Status */}
          <div className="flex items-center space-x-2">
            {isConnected ? (
              <motion.div
                initial={{ opacity: 0, scale: 0 }}
                animate={{ opacity: 1, scale: 1 }}
                className="flex items-center space-x-2 text-success-600"
              >
                <WifiIcon className="h-5 w-5" />
                <span className="text-sm font-medium">Connected</span>
              </motion.div>
            ) : (
              <motion.div
                initial={{ opacity: 0, scale: 0 }}
                animate={{ opacity: 1, scale: 1 }}
                className="flex items-center space-x-2 text-error-600"
              >
                <ExclamationTriangleIcon className="h-5 w-5" />
                <span className="text-sm font-medium">Disconnected</span>
              </motion.div>
            )}
          </div>

          {/* Status Indicator */}
          <div className="flex items-center">
            <div className={`w-3 h-3 rounded-full ${
              isConnected 
                ? 'bg-success-500 animate-pulse' 
                : 'bg-error-500'
            }`} />
          </div>
        </div>
      </div>
    </div>
  )
}