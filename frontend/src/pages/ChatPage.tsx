import { useParams } from 'react-router-dom'

export default function ChatPage() {
  const { id } = useParams()
  return (
    <div className="flex items-center justify-center h-64">
      <h2 className="text-2xl font-semibold text-gray-400">Chat — match {id} — coming soon</h2>
    </div>
  )
}
