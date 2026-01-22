import React, { useState } from 'react'
import './App.css'

function App() {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [showRawData, setShowRawData] = useState(false)

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      setFile(selectedFile)
      setResult(null)
      setError(null)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file) {
      setError('Please select an image file')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    const formData = new FormData()
    formData.append('image', file)

    try {
      const response = await fetch('/api/process-receipt', {
        method: 'POST',
        body: formData,
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to process receipt')
      }

      setResult(data)
    } catch (err) {
      setError(err.message || 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <div className="container">
        <h1>🧾 Receipt Tracker</h1>
        <p className="subtitle">Upload a receipt image to extract and parse data</p>

        <form onSubmit={handleSubmit} className="upload-form">
          <div className="file-input-wrapper">
            <input
              type="file"
              id="file-input"
              accept="image/*"
              onChange={handleFileChange}
              disabled={loading}
            />
            <label htmlFor="file-input" className="file-label">
              {file ? file.name : 'Choose Receipt Image'}
            </label>
          </div>

          <button type="submit" disabled={loading || !file} className="submit-btn">
            {loading ? 'Processing...' : 'Process Receipt'}
          </button>
        </form>

        {error && (
          <div className="error-message">
            <strong>Error:</strong> {error}
          </div>
        )}

        {result && (
          <div className="results">
            <div className="results-header">
              <h2>Results</h2>
              <button
                onClick={() => setShowRawData(!showRawData)}
                className="toggle-btn"
              >
                {showRawData ? 'Hide' : 'Show'} Raw Data
              </button>
            </div>

            {showRawData && (
              <div className="raw-data-section">
                <h3>OCR Extracted Text</h3>
                <pre className="raw-text">{result.ocr_text}</pre>

                <h3>LLM Response (Raw JSON)</h3>
                <pre className="raw-json">
                  {JSON.stringify(result.parsed_data, null, 2)}
                </pre>
              </div>
            )}

            <div className="parsed-data">
              <h3>Parsed Receipt Data</h3>
              <div className="data-grid">
                <div className="data-item">
                  <label>Merchant:</label>
                  <span>{result.parsed_data.merchant || 'N/A'}</span>
                </div>
                <div className="data-item">
                  <label>Date:</label>
                  <span>{result.parsed_data.date || 'N/A'}</span>
                </div>
                <div className="data-item">
                  <label>Total:</label>
                  <span className="amount">
                    {result.parsed_data.total !== null && result.parsed_data.total !== undefined
                      ? `€${result.parsed_data.total.toFixed(2)}`
                      : 'N/A'}
                  </span>
                </div>
                <div className="data-item">
                  <label>VAT:</label>
                  <span className="amount">
                    {result.parsed_data.vat !== null && result.parsed_data.vat !== undefined
                      ? `€${result.parsed_data.vat.toFixed(2)}`
                      : 'N/A'}
                  </span>
                </div>
                {result.parsed_data.fuel_type && (
                  <div className="data-item">
                    <label>Fuel Type:</label>
                    <span>{result.parsed_data.fuel_type}</span>
                  </div>
                )}
                {result.parsed_data.liters && (
                  <div className="data-item">
                    <label>Liters:</label>
                    <span>{result.parsed_data.liters} L</span>
                  </div>
                )}
                {result.parsed_data.price_per_liter && (
                  <div className="data-item">
                    <label>Price/Liter:</label>
                    <span>€{result.parsed_data.price_per_liter.toFixed(3)}</span>
                  </div>
                )}
              </div>

              {result.station_info && (
                <div className="station-info">
                  <h4>📍 Station Location</h4>
                  <div className="station-details">
                    <p><strong>Name:</strong> {result.station_info.name}</p>
                    <p><strong>Address:</strong> {result.station_info.address}</p>
                    <p><strong>Brand:</strong> {result.station_info.brand}</p>
                    {result.station_info.google_fuel_price_data && (
                      <div style={{marginTop: '15px', padding: '10px', background: '#f0f9ff', borderRadius: '5px'}}>
                        <strong>Google Fuel Prices:</strong>
                        <pre style={{marginTop: '5px', fontSize: '0.9em', overflow: 'auto'}}>
                          {JSON.stringify(result.station_info.google_fuel_price_data, null, 2)}
                        </pre>
                      </div>
                    )}
                    {result.station_info.price_from_receipt && (
                      <p>
                        <strong>Price from Receipt:</strong>{' '}
                        <span className="price-highlight">
                          €{result.station_info.price_from_receipt.toFixed(3)}/L
                        </span>
                        {!result.station_info.google_fuel_price_data && (
                          <small style={{display: 'block', color: '#666', marginTop: '5px'}}>
                            (Google Places API doesn't provide fuel prices)
                          </small>
                        )}
                      </p>
                    )}
                    {result.station_info.place_id && (
                      <p>
                        <a
                          href={`https://www.google.com/maps/place/?q=place_id:${result.station_info.place_id}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="maps-link"
                        >
                          🗺️ View on Google Maps
                        </a>
                      </p>
                    )}
                  </div>
                </div>
              )}

              {result.parsed_data.items && result.parsed_data.items.length > 0 && (
                <div className="items-section">
                  <h4>Items</h4>
                  <ul className="items-list">
                    {result.parsed_data.items.map((item, index) => (
                      <li key={index} className="item">
                        <span className="item-name">{item.name}</span>
                        <span className="item-price">
                          €{item.price?.toFixed(2) || '0.00'}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
