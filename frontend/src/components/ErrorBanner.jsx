// Inline error message. Renders nothing when there is no message.
export default function ErrorBanner({ message }) {
  if (!message) return null
  return <div className="error" role="alert">{message}</div>
}
