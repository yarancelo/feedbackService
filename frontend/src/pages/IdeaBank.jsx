import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ideaBank, reactToIdea } from '../api/ideas.js'
import ErrorBanner from '../components/ErrorBanner.jsx'
import IdeaDialog from '../components/IdeaDialog.jsx'
import Logo from '../components/Logo.jsx'

const preview = (text) => text.length > 160 ? `${text.slice(0, 160).trim()}...` : text
export default function IdeaBank() {
  const [data, setData] = useState({ weeks: [] }); const [selected, setSelected] = useState(null); const [error, setError] = useState(''); const [loading, setLoading] = useState(true)
  async function load() { setLoading(true); try { setData(await ideaBank()) } catch (requestError) { setError(requestError.message) } finally { setLoading(false) } }
  useEffect(() => { load() }, [])
  async function react(item, value) { try { const updated = await reactToIdea(item.id, value); setData((current) => ({ weeks: current.weeks.map((week) => ({ ...week, ideas: week.ideas.map((entry) => entry.id === updated.id ? updated : entry) })) })); setSelected((current) => current?.id === updated.id ? updated : current) } catch (requestError) { setError(requestError.message) } }
  return <div className="wrap"><main className="wall-page"><header className="wall-page__head"><div className="page-top"><Logo /><Link className="account-link" to="/admin" aria-label="Личный кабинет">ЛК</Link></div><div className="wall-page__intro"><h1 className="compose__title">Банк идей</h1><p className="compose__lede">В этом разделе собраны предложения, отмеченные руководством компании и принятые в работу.</p></div><nav className="wall-page__actions" aria-label="Разделы"><Link className="btn btn--ghost" to="/">Стена</Link><Link className="btn btn--primary" to="/submit">Добавить предложение</Link></nav></header><ErrorBanner message={error} />{loading ? <p className="wall-state">Загружаем банк...</p> : !data.weeks.length ? <div className="empty"><p className="empty__title">Банк пока пуст</p><p>Добавьте золотой статус принятому предложению в личном кабинете.</p></div> : <div className="bank-weeks">{data.weeks.map((week) => <section className="bank-week" key={week.week}><header><p className="eyebrow">Неделя {week.week}</p><h2>{week.title}</h2><p>Отмеченные авторы: {week.winner_names.join(', ')}</p></header><div className="idea-grid">{week.ideas.map((idea) => <article className="idea-card" key={idea.id}><div className="idea-card__meta">{idea.category && <span className="idea-card__category">{idea.category}</span>}<span className="gold-badge">Золотой статус</span></div><h3>{idea.topic || 'Без заголовка'}</h3><p>{preview(idea.body)}</p><footer><span>{idea.author_name || 'Анонимно'}</span></footer><button type="button" className="idea-card__more" onClick={() => setSelected(idea)}>Открыть</button></article>)}</div></section>)}</div>}<IdeaDialog idea={selected} onClose={() => setSelected(null)} onReact={react} /></main></div>
}
