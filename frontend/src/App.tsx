import React, { useState } from 'react'

export default function App() {
  const [prompt, setPrompt] = useState("")
  const [namespace, setNamespace] = useState("")
  const [resp, setResp] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const ask = async () => {
    setLoading(true)
    const r = await fetch('/api/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt, namespace: namespace || undefined })
    })
    const j = await r.json()
    setResp(j)
    setLoading(false)
  }

  return (
    <div style={{ maxWidth: 900, margin: '40px auto', fontFamily: 'Inter, system-ui' }}>
      <h1>k8s-assistant</h1>
      <p>Ask in natural language. Example: <code>show pods in operations</code> or <code>logs of api-gateway in prod</code></p>
      <div style={{ display: 'flex', gap: 8 }}>
        <input style={{ flex: 1, padding: 8 }} value={prompt} onChange={e=>setPrompt(e.target.value)} placeholder="Your question" />
        <input style={{ width: 200, padding: 8 }} value={namespace} onChange={e=>setNamespace(e.target.value)} placeholder="Namespace (optional)" />
        <button onClick={ask} disabled={loading}>{loading?'Asking...':'Ask'}</button>
      </div>
      {resp && (
        <div style={{ marginTop: 20 }}>
          <h3>Intent</h3>
          <pre>{JSON.stringify(resp.intent, null, 2)}</pre>
          <h3>Result</h3>
          <pre>{JSON.stringify(resp.result, null, 2)}</pre>
        </div>
      )}
    </div>
  )
}