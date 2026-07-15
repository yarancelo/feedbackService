// A labeled text input or textarea. Presentation only.
export default function Field({ id, label, value, onChange, type = 'text', textarea = false, ...rest }) {
  return (
    <div className="field">
      <label className="label" htmlFor={id}>{label}</label>
      {textarea ? (
        <textarea id={id} className="textarea" value={value}
                  onChange={(e) => onChange(e.target.value)} {...rest} />
      ) : (
        <input id={id} className="input" type={type} value={value}
               onChange={(e) => onChange(e.target.value)} {...rest} />
      )}
    </div>
  )
}
