// A button with a visual variant. Presentation only.
export default function Button({ variant = 'primary', children, ...rest }) {
  return (
    <button className={`btn btn--${variant}`} {...rest}>
      {children}
    </button>
  )
}
