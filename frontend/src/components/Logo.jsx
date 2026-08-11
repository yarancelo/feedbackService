import { useState } from 'react'

export default function Logo() {
  const [loaded, setLoaded] = useState(false)
  return <div className="brand"><div className="brand__logo-wrap">{!loaded && <div className="brand__logo-slot">ЛОГОТИП<br/>PNG</div>}<img className={loaded ? 'brand__logo-file is-loaded' : 'brand__logo-file'} src="/logo.png" alt="Логотип компании" onLoad={() => setLoaded(true)} onError={(event) => { event.currentTarget.style.display = 'none' }} /></div></div>
}
