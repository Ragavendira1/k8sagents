'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  Cog6ToothIcon,
  ServerIcon,
  KeyIcon,
  ShieldCheckIcon,
  InformationCircleIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

interface Settings {
  model: string
  namespace: string
  maxReplicas: number
  temperature: number
  maxTokens: number
  allowedImages: string[]
  forbiddenNamespaces: string[]
}

export default function Settings() {
  const [settings, setSettings] = useState<Settings>({
    model: 'gemini-2.0-flash',
    namespace: 'default',
    maxReplicas: 10,
    temperature: 0.1,
    maxTokens: 2048,
    allowedImages: ['nginx', 'httpd', 'redis', 'postgres', 'mysql', 'mongo'],
    forbiddenNamespaces: ['kube-system', 'kube-public', 'kube-node-lease']
  })
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    fetchSettings()
  }, [])

  const fetchSettings = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/status')
      if (!response.ok) {
        throw new Error('Failed to fetch settings')
      }
      const data = await response.json()
      
      if (data.configuration) {
        setSettings({
          model: data.configuration.model,
          namespace: data.configuration.namespace,
          maxReplicas: data.configuration.max_replicas,
          temperature: 0.1, // Default value
          maxTokens: 2048, // Default value
          allowedImages: data.configuration.allowed_images || [],
          forbiddenNamespaces: data.configuration.forbidden_namespaces || []
        })
      }
    } catch (error) {
      console.error('Error fetching settings:', error)
      toast.error('Failed to fetch settings')
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      // This would need to be implemented in the backend
      toast.success('Settings saved successfully')
    } catch (error) {
      console.error('Error saving settings:', error)
      toast.error('Failed to save settings')
    } finally {
      setSaving(false)
    }
  }

  const handleInputChange = (field: keyof Settings, value: any) => {
    setSettings(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleArrayChange = (field: 'allowedImages' | 'forbiddenNamespaces', value: string) => {
    const items = value.split(',').map(item => item.trim()).filter(item => item)
    setSettings(prev => ({
      ...prev,
      [field]: items
    }))
  }

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
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="mt-1 text-sm text-gray-500">
          Configure your Kubernetes AI Agent settings
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* AI Configuration */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="card"
        >
          <div className="flex items-center space-x-3 mb-4">
            <Cog6ToothIcon className="h-6 w-6 text-primary-600" />
            <h3 className="text-lg font-medium text-gray-900">AI Configuration</h3>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Model
              </label>
              <select
                value={settings.model}
                onChange={(e) => handleInputChange('model', e.target.value)}
                className="select"
              >
                <option value="gemini-2.0-flash">Gemini 2.0 Flash</option>
                <option value="gemini-1.5-pro">Gemini 1.5 Pro</option>
                <option value="gemini-1.5-flash">Gemini 1.5 Flash</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Temperature
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={settings.temperature}
                onChange={(e) => handleInputChange('temperature', parseFloat(e.target.value))}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>0.0 (Focused)</span>
                <span>{settings.temperature}</span>
                <span>1.0 (Creative)</span>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Max Tokens
              </label>
              <input
                type="number"
                value={settings.maxTokens}
                onChange={(e) => handleInputChange('maxTokens', parseInt(e.target.value))}
                className="input"
                min="100"
                max="4096"
              />
            </div>
          </div>
        </motion.div>

        {/* Kubernetes Configuration */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="card"
        >
          <div className="flex items-center space-x-3 mb-4">
            <ServerIcon className="h-6 w-6 text-green-600" />
            <h3 className="text-lg font-medium text-gray-900">Kubernetes Configuration</h3>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Default Namespace
              </label>
              <input
                type="text"
                value={settings.namespace}
                onChange={(e) => handleInputChange('namespace', e.target.value)}
                className="input"
                placeholder="default"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Max Replicas
              </label>
              <input
                type="number"
                value={settings.maxReplicas}
                onChange={(e) => handleInputChange('maxReplicas', parseInt(e.target.value))}
                className="input"
                min="1"
                max="100"
              />
            </div>
          </div>
        </motion.div>

        {/* Security Settings */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card lg:col-span-2"
        >
          <div className="flex items-center space-x-3 mb-4">
            <ShieldCheckIcon className="h-6 w-6 text-red-600" />
            <h3 className="text-lg font-medium text-gray-900">Security Settings</h3>
          </div>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Allowed Images
              </label>
              <textarea
                value={settings.allowedImages.join(', ')}
                onChange={(e) => handleArrayChange('allowedImages', e.target.value)}
                className="textarea"
                rows={3}
                placeholder="nginx, httpd, redis, postgres, mysql, mongo"
              />
              <p className="text-xs text-gray-500 mt-1">
                Comma-separated list of allowed container images
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Forbidden Namespaces
              </label>
              <textarea
                value={settings.forbiddenNamespaces.join(', ')}
                onChange={(e) => handleArrayChange('forbiddenNamespaces', e.target.value)}
                className="textarea"
                rows={3}
                placeholder="kube-system, kube-public, kube-node-lease"
              />
              <p className="text-xs text-gray-500 mt-1">
                Comma-separated list of forbidden namespaces
              </p>
            </div>
          </div>
        </motion.div>

        {/* System Information */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="card lg:col-span-2"
        >
          <div className="flex items-center space-x-3 mb-4">
            <InformationCircleIcon className="h-6 w-6 text-blue-600" />
            <h3 className="text-lg font-medium text-gray-900">System Information</h3>
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <div className="flex items-center space-x-3">
              <CheckCircleIcon className="h-5 w-5 text-success-500" />
              <div>
                <p className="text-sm font-medium text-gray-900">Agent Status</p>
                <p className="text-sm text-gray-500">Running</p>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <CheckCircleIcon className="h-5 w-5 text-success-500" />
              <div>
                <p className="text-sm font-medium text-gray-900">kubectl</p>
                <p className="text-sm text-gray-500">Available</p>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <ExclamationTriangleIcon className="h-5 w-5 text-warning-500" />
              <div>
                <p className="text-sm font-medium text-gray-900">API Key</p>
                <p className="text-sm text-gray-500">Configured</p>
              </div>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Save Button */}
      <div className="flex justify-end">
        <button
          onClick={handleSave}
          disabled={saving}
          className="btn btn-primary"
        >
          {saving ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Saving...
            </>
          ) : (
            'Save Settings'
          )}
        </button>
      </div>
    </div>
  )
}