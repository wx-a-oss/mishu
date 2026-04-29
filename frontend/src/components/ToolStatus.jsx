import './ToolStatus.css'

export default function ToolStatus({ status }) {
  return (
    <div className="tool-status">
      <span className="tool-spinner" />
      <span className="tool-text">
        Running: <strong>{status.name}</strong>
        {status.args && Object.keys(status.args).length > 0 && (
          <span className="tool-args">
            ({Object.entries(status.args).map(([k, v]) => `${k}: ${JSON.stringify(v)}`).join(', ')})
          </span>
        )}
      </span>
    </div>
  )
}
