'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  ServerIcon,
  CloudIcon,
  CpuChipIcon,
  CircleStackIcon,
  ChartBarIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon
} from '@heroicons/react/24/outline'
import { useWebSocket } from '@/contexts/WebSocketContext'

interface ClusterStatus {
  agent_status: string
  kubectl_available: boolean
  configuration: {
    model: string
    namespace: string
    max_replicas: number
    allowed_images: string[]
    forbidden_namespaces: string[]
  }
  timestamp: string
}

interface ResourceCounts {
  deployments: number
  services: number
  pods: number
  namespaces: number
}

export default function Dashboard() {
  const [clusterStatus, setClusterStatus] = useState<ClusterStatus | null>(null)
  const [resourceCounts, setResourceCounts] = useState<ResourceCounts>({
    deployments: 0,
    services: 0,
    pods: 0,
    namespaces: 0
  })
  const [loading, setLoading] = useState(true)
  const { isConnected } = useWebSocket()

  useEffect(() => {
    fetchClusterStatus()
    fetchResourceCounts()
  }, [])

  const fetchClusterStatus = async () => {
    try {
      const response = await fetch('/api/status')
      const data = await response.json()
      setClusterStatus(data)
    } catch (error) {
      console.error('Error fetching cluster status:', error)
    }
  }

  const fetchResourceCounts = async () => {
    try {
      const [deployments, services, pods, namespaces] = await Promise.all([
        fetch('/api/resources/deployments').then(res => res.json()),
        fetch('/api/resources/services').then(res => res.json()),
        fetch('/api/resources/pods').then(res => res.json()),
        fetch('/api/resources/namespaces').then(res => res.json())
      ])

      setResourceCounts({
        deployments: deployments.resources?.length || 0,
        services: services.resources?.length || 0,
        pods: pods.resources?.length || 0,
        namespaces: namespaces.resources?.length || 0
      })
    } catch (error) {
      console.error('Error fetching resource counts:', error)
    } finally {
      setLoading(false)
    }
  }

  const stats = [
    {
      name: 'Deployments',
      value: resourceCounts.deployments,
      icon: ServerIcon,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100'
    },
    {
      name: 'Services',
      value: resourceCounts.services,
      icon: CloudIcon,
      color: 'text-green-600',
      bgColor: 'bg-green-100'
    },
    {
      name: 'Pods',
      value: resourceCounts.pods,
      icon: CpuChipIcon,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100'
    },
    {
      name: 'Namespaces',
      value: resourceCounts.namespaces,
      icon: CircleStackIcon,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100'
    }
  ]

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Overview of your Kubernetes cluster and AI agent status
        </p>
      </div>

      {/* Status Cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat, index) => (
          <motion.div
            key={stat.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="card hover:shadow-md transition-shadow duration-200"
          >
            <div className="flex items-center">
              <div className={`flex-shrink-0 p-3 rounded-md ${stat.bgColor}`}>
                <stat.icon className={`h-6 w-6 ${stat.color}`} aria-hidden="true" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">{stat.name}</p>
                <p className="text-2xl font-semibold text-gray-900">{stat.value}</p>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Cluster Status */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Agent Status */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="card"
        >
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-medium text-gray-900">AI Agent Status</h3>
              <p className="text-sm text-gray-500">Current agent configuration and status</p>
            </div>
            <div className="flex items-center space-x-2">
              {isConnected ? (
                <CheckCircleIcon className="h-6 w-6 text-success-500" />
              ) : (
                <ExclamationTriangleIcon className="h-6 w-6 text-error-500" />
              )}
            </div>
          </div>
          
          <div className="mt-4 space-y-3">
            <div className="flex justify-between">
              <span className="text-sm text-gray-500">Connection</span>
              <span className={`text-sm font-medium ${
                isConnected ? 'text-success-600' : 'text-error-600'
              }`}>
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
            
            {clusterStatus && (
              <>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Model</span>
                  <span className="text-sm font-medium text-gray-900">
                    {clusterStatus.configuration.model}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Namespace</span>
                  <span className="text-sm font-medium text-gray-900">
                    {clusterStatus.configuration.namespace}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Max Replicas</span>
                  <span className="text-sm font-medium text-gray-900">
                    {clusterStatus.configuration.max_replicas}
                  </span>
                </div>
              </>
            )}
          </div>
        </motion.div>

        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          className="card"
        >
          <h3 className="text-lg font-medium text-gray-900">Quick Actions</h3>
          <p className="text-sm text-gray-500">Common Kubernetes operations</p>
          
          <div className="mt-4 space-y-3">
            <button className="w-full btn btn-primary text-left">
              <ServerIcon className="h-5 w-5 mr-2" />
              Create Deployment
            </button>
            <button className="w-full btn btn-secondary text-left">
              <CloudIcon className="h-5 w-5 mr-2" />
              Create Service
            </button>
            <button className="w-full btn btn-secondary text-left">
              <ChartBarIcon className="h-5 w-5 mr-2" />
              View Resources
            </button>
          </div>
        </motion.div>
      </div>

      {/* Recent Activity */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="card"
      >
        <h3 className="text-lg font-medium text-gray-900">Recent Activity</h3>
        <p className="text-sm text-gray-500">Latest operations and events</p>
        
        <div className="mt-4">
          <div className="flex items-center space-x-3 py-3 border-b border-gray-200">
            <ClockIcon className="h-5 w-5 text-gray-400" />
            <div className="flex-1">
              <p className="text-sm text-gray-900">AI Agent initialized</p>
              <p className="text-xs text-gray-500">Just now</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3 py-3 border-b border-gray-200">
            <CheckCircleIcon className="h-5 w-5 text-success-500" />
            <div className="flex-1">
              <p className="text-sm text-gray-900">Cluster connection established</p>
              <p className="text-xs text-gray-500">Just now</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3 py-3">
            <ServerIcon className="h-5 w-5 text-blue-500" />
            <div className="flex-1">
              <p className="text-sm text-gray-900">Ready for Kubernetes operations</p>
              <p className="text-xs text-gray-500">Just now</p>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  )
}