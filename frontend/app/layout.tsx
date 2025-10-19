import './globals.css'
import { Inter } from 'next/font/google'
import { Toaster } from 'react-hot-toast'
import { WebSocketProvider } from '@/contexts/WebSocketContext'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'Kubernetes AI Agent',
  description: 'AI-powered Kubernetes management with LangChain and Google Gemini',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <WebSocketProvider>
          <div className="min-h-screen bg-gray-50">
            {children}
          </div>
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#363636',
                color: '#fff',
              },
            }}
          />
        </WebSocketProvider>
      </body>
    </html>
  )
}