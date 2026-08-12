import { useState } from 'react'
import { Link } from 'react-router-dom'

export default function Logo() {
  const [loaded, setLoaded] = useState(false)
  return <Link className="brand" to="/" aria-label="Перейти на главную"><div className="brand__logo-wrap">{!loaded && <div className="brand__logo-slot">ЛОГО<br />PNG</div>}<img className={loaded ? 'brand__logo-file is-loaded' : 'brand__logo-file'} src="/logo.png" alt="Логотип компании" onLoad={() => setLoaded(true)} onError={(event) => { event.currentTarget.style.display = 'none' }} /></div></Link>
}
