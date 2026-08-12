import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { listWall, reactToIdea } from '../api/ideas.js'
import Button from '../components/Button.jsx'
import ErrorBanner from '../components/ErrorBanner.jsx'
import IdeaDialog from '../components/IdeaDialog.jsx'

const preview = (text) => text.length > 190 ? `${text.slice(0, 190).trim()}…` : text

export default function Wall() {
  const [page, setPage] = useState(1)
  const [data, setData] = useState({ items: [], total_pages: 0 })
  const [selected, setSelected] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  async function load() {
    setLoading(true); setError('')
    try { setData(await listWall(page)) } catch (requestError) { setError(requestError.message) } finally { setLoading(false) }
  }
  useEffect(() => { load() }, [page])

  async function react(idea, value) {
    try {
      const updated = await reactToIdea(idea.id, value)
      setData((current) => ({ ...current, items: current.items.map((item) => item.id === updated.id ? updated : item) }))
      setSelected((current) => current?.id === updated.id ? updated : current)
    } catch (requestError) { setError(requestError.message) }
  }

  return <div className="wrap"><main className="wall-page">
    <header className="wall-page__head"><div><p className="eyebrow">Есть идея, как сделать лучше?</p><h1 className="compose__title">Стена идей</h1><p className="compose__lede">Делитесь идеями, которые делают работу проще, сервис лучше, а компанию сильнее.</p></div><div className="wall-page__actions"><Link className="btn btn--primary" to="/submit?type=idea">＋ Предложить идею</Link><Link className="btn btn--ghost" to="/submit?type=feedback">Оставить отзыв</Link></div></header>
    <section className="reward"><strong>5 000 ₽ автору идеи недели</strong><span>В зачёт попадают принятые идеи с указанным автором: полезные, понятные и не повторяющие уже предложенные.</span></section>
    <ErrorBanner message={error} />
    {loading ? <p className="wall-state">Загружаем идеи…</p> : !data.items.length ? <div className="empty"><p className="empty__title">Здесь пока нет идей</p><p>Предложите первую.</p><Link className="btn btn--primary" to="/submit?type=idea">Предложить идею</Link></div> : <div className="idea-grid">{data.items.map((idea) => <article className="idea-card" key={idea.id}>
      <div className="idea-card__meta"><span className={idea.status === 'accepted' ? 'status status--accepted' : 'status'}>{idea.status === 'accepted' ? 'Принята' : 'На рассмотрении'}</span>{idea.category && <span className="idea-card__category">{idea.category}</span>}</div>
      <h2>{idea.topic || 'Без названия'}</h2><p>{preview(idea.body)}</p>
      <footer><span>{idea.author_name ? `${idea.author_name}${idea.author_department ? ` · ${idea.author_department}` : ''}` : 'Анонимно'}</span><div className="reaction-row"><button className={idea.viewer_reaction === 1 ? 'reaction is-active' : 'reaction'} onClick={() => react(idea, idea.viewer_reaction === 1 ? 0 : 1)}>👍 {idea.likes}</button><button className={idea.viewer_reaction === -1 ? 'reaction is-active' : 'reaction'} onClick={() => react(idea, idea.viewer_reaction === -1 ? 0 : -1)}>👎 {idea.dislikes}</button></div></footer>
      <button type="button" className="idea-card__more" onClick={() => setSelected(idea)}>Подробнее</button>
    </article>)}</div>}
    {data.total_pages > 1 && <div className="pager"><Button variant="ghost" disabled={page === 1} onClick={() => setPage((current) => current - 1)}>← Назад</Button><span className="pager__label">{page} из {data.total_pages}</span><Button variant="ghost" disabled={page === data.total_pages} onClick={() => setPage((current) => current + 1)}>Вперёд →</Button></div>}
    <IdeaDialog idea={selected} onClose={() => setSelected(null)} onReact={react} />
  </main></div>
}
