'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  ServerIcon,
  CloudIcon,
  CpuChipIcon,
  CircleStackIcon,
  EyeIcon,
  TrashIcon,
  ArrowPathIcon,
  PlusIcon
} from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

interface Resource {
  name: string
  namespace: string
  age: string
  status: string
}

interface ResourceType {
  id: string
  name: string
  icon: React.ComponentType<{ className?: string }>
  color: string
  bgColor: string
}

const resourceTypes: ResourceType[] = [
  {
    id: 'deployments',
    name: 'Deployments',
    icon: ServerIcon,
    color: 'text-blue-600',
    bgColor: 'bg-blue-100'
  },
  {
    id: 'services',
    name: 'Services',
    icon: CloudIcon,
    color: 'text-green-600',
    bgColor: 'bg-green-100'
  },
  {
    id: 'pods',
    name: 'Pods',
    icon: CpuChipIcon,
    color: 'text-purple-600',
    bgColor: 'bg-purple-100'
  },
  {
    id: 'namespaces',
    name: 'Namespaces',
    icon: CircleStackIcon,
    color: 'text-orange-600',
    bgColor: 'bg-orange-100'
  }
]

export default function Resources() {
  const [selectedType, setSelectedType] = useState('deployments')
  const [resources, setResources] = useState<Resource[]>([])
  const [loading, setLoading] = useState(false)
  const [refreshing, setRefreshing] = useState(false)

  useEffect(() => {
    fetchResources(selectedType)
  }, [selectedType])

  const fetchResources = async (type: string) => {
    setLoading(true)
    try {
      const response = await fetch(`/api/resources/${type}`)
      if (!response.ok) {
        throw new Error('Failed to fetch resources')
      }
      const data = await response.json()
      setResources(data.resources || [])
    } catch (error) {
      console.error('Error fetching resources:', error)
      toast.error('Failed to fetch resources')
    } finally {
      setLoading(false)
    }
  }

  const handleRefresh = async () => {
    setRefreshing(true)
    await fetchResources(selectedType)
    setRefreshing(false)
    toast.success('Resources refreshed')
  }

  const handleDelete = async (name: string, type: string) => {
    if (!confirm(`Are you sure you want to delete ${type} "${name}"?`)) {
      return
    }

    try {
      // This would need to be implemented in the backend
      toast.error('Delete functionality not implemented yet')
    } catch (error) {
      console.error('Error deleting resource:', error)
      toast.error('Failed to delete resource')
    }
  }

  const selectedResourceType = resourceTypes.find(rt => rt.id === selectedType)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Resources</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage your Kubernetes resources
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="btn btn-secondary"
          >
            <ArrowPathIcon className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          <button className="btn btn-primary">
            <PlusIcon className="h-4 w-4 mr-2" />
            Create
          </button>
        </div>
      </div>

      {/* Resource Type Tabs */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {resourceTypes.map((type, index) => (
          <motion.button
            key={type.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            onClick={() => setSelectedType(type.id)}
            className={`p-4 rounded-lg border-2 transition-all duration-200 ${
              selectedType === type.id
                ? 'border-primary-500 bg-primary-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center space-x-3">
              <div className={`p-2 rounded-md ${type.bgColor}`}>
                <type.icon className={`h-6 w-6 ${type.color}`} />
              </div>
              <div className="text-left">
                <p className={`font-medium ${
                  selectedType === type.id ? 'text-primary-900' : 'text-gray-900'
                }`}>
                  {type.name}
                </p>
                <p className="text-sm text-gray-500">
                  {resources.length} items
                </p>
              </div>
            </div>
          </motion.button>
        ))}
      </div>

      {/* Resources Table */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">
            {selectedResourceType?.name} ({resources.length})
          </h3>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        ) : resources.length === 0 ? (
          <div className="text-center py-12">
            <selectedResourceType?.icon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No {selectedResourceType?.name.toLowerCase()}</h3>
            <p className="text-gray-500 mb-4">
              No {selectedResourceType?.name.toLowerCase()} found in the cluster.
            </p>
            <button className="btn btn-primary">
              <PlusIcon className="h-4 w-4 mr-2" />
              Create {selectedResourceType?.name.slice(0, -1)}
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Namespace
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Age
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {resources.map((resource, index) => (
                  <motion.tr
                    key={resource.name}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="hover:bg-gray-50"
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className={`flex-shrink-0 p-1 rounded ${selectedResourceType?.bgColor}`}>
                          <selectedResourceType?.icon className={`h-4 w-4 ${selectedResourceType?.color}`} />
                        </div>
                        <div className="ml-3">
                          <div className="text-sm font-medium text-gray-900">
                            {resource.name}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {resource.namespace}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {resource.age}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        resource.status === 'Running' || resource.status === 'Active'
                          ? 'bg-success-100 text-success-800'
                          : resource.status === 'Pending'
                          ? 'bg-warning-100 text-warning-800'
                          : 'bg-error-100 text-error-800'
                      }`}>
                        {resource.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center justify-end space-x-2">
                        <button
                          onClick={() => {/* View details */}}
                          className="text-primary-600 hover:text-primary-900"
                        >
                          <EyeIcon className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(resource.name, selectedType)}
                          className="text-error-600 hover:text-error-900"
                        >
                          <TrashIcon className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}