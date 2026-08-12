// A labeled text input or textarea. Presentation only.
export default function Field({ id, label, value, onChange, type = 'text', textarea = false, error, ...rest }) {
  return (
    <div className="field">
      <label className="label" htmlFor={id}>{label}</label>
      {textarea ? (
        <textarea id={id} className="textarea" value={value}
                  onChange={(e) => onChange(e.target.value)} aria-describedby={error ? `${id}-error` : undefined} {...rest} />
      ) : (
        <input id={id} className="input" type={type} value={value}
               onChange={(e) => onChange(e.target.value)} aria-describedby={error ? `${id}-error` : undefined} {...rest} />
      )}
      {error && <p id={`${id}-error`} className="field-error">{error}</p>}
    </div>
  )
}
