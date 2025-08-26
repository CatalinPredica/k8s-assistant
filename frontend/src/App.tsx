import React, { useState } from 'react'

export default function App() {
  const [prompt, setPrompt] = useState("")
  const [resp, setResp] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const ask = async () => {
    setLoading(true)
    const r = await fetch('/api/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt })
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
        <input 
          style={{ flex: 1, padding: 8 }} 
          value={prompt} 
          onChange={e=>setPrompt(e.target.value)} 
          onKeyDown={e => e.key === 'Enter' && !loading && ask()}
          placeholder="Your question" 
        />
        <button onClick={ask} disabled={loading}>{loading?'Asking...':'Ask'}</button>
      </div>
      {resp && (
        <div style={{ marginTop: 20 }}>
          <div style={{ 
            background: '#f8f9fa', 
            padding: '20px', 
            borderRadius: '8px', 
            border: '1px solid #e9ecef',
            marginBottom: '20px'
          }}>
            <h3 style={{ margin: '0 0 15px 0', color: '#495057' }}>
              Command Intent
            </h3>
            <div style={{ 
              background: 'white', 
              padding: '15px', 
              borderRadius: '6px', 
              border: '1px solid #dee2e6',
              fontFamily: 'monospace',
              fontSize: '14px'
            }}>
              <div><strong>Action:</strong> <span style={{ color: '#007bff' }}>{resp.intent.action}</span></div>
              <div><strong>Resource:</strong> <span style={{ color: '#28a745' }}>{resp.intent.resource}</span></div>
              {resp.intent.namespace && (
                <div><strong>Namespace:</strong> <span style={{ color: '#6f42c1' }}>{resp.intent.namespace}</span></div>
              )}
            </div>
          </div>
          
          <div style={{
            background: '#f8f9fa',
            padding: '20px',
            borderRadius: '8px',
            border: '1px solid #e9ecef',
            marginBottom: '20px'
          }}>
            <h3 style={{ margin: '0 0 15px 0', color: '#495057' }}>
              Gemini Raw Response
            </h3>
            <div style={{
              background: 'white',
              padding: '15px',
              borderRadius: '6px',
              border: '1px solid #dee2e6',
              fontFamily: 'monospace',
              fontSize: '14px',
              whiteSpace: 'pre-wrap'
            }}>
              {JSON.stringify(resp.intent, null, 2)}
            </div>
          </div>

          <div style={{ 
            background: '#f8f9fa', 
            padding: '20px', 
            borderRadius: '8px', 
            border: '1px solid #e9ecef'
          }}>
            <h3 style={{ margin: '0 0 15px 0', color: '#495057' }}>
              Results
            </h3>
            {resp.result.error ? (
              <div style={{ 
                background: '#f8d7da', 
                color: '#721c24', 
                padding: '15px', 
                borderRadius: '6px', 
                border: '1px solid #f5c6cb'
              }}>
                <strong>Error:</strong> {resp.result.error}
              </div>
            ) : resp.result.items ? (
              <div>
                <div style={{ 
                  background: 'white', 
                  padding: '15px', 
                  borderRadius: '6px', 
                  border: '1px solid #dee2e6'
                }}>
                  <div style={{ marginBottom: '10px', fontWeight: 'bold', color: '#495057' }}>
                    {resp.result.all_namespaces ? (
                      <>Found {resp.result.items.length} {resp.intent.resource} across all namespaces:</>
                    ) : (
                      <>Found {resp.result.items.length} {resp.intent.resource} in {resp.result.namespace || 'default'} namespace:</>
                    )}
                  </div>
                  <div style={{ display: 'grid', gap: '8px' }}>
                    {resp.result.items.map((item: string, index: number) => {
                      // Extract pod name and status if available
                      let displayName = item;
                      let status = "";
                      if (item.includes(" (")) {
                        const parts = item.split(" (");
                        displayName = parts[0];
                        status = parts[1].replace(")", "");
                      }

                      const hasNamespace = displayName.includes('/');

                      // Color coding for status
                      let statusColor = '#6c757d'; // default grey
                      if (status === 'Running') statusColor = '#28a745';
                      else if (status === 'Pending') statusColor = '#ffc107';
                      else if (status === 'CrashLoopBackOff' || status === 'Failed') statusColor = '#dc3545';

                      return (
                        <div key={index} style={{
                          background: hasNamespace ? '#e3f2fd' : '#e9ecef',
                          padding: '8px 12px',
                          borderRadius: '4px',
                          fontFamily: 'monospace',
                          fontSize: '13px',
                          color: hasNamespace ? '#1565c0' : '#495057',
                          border: hasNamespace ? '1px solid #bbdefb' : 'none',
                          display: 'flex',
                          justifyContent: 'space-between'
                        }}>
                          <span>{displayName}</span>
                          {status && <span style={{ color: statusColor }}>{status}</span>}
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            ) : resp.result.log ? (
              <div style={{ 
                background: 'white', 
                padding: '15px', 
                borderRadius: '6px', 
                border: '1px solid #dee2e6',
                fontFamily: 'monospace',
                fontSize: '12px',
                whiteSpace: 'pre-wrap',
                maxHeight: '400px',
                overflow: 'auto'
              }}>
                {resp.result.log}
              </div>
            ) : (
              <div style={{ 
                background: 'white', 
                padding: '15px', 
                borderRadius: '6px', 
                border: '1px solid #dee2e6',
                fontFamily: 'monospace',
                fontSize: '14px'
              }}>
                {JSON.stringify(resp.result, null, 2)}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}